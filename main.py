import RPi.GPIO as GPIO
import time
from threading import Timer
from carro import piscar_seta, farol_baixo, farol_alto, desligar_painel,detect_farol, detect_rpm_and_velocity, motor_pulse_callback, wheel_pulse_callback, detect_temperature
from led import write_to_led
# OUT PINS
MOTOR_DIR1 = 17
MOTOR_DIR2 = 18
MOTOR_POT = 23 # PWM
FREIO_POT = 24 # PWM
LUZ_FREIO = 25
SETA_ESQ = 8
SETA_DIR = 7
FAROL_ALTO = 26
FAROL_BAIXO = 19
LUZ_TEMP = 12

# IN PINS
FREIO_PIN = 22 
ACELERADOR_PIN = 27
MOTOR_HALL_PIN = 11  # Substitua pelo número do GPIO do sensor do motor
WHEEL_HALL_A_PIN = 5  # Substitua pelo número do GPIO do canal A da roda
WHEEL_HALL_B_PIN = 6  # Substitua pelo número do GPIO do canal B da roda


# Inicialização do GPIO
def setup_gpio():
    global motor_pwm, freio_pwm
    GPIO.setmode(GPIO.BCM)  # Usar o esquema de numeração BCM
    GPIO.setwarnings(False)

    # Configuração dos pinos
    GPIO.setup(LUZ_FREIO, GPIO.OUT)
    GPIO.setup(MOTOR_DIR1, GPIO.OUT)
    GPIO.setup(MOTOR_DIR2, GPIO.OUT)
    GPIO.setup(SETA_DIR, GPIO.OUT)
    GPIO.setup(SETA_ESQ, GPIO.OUT)
    GPIO.setup(FAROL_ALTO, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(FAROL_BAIXO, GPIO.OUT)
    GPIO.setup(LUZ_TEMP, GPIO.OUT)

    GPIO.setup(MOTOR_HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(WHEEL_HALL_A_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(WHEEL_HALL_B_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.setup(MOTOR_POT, GPIO.OUT)
    motor_pwm = GPIO.PWM(MOTOR_POT, 1000)
    motor_pwm.start(0)

    GPIO.setup(FREIO_POT, GPIO.OUT)
    freio_pwm = GPIO.PWM(FREIO_POT, 1000)
    freio_pwm.start(0)

    GPIO.setup(FREIO_PIN, GPIO.IN)
    GPIO.setup(ACELERADOR_PIN, GPIO.IN)


def handle_freio(channel):
    if GPIO.input(channel):
        freiar_motor()
        GPIO.output(LUZ_FREIO, True)
        motor_pwm.ChangeDutyCycle(0)
        freio_pwm.ChangeDutyCycle(50)
    else:
        GPIO.output(LUZ_FREIO, False)
        freio_pwm.ChangeDutyCycle(0)

def handle_acelerar(channel):
    if GPIO.input(channel):
        andar_frente()
        motor_pwm.ChangeDutyCycle(100)
    else:
        motor_pwm.ChangeDutyCycle(0)

def andar_frente():
    GPIO.output(MOTOR_DIR1, 1)
    GPIO.output(MOTOR_DIR2, 0)

def freiar_motor():
    GPIO.output(MOTOR_DIR1, 1)
    GPIO.output(MOTOR_DIR2, 1)
    

# Loop principal de teste
if __name__ == "__main__":
    try:
        setup_gpio()
        GPIO.add_event_detect(FREIO_PIN, GPIO.BOTH, callback=handle_freio)
        GPIO.add_event_detect(ACELERADOR_PIN, GPIO.BOTH, callback=handle_acelerar)
        GPIO.add_event_detect(MOTOR_HALL_PIN, GPIO.RISING, callback=motor_pulse_callback)
        GPIO.add_event_detect(WHEEL_HALL_A_PIN, GPIO.RISING, callback=wheel_pulse_callback)
        print("Sistema inicializado.")
        while True:
            velocidade , rpm = detect_rpm_and_velocity()
            temperature = detect_temperature()
            detect_farol()
            write_to_led(velocidade, rpm, temperature)

    except KeyboardInterrupt:
        print("Encerrando...")
    finally:
        desligar_painel()
        GPIO.cleanup()
