# Projeto: Controle de Carro com Raspberry Pi

## Descrição

Este projeto utiliza um Raspberry Pi para implementar o controle de um carro. O sistema faz uso de sensores para monitorar a velocidade, direção e temperatura, além de controlar faróis, setas e o freio do veículo. O código é escrito em Python e utiliza a biblioteca RPi.GPIO para interação com os pinos GPIO do Raspberry Pi.

## Estrutura do Código

O código é organizado em:

- `carro.py`: Contém funções para controle de faróis, setas, painel e sensores.
- `crc.py`: Implementa a função de cálculo de CRC.
- `led.py`: Contém funções para controle de LEDs.
- `main.py`: Script principal que inicializa e executa o sistema.
- `requirements.txt`: Lista de dependências do projeto.

## Como Executar

Certifique-se de que todas as conexões de hardware estejam feitas corretamente conforme descrito nos requisitos.

1. Crie e ative um ambiente virtual:

   - No macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - No Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

2. Instale as dependências do arquivo
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o script principal:
   ```bash
   python3 main.py
   ```
4. Interaja com o sistema usando os controles físicos (botões ou sensores).
5. Desativar o ambiente virtual:
   ```bash
   deactivate
   ```

## Video

[Link video]()

## Observações

- Para interromper o programa com segurança, pressione `Ctrl+C`.
- Certifique-se de que os componentes conectados ao Raspberry Pi estejam dimensionados corretamente para evitar danos ao hardware.

## Autores

| Nome                   | Matrícula |
| ---------------------- | --------- |
| Bruno Henrique Cardoso | 190134275 |
| João Gabriel Elvas     | 190109599 |
