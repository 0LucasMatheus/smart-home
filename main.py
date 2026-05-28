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
lcd_d6   = 16     
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
buzzer = PWM(Pin(buzzer_pin))
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


########## rtc relogio

import ntptime

fuso_brasil = -3

def sincronizar_rtc():
    ntptime.settime()
    ano, mes, dia, hora, minuto, segundo, semana, dia_do_ano = time.localtime()
    hora = hora + fuso_brasil
    if hora < 0:
        hora = hora + 24
        dia = dia - 1
    if hora >= 24:
        hora = hora - 24
        dia = dia + 1
    rtc.datetime = (ano, mes, dia, semana, hora, minuto, segundo, 0)
    print("rtc sincronizado")

def ler_hora():
    return rtc.datetime[4]

def ler_minuto():
    return rtc.datetime[5]

def ler_segundo():
    return rtc.datetime[6]

def mostrar_hora():
    hora = ler_hora()
    minuto = ler_minuto()
    segundo = ler_segundo()
    hora_str = f"{hora:02d}:{minuto:02d}:{segundo:02d}"
    return hora_str

def mostrar_data():
    ano = rtc.datetime[0]
    mes = rtc.datetime[1]
    dia = rtc.datetime[2]
    data_str = f"{dia:02d}/{mes:02d}/{ano}"
    return data_str



sincronizar_rtc()
print("hora:", ler_hora())
print("minuto:", ler_minuto())
print("segundo:", ler_segundo())
print("hora formatada:", mostrar_hora())
print("data formatada:", mostrar_data())



################################# funcoes sensores

########## sensor IR - infravermelho

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
    ultimo_sinalVermelho = None
    return cmd


########## sensor de luz (ldr)

def ler_ldr():
    leitura = ldr.read()
    luminosidade = 100 -round(leitura * 100 / 4095)
    return luminosidade


########## sensor de temperatura

import math

# def ler_temperatura():    # wokwi - NTC
#     leitura = ntc.read()
#     if leitura == 0:
#         return 0
#     voltagem = leitura * 3.3 / 4095
#     r_ntc = 10000 * voltagem / (3.3 - voltagem)
#     temp = 1 / (1/298.15 + (1/3950) * math.log(r_ntc / 10000))
#     temp = temp - 273.15
#     return round(temp, 1)

def ler_temperatura():    # fisico - LM35
    leitura = ntc.read()
    voltagem = leitura * 3.3 / 4095
    temp = voltagem * 100
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


############################################# funcoes atuadores

########## buzzer

def ligar_buzzer(freq=440):
    buzzer.freq(freq)
    buzzer.duty(512)


def desligar_buzzer():
    buzzer.duty(0)

def beep(duracao=0.2, freq=440, repeat=1):
    for i in range(repeat):
        ligar_buzzer(freq)
        time.sleep(duracao)
        desligar_buzzer()


########## servo

angulo_servo = 0

def mover_servo(angulo):
    global angulo_servo
    if angulo < 0:
        angulo = 0
    if angulo > 180:
        angulo = 180
    angulo_servo = angulo
    duty_angulo = int(40 + (angulo / 180) * 75) # ajuste para 0-180 graus +ou-
    servo.duty(duty_angulo)

def fechar_servo():
    mover_servo(0)

def abrir_servo():
    mover_servo(180)


########## motor de passo

padroes = [
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 0, 1],
]

padrao_atual = 0
passo_velocidade = 10

def girar_motor(lado, velocidade):
    global padrao_atual
    if velocidade < passo_velocidade:
        velocidade = passo_velocidade
    if velocidade > 100:
        velocidade = 100
    delay = int(22 - (velocidade / 100) * 20)
    if lado == "horario":
        padrao_atual = padrao_atual + 1
        if padrao_atual > 3:
            padrao_atual = 0

    if lado == "anti":
        if padrao_atual == 0:
            padrao_atual = 3
        else:
            padrao_atual = padrao_atual - 1
            
    mot1.value(padroes[padrao_atual][0])
    mot2.value(padroes[padrao_atual][1])
    mot3.value(padroes[padrao_atual][2])
    mot4.value(padroes[padrao_atual][3])
    time.sleep_ms(delay)

def parar_motor():
    mot1.value(0)
    mot2.value(0)
    mot3.value(0)
    mot4.value(0)


########## atuador rele

def ligar_rele():
    rele.value(1)

def desligar_rele():
    rele.value(0)










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

def tela_luz():
    mostrar_lcd("Luminosidade:", str(ler_ldr()) + "%")

telas = {
    48: tela_temperatura, # botao 1
    24: tela_distancia,   # 2
    122: tela_luz,        # 3
}


########## mqtt

import ujson
from umqtt.simple import MQTTClient

broker_url     = "faa537d2fa124d9fab4b43af033e4b18.s1.eu.hivemq.cloud"
broker_porta   = 8883
broker_usuario = "smart-home"
broker_senha   = "SmartHome123"

mqtt = MQTTClient(
    client_id="esp32-smart-home",
    server=broker_url,
    port=broker_porta,
    user=broker_usuario,
    password=broker_senha,
    ssl=True,
    ssl_params={"server_hostname": broker_url}
)
mqtt.connect()
print("mqtt conectado")

def publicar_status():
    dados = {
        "temperatura": ler_temperatura(),
        "distancia": ler_distancia(),
        "luminosidade": ler_ldr(),
        "tela": tela_atual,
        "rele": rele.value(),
        "motor_ligado": motor_ligado,
        "velocidade_motor": velocidade_motor,
        "direcao_motor": direcao_motor
    }
    mqtt.publish("smart-home/status", ujson.dumps(dados))


########## google sheets

import urequests

sheets_url = "https://script.google.com/macros/s/AKfycbx4GYj-LygLNYQT-0gMAhGATHjXbs72zttV_7zSwhO9OhBsiYko8-5nupR4tRDrLTwc/exec"

fila_sheets = []

def gravar_sheets(alerta, data_hora):
    import gc
    gc.collect()
    linhas = [
        {"item": "Alerta",    "valor": f"alerta: {alerta} hora: {data_hora}"},
        {"item": "sensores",  "valor": f"temperatura: {ler_temperatura()} C || distancia: {ler_distancia()} cm || luminosidade: {ler_ldr()} %"},
        {"item": "---------------------", "valor": "------------------"},
    ]
    headers = {"Content-Type": "application/json"}
    corpo = ujson.dumps(linhas)
    try:
        r = urequests.post(sheets_url, data=corpo, headers=headers)
        r.close()
        print("sheets: ok")
    except Exception as e:
        print("sheets erro:", e)

def verificar_sheets(alerta):
    data_hora = mostrar_data() + " " + mostrar_hora()
    fila_sheets.append((alerta, data_hora))
    print("fila sheets:", alerta)


####### alertas

porta_aberta_registrada = False
movimento_registrado    = False
temperatura_registrada  = False

def verificar_alertas():
    global porta_aberta_registrada, movimento_registrado, temperatura_registrada

    hora = ler_hora()
    dist = ler_distancia()
    temp = ler_temperatura()

    # alerta 1 de movimento na porta durante a noite
    if (dist > 0 and dist < 50) and (hora >= 20 or hora < 8) and movimento_registrado == False:
        movimento_registrado = True
        verificar_sheets(f"alguem na porta: a {dist} cm detectada")

    if not (dist > 0 and dist < 50) and movimento_registrado == True:
        movimento_registrado = False

    # alerta 2 de temperatura alta
    if temp > 35 and temperatura_registrada == False:
        temperatura_registrada = True
        verificar_sheets(f"temperatura alta: {temp} C")

    if temp <= 35 and temperatura_registrada == True:
        temperatura_registrada = False

    # alerta 3 de porta aberta
    if angulo_servo > 0 and porta_aberta_registrada == False:
        porta_aberta_registrada = True
        verificar_sheets("porta aberta")

    # alerta 4 de porta fechada
    if angulo_servo == 0 and porta_aberta_registrada == True:
        porta_aberta_registrada = False
        verificar_sheets("porta fechada")


########## loop principal

motor_ligado = False
velocidade_motor = 20
direcao_motor = "horario"

ultimo_lcd    = time.ticks_ms()
ultimo_mqtt   = time.ticks_ms()
ultimo_alerta = time.ticks_ms()
ultimo_sheets = time.ticks_ms()







while True:
    agora = time.ticks_ms()
    cmd = ler_sinalVermelho()

    if cmd in telas:
        tela_atual = cmd

    if cmd == 2:
        if not motor_ligado or direcao_motor != "horario":
            direcao_motor = "horario"
            velocidade_motor = passo_velocidade
        else:
            velocidade_motor = velocidade_motor + passo_velocidade
            if velocidade_motor > 100:
                velocidade_motor = 100
        motor_ligado = True
        print("motor: horario, velocidade:", velocidade_motor)

    if cmd == 152:
        if not motor_ligado or direcao_motor != "anti":
            direcao_motor = "anti"
            velocidade_motor = passo_velocidade
        else:
            velocidade_motor = velocidade_motor + passo_velocidade
            if velocidade_motor > 100:
                velocidade_motor = 100
        motor_ligado = True
        print("motor: anti-horario, velocidade:", velocidade_motor)

    if cmd == 168:
        motor_ligado = False
        parar_motor()

    if motor_ligado:
        girar_motor(direcao_motor, velocidade_motor)

    if time.ticks_diff(agora, ultimo_lcd) >= 1000:
        if tela_atual in telas:
            telas[tela_atual]()
        ultimo_lcd = agora

    if time.ticks_diff(agora, ultimo_mqtt) >= 5000:
        publicar_status()
        ultimo_mqtt = agora

    if time.ticks_diff(agora, ultimo_alerta) >= 5000:
        verificar_alertas()
        ultimo_alerta = agora

    if time.ticks_diff(agora, ultimo_sheets) >= 10000:
        if fila_sheets:
            alerta, data_hora = fila_sheets.pop(0)
            gravar_sheets(alerta, data_hora)
        ultimo_sheets = agora
