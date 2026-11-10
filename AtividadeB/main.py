import network
import time
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Configurações
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""
MQTT_BROKER = "broker.hivemq.com"
MQTT_CLIENT_ID = "esp32_grupo18_estacao_b"

# Tópicos MQTT
TOPICO_SUB = b"cscf/grupo18/hollow/templo/infeccao"
TOPICO_COMANDO = b"cscf/grupo18/hollow/estacao/comando"
TOPICO_PUB = b"cscf/grupo18/hollow/estacao/chamado"

# Pinos
botao = Pin(4, Pin.IN, Pin.PULL_UP)
servo = PWM(Pin(15), freq=50)

infeccao_alta = False
modo_manual = False

# Controle do servo
def mover_servo(angulo):
    duty = int(((angulo / 180) * 75) + 40)
    servo.duty(duty)

# Recebe mensagens MQTT
def mqtt_callback(topic, msg):
    global infeccao_alta, modo_manual

    mensagem = msg.decode()

    if topic == TOPICO_SUB:
        print("Mensagem do Templo:", mensagem)

        if mensagem == "ALTA":
            infeccao_alta = True

            if not modo_manual:
                print("Lockdown! Fechando o portao.")
                mover_servo(0)

        elif mensagem == "BAIXA":
            infeccao_alta = False

            if not modo_manual:
                print("Caminho seguro. Abrindo portao.")
                mover_servo(90)

    elif topic == TOPICO_COMANDO:
        print("Comando recebido do Dashboard:", mensagem)

        if mensagem == "ABRIR":
            modo_manual = True
            mover_servo(90)
            print("Portao aberto manualmente.")

        elif mensagem == "FECHAR":
            modo_manual = True
            mover_servo(0)
            print("Portao fechado manualmente.")

        elif mensagem == "AUTO":
            modo_manual = False
            print("Modo automatico ativado.")

            if infeccao_alta:
                mover_servo(0)
            else:
                mover_servo(90)

# Conectar ao Wi-Fi
print("Conectando Wi-Fi...")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi.isconnected():
    time.sleep(0.5)

print("Wi-Fi OK!")

# Conectar ao MQTT
print("Conectando MQTT...")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
client.set_callback(mqtt_callback)
client.connect()

client.subscribe(TOPICO_SUB)
client.subscribe(TOPICO_COMANDO)

print("MQTT conectado!")
print("Escutando mensagens do Templo e do Dashboard...")

# Estado inicial
mover_servo(90)
ultimo_estado_botao = 1

# Loop principal
while True:
    client.check_msg()

    estado_botao = botao.value()

    if estado_botao == 0 and ultimo_estado_botao == 1:
        if not infeccao_alta:
            print("Chamando o Besouro!")
            client.publish(TOPICO_PUB, b"TRUE")
        else:
            print("O Besouro nao pode vir, infeccao alta!")

    ultimo_estado_botao = estado_botao
    time.sleep(0.1)