# projeto de simulacao de casa inteligente com ESP32 e Micropython

## Pre-requisitos

1. [Wokwi for VS Code](https://marketplace.visualstudio.com/items?itemName=Wokwi.wokwi-vscode) 
2. [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) `pip install mpremote`.

## bibliotecas necessarias

baixe os arquivos abaixo e coloque dentro de uma pasta `lib/` na raiz do projeto:

| arquivo | repositorio |
|---|---|
| `ds1307.py` | https://github.com/mcauser/micropython-tinyrtc-i2c |
| `lcd_api.py` | https://github.com/dhylands/python_lcd |
| `esp32_gpio_lcd.py` | https://github.com/dhylands/python_lcd |
| `ir_rx.py` | https://github.com/peterhinch/micropython_ir (ir_rx/__init__.py) |
| `nec.py` | https://github.com/peterhinch/micropython_ir (ir_rx/nec.py) |

## como rodar no seu vscode:

1. clone o repositorio e abra no seu github
2. abra o simulador do wokwi em diagram.json e inicie a simulacao
3. com a simulacao rodando abra um segundo terminal e rode:

   ```
   mpremote connect port:rfc2217://localhost:4000 exec "import os; 'lib' not in os.listdir() and os.mkdir('lib')" + fs cp lib/ds1307.py :lib/ds1307.py + fs cp lib/esp32_gpio_lcd.py :lib/esp32_gpio_lcd.py + fs cp lib/lcd_api.py :lib/lcd_api.py + fs cp lib/ir_rx.py :lib/ir_rx.py + fs cp lib/nec.py :lib/nec.py + run main.py
   ```
