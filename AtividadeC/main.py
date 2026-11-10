import network
import time
from machine import Pin, time_pulse_us
from umqtt.simple import MQTTClient

# Configuracoes de Rede e MQTT
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""
MQTT_BROKER = "broker.hivemq.com"
MQTT_CLIENT_ID = "esp32_grupo18_banco_c"

# Topicos MQTT
TOPICO_SUB = b"cscf/grupo18/hollow/estacao/chamado"
TOPICO_COMANDO = b"cscf/grupo18/hollow/banco/comando"
TOPICO_PUB = b"cscf/grupo18/hollow/banco/estado"

# Pinos dos componentes
pino_trig = Pin(5, Pin.OUT)
pino_echo = Pin(18, Pin.IN)
led_banco = Pin(19, Pin.OUT)
buzzer = Pin(21, Pin.OUT)

# Estados do sistema
modo_manual = False
estado_manual_led = False
estado_ocupado = False

# Mede a distancia usando o sensor HC-SR04
def medir_distancia():
    pino_trig.value(0)
    time.sleep_us(2)
    pino_trig.value(1)
    time.sleep_us(10)
    pino_trig.value(0)

    duracao = time_pulse_us(pino_echo, 1, 30000)

    if duracao < 0:
        return 999

    distancia = (duracao / 2) / 29.1
    return distancia

# Atualiza o LED conforme o modo de funcionamento
def atualizar_led():
    if modo_manual:
        led_banco.value(1 if estado_manual_led else 0)
    else:
        led_banco.value(1 if estado_ocupado else 0)

# Recebe mensagens MQTT
def mqtt_callback(topic, msg):
    global modo_manual, estado_manual_led

    mensagem = msg.decode()

    # Recebe o chamado da Estacao do Besouro
    if topic == TOPICO_SUB and mensagem == "TRUE":
        print("Aviso: O Besouro esta chegando!")

        for _ in range(3):
            led_banco.value(1)
            time.sleep(0.3)
            led_banco.value(0)
            time.sleep(0.3)

        atualizar_led()

    # Recebe comandos do Dashboard
    elif topic == TOPICO_COMANDO:
        print("Comando recebido do Dashboard:", mensagem)

        if mensagem == "LIGAR":
            modo_manual = True
            estado_manual_led = True
            atualizar_led()
            print("LED do banco ligado manualmente.")

        elif mensagem == "DESLIGAR":
            modo_manual = True
            estado_manual_led = False
            atualizar_led()
            print("LED do banco desligado manualmente.")

        elif mensagem == "AUTO":
            modo_manual = False
            atualizar_led()
            print("Modo automatico ativado.")

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
print("Escutando a Estacao e o Dashboard...")

estado_anterior = ""

# Loop principal
while True:
    client.check_msg()

    dist = medir_distancia()

    # Verifica se o banco esta ocupado
    if dist < 10:
        novo_estado = "OCUPADO"
        buzzer.value(1)
        time.sleep(0.1)
        buzzer.value(0)
    else:
        novo_estado = "LIVRE"

    estado_ocupado = (novo_estado == "OCUPADO")

    # Atualiza o LED se estiver no modo automatico
    if not modo_manual:
        atualizar_led()

    # Publica somente quando o estado muda
    if novo_estado != estado_anterior:
        print("Status do Banco:", novo_estado)
        client.publish(TOPICO_PUB, novo_estado.encode())
        estado_anterior = novo_estado

    time.sleep(0.5)
