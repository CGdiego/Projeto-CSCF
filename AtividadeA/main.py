import network
import time
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configurações de Rede e MQTT
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""
MQTT_BROKER = "broker.hivemq.com"
MQTT_CLIENT_ID = "esp32_grupo18_templo_a"

TOPICO_PUB = b"cscf/grupo18/hollow/templo/infeccao"
TOPICO_SUB = b"cscf/grupo18/hollow/templo/comando"

# Configuração dos Pinos
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
led_laranja = Pin(2, Pin.OUT)

# Controle do LED
modo_manual = False

# Recebe comandos MQTT
def receber_comando(topico, mensagem):
    global modo_manual

    if mensagem == b"LIGAR":
        modo_manual = True
        led_laranja.value(1)
        print("Comando recebido: LED LIGADO")

    elif mensagem == b"DESLIGAR":
        modo_manual = True
        led_laranja.value(0)
        print("Comando recebido: LED DESLIGADO")

    elif mensagem == b"AUTO":
        modo_manual = False
        print("Comando recebido: MODO AUTOMATICO")

# 1. Conectar ao Wi-Fi
print("Conectando ao Wi-Fi Wokwi-GUEST...")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi.isconnected():
    time.sleep(0.5)
    print(".", end="")

print("\nWi-Fi Conectado!")

# 2. Conectar ao Broker HiveMQ
print("Conectando ao MQTT HiveMQ...")

client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
client.set_callback(receber_comando)
client.connect()
client.subscribe(TOPICO_SUB)

print("MQTT Conectado com Sucesso!")
print("Inscrito no tópico:", TOPICO_SUB)

# 3. Loop Principal
while True:
    # Verifica se chegaram comandos MQTT
    client.check_msg()

    valor_luz = ldr.read()

    if valor_luz < 2000:
        estado_infeccao = "ALTA"
    else:
        estado_infeccao = "BAIXA"

    # Controle automático do LED, se não houver comando manual
    if not modo_manual:
        if estado_infeccao == "ALTA":
            led_laranja.value(1)
        else:
            led_laranja.value(0)

    print("Luz:", valor_luz, "-> Infecção:", estado_infeccao)

    # Publica o estado do sensor
    client.publish(TOPICO_PUB, estado_infeccao.encode())

    time.sleep(3)
