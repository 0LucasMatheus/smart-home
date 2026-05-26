# projeto de simulacao de casa inteligente com ESP32 e Micropython

## Pre-requisitos

1. [Wokwi for VS Code](https://marketplace.visualstudio.com/items?itemName=Wokwi.wokwi-vscode) 
2. [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) `pip install mpremote`.

## como rodar no seu vscode:

1. clone o repositorio e abra no seu github
2. abra o simulador do wokwi em diagram.json e inicie a simulacao
3. com a simulacao rodando abra um segundo terminal e rode:

   ```python
   python -m mpremote connect port:rfc2217://localhost:4000 run main.py
   ```
