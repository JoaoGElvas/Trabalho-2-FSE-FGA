import termios
import os
from time import sleep, time
from crc import calcula_CRC
import struct  # Para conversão dos bytes para float
import RPi.GPIO as GPIO
from bmp280 import BMP280
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

SETA_ESQ = 8
SETA_DIR = 7
FAROL_ALTO = 26
FAROL_BAIXO = 19
LUZ_TEMP = 12
WHEEL_HALL_A_PIN = 5  # Substitua pelo número do GPIO do canal A da roda
WHEEL_HALL_B_PIN = 6 


# Constantes
WHEEL_DIAMETER = 0.63  # Diâmetro externo da roda (metros)
WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * 3.14159  # Circunferência da roda (metros)
SECONDS_PER_MINUTE = 60
KM_PER_METER = 1 / 1000

# Variáveis globais
motor_pulse_count = 0
wheel_pulse_count = 0
direction = "forward"

# Temperatura
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)

uarto_filestream = os.open(
        "/dev/serial0", os.O_RDWR | os.O_NOCTTY | os.O_NDELAY)

# Pega valor das flags
[iflag, oflag, cflag, lflag] = [0, 1, 2, 3]

attrs = termios.tcgetattr(uarto_filestream)

attrs[cflag] = termios.B9600 | termios.CS8 | termios.CLOCAL | termios.CREAD
attrs[iflag] = termios.IGNPAR
attrs[oflag] = 0
attrs[lflag] = 0

termios.tcflush(uarto_filestream, termios.TCIFLUSH)
termios.tcsetattr(uarto_filestream, termios.TCSANOW, attrs)

def enviar_requisicao(uarto_filestream, requisicao):
    crc16 = calcula_CRC(requisicao)
    crc_bytes = struct.pack("<H", crc16)
    requisicao_com_crc = requisicao + crc_bytes
    os.write(uarto_filestream, requisicao_com_crc)
    sleep(1)
    return os.read(uarto_filestream, 255)

def processar_mensagem(mensagem, estado_registrador):
    if mensagem[2] == estado_registrador:
        return estado_registrador
    elif mensagem[2] == 0x02:
        return 0x02
    elif mensagem[2] == 0x01:
        return 0x01
    elif mensagem[2] == 0x00:
        return 0x00
    return estado_registrador

def seta_painel(is_ligado, direcao):
    endereco = 0x01
    codigo = 0x06
    sub_codigo = 0x0C if direcao == 'r' else 0x0B
    quantidade = [1]
    matricula = [9,5,9,9]
    matricula_bytes = bytes(matricula)
    quantidade_bytes = bytes(quantidade)
    dados = [is_ligado]
    dados_bytes = bytes(dados)
    requisicao = bytes([endereco, codigo, sub_codigo]) + quantidade_bytes + dados_bytes + matricula_bytes

    crc16 = calcula_CRC(requisicao)
    crc_bytes = struct.pack("<H", crc16)
    requisicao_com_crc = requisicao + crc_bytes
    os.write(uarto_filestream, requisicao_com_crc)

    sleep(0.1)
    leitura = os.read(uarto_filestream, 255)

def piscar_seta(direcao):
    
    if direcao == 'l':
        seta_painel(1, direcao)
        GPIO.output(SETA_DIR, False)
        GPIO.output(SETA_ESQ, True)
        
        sleep(1)
        seta_painel(0, direcao)
        GPIO.output(SETA_ESQ, False)
        sleep(1)
    elif direcao == 'r':
        seta_painel(1)

        GPIO.output(SETA_ESQ, False)
        GPIO.output(SETA_DIR, True)

        sleep(1)
        seta_painel(0, direcao)
        GPIO.output(SETA_DIR, False)
        sleep(1)
    else:
        print("Direção de Seta Invalida!")
    piscar_seta(direcao)

def farol_painel(is_ligado, altura):
    endereco = 0x01
    codigo = 0x06
    sub_codigo = 0x0D if altura == 'alto' else 0x0E
    quantidade = [1]
    matricula = [9,5,9,9]
    matricula_bytes = bytes(matricula)
    quantidade_bytes = bytes(quantidade)
    dados = [is_ligado]
    dados_bytes = bytes(dados)
    requisicao = bytes([endereco, codigo, sub_codigo]) + quantidade_bytes + dados_bytes + matricula_bytes

    crc16 = calcula_CRC(requisicao)
    crc_bytes = struct.pack("<H", crc16)
    requisicao_com_crc = requisicao + crc_bytes
    os.write(uarto_filestream, requisicao_com_crc)

    sleep(0.1)
    leitura = os.read(uarto_filestream, 255)

def farol_alto():
    farol_painel(0,'baixo')
    farol_painel(1,'alto')
    GPIO.output(FAROL_BAIXO, False)
    GPIO.output(FAROL_ALTO, True)

def farol_baixo():
    farol_painel(1,'baixo')
    farol_painel(0,'alto')
    GPIO.output(FAROL_BAIXO, True)
    GPIO.output(FAROL_ALTO, False)

def detect_farol():
    estado_registrador = 0x00
    requisicao = bytes([0x01, 0x03, 0x02, 1]) + bytes([5, 9, 9, 9])
    leitura = enviar_requisicao(uarto_filestream, requisicao)
    mensagem, crc_recebido = leitura[:-2], leitura[-2:]
    crc_calculado = struct.pack("<H", calcula_CRC(mensagem))

    if crc_recebido == crc_calculado:
        estado_registrador = processar_mensagem(mensagem, estado_registrador)

        if mensagem[0] == 0x00 and mensagem[1] == 0x03:
            if mensagem[2] == 0x02:
                print("Botão pressionado: Farol Alto")
                farol_alto()
            elif mensagem[2] == 0x01:
                print("Botão pressionado: Farol Baixo")
                farol_baixo()
            # elif mensagem[2] == 0x00:
            #     print("Botão pressionado: Farol Desligado")
            #     alternar_estado_farois()
            #     requisicao = bytes([0x01, 0x06, 0x0F, 1, estado_farois]) + bytes([5, 9, 9, 9])
            #     enviar_requisicao(uarto_filestream, requisicao)
            #     estado_registrador = 0x00
        

def desligar_farol_baixo():
    GPIO.output(FAROL_BAIXO, False)
    farol_painel(0,'baixo')

def desligar_farol_alto():
    GPIO.output(FAROL_BAIXO, False)
    farol_painel(0,'alto')

def desligar_painel():
    desligar_farol_alto()
    desligar_farol_baixo()
    seta_painel(0, 'l')
    seta_painel(0, 'r')
    set_rpm_painel(0)
    set_velocidade_painel(0)

def set_velocidade_painel(velocidade):
    endereco = 0x01
    codigo = 0x06
    sub_codigo = 0x03
    quantidade = [4]
    matricula = [9,5,9,9]
    matricula_bytes = bytes(matricula)
    quantidade_bytes = bytes(quantidade)
    dados = bytearray(struct.pack("f", velocidade)) 
    dados_bytes = bytes(dados)
    requisicao = bytes([endereco, codigo, sub_codigo]) + quantidade_bytes + dados_bytes + matricula_bytes

    crc16 = calcula_CRC(requisicao)
    crc_bytes = struct.pack("<H", crc16)
    requisicao_com_crc = requisicao + crc_bytes
    os.write(uarto_filestream, requisicao_com_crc)

    sleep(0.1)
    leitura = os.read(uarto_filestream, 255)
    mensagem, crc_recebido = leitura[:-2], leitura[-2:]
    crc_calculado = struct.pack("<H", calcula_CRC(mensagem))

def set_rpm_painel(rpm):
    endereco = 0x01
    codigo = 0x06
    sub_codigo = 0x07
    quantidade = [4]
    matricula = [9,5,9,9]
    matricula_bytes = bytes(matricula)
    quantidade_bytes = bytes(quantidade)
    dados = bytearray(struct.pack("f", rpm)) 
    dados_bytes = dados
    requisicao = bytes([endereco, codigo, sub_codigo]) + quantidade_bytes + dados_bytes + matricula_bytes

    crc16 = calcula_CRC(requisicao)
    crc_bytes = struct.pack("<H", crc16)
    requisicao_com_crc = requisicao + crc_bytes
    os.write(uarto_filestream, requisicao_com_crc)

    sleep(0.1)
    leitura = os.read(uarto_filestream, 255)
    mensagem, crc_recebido = leitura[:-2], leitura[-2:]
    crc_calculado = struct.pack("<H", calcula_CRC(mensagem))

# Funções de callback para interrupções
def motor_pulse_callback(channel):
    global motor_pulse_count
    motor_pulse_count += 1

def wheel_pulse_callback(channel):
    global wheel_pulse_count, direction
    wheel_pulse_count += 1
    # Determina o sentido do giro
    if GPIO.input(WHEEL_HALL_A_PIN) == GPIO.input(WHEEL_HALL_B_PIN):
        direction = "reverse"  # Pulso B antes de A
    else:
        direction = "forward"  # Pulso A antes de B

def detect_rpm_and_velocity():
    start_time = time()
    start_motor_pulse_count = motor_pulse_count
    start_wheel_pulse_count = wheel_pulse_count
        # Aguarda 0.5 segundo para medir os pulsos
    sleep(0.3)

    # Calcula a frequência dos pulsos
    elapsed_time = time() - start_time
    motor_pulses = motor_pulse_count - start_motor_pulse_count
    wheel_pulses = wheel_pulse_count - start_wheel_pulse_count

    # Calcula o RPM do motor
    motor_rpm = (motor_pulses / elapsed_time) * SECONDS_PER_MINUTE

    # Calcula a velocidade do carro em km/h
    distance_moved = wheel_pulses * WHEEL_CIRCUMFERENCE  # Distância percorrida em metros
    speed_kmh = (distance_moved / elapsed_time) * KM_PER_METER * SECONDS_PER_MINUTE * SECONDS_PER_MINUTE

    # Exibe os resultados
    # print(f"Motor RPM: {motor_rpm:.2f} RPM")
    # print(f"Car speed: {speed_kmh:.2f} km/h")
    set_velocidade_painel(speed_kmh)
    set_rpm_painel(motor_rpm)
    return speed_kmh, motor_rpm

def detect_temperature():
    temperature = bmp280.get_temperature()
    degree_sign = u"\N{DEGREE SIGN}"
    if temperature > 115:
        GPIO.output(LUZ_TEMP, GPIO.HIGH)
    else: 
        GPIO.output(LUZ_TEMP, GPIO.LOW)
    format_temp = "{:.2f}".format(temperature)
    print('Temperature = ' + format_temp + degree_sign + 'C')
    return format_temp + degree_sign + 'C'
    