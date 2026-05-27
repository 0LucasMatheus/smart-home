from machine import Pin, PWM, ADC, I2C, time_pulse_us
import time
from ds1307 import DS1307
from esp32_gpio_lcd import GpioLcd
from nec import NEC_8

##########  configuração dos pinos 

# 4 sensores
ntc_pin    = 39
trig_pin   = 4
echo_pin   = 5
ldr_pin    = 35
sinalVermelho_pin     = 34

# 4 atuadores
buzzer_pin = 18
rele_pin   = 13
servo_pin  = 12
mot1_pin   = 25
mot2_pin   = 26
mot3_pin   = 27
mot4_pin   = 14

# RTC 
rtc_scl  = 32
rtc_sda  = 33

# LCD
lcd_rs   = 19
lcd_en   = 21
lcd_d4   = 22
lcd_d5   = 23
lcd_d6   = 0
lcd_d7   = 15

# sensores
ntc = ADC(Pin(ntc_pin))
ntc.atten(ADC.ATTN_11DB)

trig = Pin(trig_pin, Pin.OUT)
echo = Pin(echo_pin, Pin.IN)

ldr = ADC(Pin(ldr_pin))
ldr.atten(ADC.ATTN_11DB)

sinalVermelho = Pin(sinalVermelho_pin, Pin.IN)

# atuadores
buzzer = PWM(Pin(buzzer_pin), freq=440)
buzzer.duty(0)

rele = Pin(rele_pin, Pin.OUT)
rele.value(0)

servo = PWM(Pin(servo_pin), freq=50)
servo.duty(0)

mot1 = Pin(mot1_pin, Pin.OUT)
mot2 = Pin(mot2_pin, Pin.OUT)
mot3 = Pin(mot3_pin, Pin.OUT)
mot4 = Pin(mot4_pin, Pin.OUT)

# RTC - relogio
i2c = I2C(0, scl=Pin(rtc_scl), sda=Pin(rtc_sda))
rtc = DS1307(i2c)

# LCD
lcd = GpioLcd(
    rs_pin=Pin(lcd_rs),
    enable_pin=Pin(lcd_en),
    d4_pin=Pin(lcd_d4),
    d5_pin=Pin(lcd_d5),
    d6_pin=Pin(lcd_d6),
    d7_pin=Pin(lcd_d7),
    num_lines=2,
    num_columns=16
)

# IR - infravermelho

ultimo_sinalVermelho = None

def receber_sinal(cmd, addr, ctrl):
    global ultimo_sinalVermelho
    if cmd >= 0:
        ultimo_sinalVermelho = cmd
        print("botao IR:", cmd)

sinalVermelho_receiver = NEC_8(sinalVermelho, receber_sinal)

def ler_sinalVermelho():
    global ultimo_sinalVermelho
    cmd = ultimo_sinalVermelho
    return cmd


########## wifi

import network

def conectar_wifi(nome, senha):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(nome, senha)
    print("conectando ao wifi...")
    while not wifi.isconnected():
        time.sleep(0.5)
    print("conectado:", wifi.ifconfig()[0])

conectar_wifi("Wokwi-GUEST", "")


########## sensor de temperatura

import math

def ler_temperatura():
    leitura = ntc.read()
    if leitura == 0:
        return 0
    voltagem = leitura * 3.3 / 4095
    r_ntc = 10000 * voltagem / (3.3 - voltagem)
    temp = 1 / (1/298.15 + (1/3950) * math.log(r_ntc / 10000))
    temp = temp - 273.15
    return round(temp, 1)


########## sensor de distancia

def ler_distancia():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    duracao = time_pulse_us(echo, 1, 30000)
    if duracao < 0:
        return -1

    distancia = duracao // 58
    return distancia


########## lcd

def mostrar_lcd(linha1, linha2=""):
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(linha1[:16])
    lcd.move_to(0, 1)
    lcd.putstr(linha2[:16])
    
    
########## telas

tela_atual = 48

def tela_temperatura():
    mostrar_lcd("Temperatura:", str(ler_temperatura()) + " C")

def tela_distancia():
    mostrar_lcd("Distancia:", str(ler_distancia()) + " cm")

telas = {
    48: tela_temperatura, # botao 1
    24: tela_distancia,   # 2
}


########## loop principal

while True:
    cmd = ler_sinalVermelho()
    if cmd in telas:
        tela_atual = cmd

    if tela_atual in telas:
        telas[tela_atual]()

    time.sleep(1)
