import socket
import network
from time import sleep
from picozero import pico_led
import rp2
import sys
from lib.umqtt.simple import MQTTClient
import env

# WiFi credentials
ssid = env.WIFI_SSID
password = env.WIFI_PASSWORD

print("[startup]: Starting MQTTR")

# Exit if WiFi credentials are missing
if ssid == "" or password == "":
    print("[error]: Wifi SSID or password not set in env.py")
    sys.exit()


# Connect to WiFi
def connect_to_hotspot():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    # Wait for connection
    while not wlan.isconnected():
        if rp2.bootsel_button() == 1:  # The connection process is cancelable
            sys.exit()
        print('[debug]: Waiting for connection...')
        pico_led.on()  # Blinking LED when connecting
        sleep(0.5)
        pico_led.off()
        sleep(0.5)

    # Set MQTT broker as gateway
    env.MQTT_BROKER = wlan.ifconfig()[2]
    local_ip = wlan.ifconfig()[0]
    print(f'[log]: Connected with pico ip: {local_ip}')
    pico_led.on()
    return local_ip


# Test raw TCP connection to MQTT broker
def test_connection_to_broker():
    s = socket.socket()
    try:
        print("[test]: Testing raw TCP connection...")
        s.settimeout(7)
        s.connect((env.MQTT_BROKER, 1883))
        print("[success]: TCP connection OK")
    except Exception as e:
        print("[error]: TCP connection failed:", e)
        pico_led.off()
        sys.exit()
    finally:
        s.close()


# Callback function triggered when a message is received
def message_handler(topic, msg):
    msg = msg.decode()
    print(f"[mqtt]: Received message on topic {topic}: {msg}")


# === MAIN ENTRYPOINT ===
connect_to_hotspot()            # connect to WiFi
test_connection_to_broker()     # test connection to broker

# Create MQTT client
mqtt_client = MQTTClient(
    client_id="MQTTRPICO-01",
    server=env.MQTT_BROKER,
    port=1883
)

print("[mqtt]: MQTT started")
mqtt_client.set_callback(message_handler)  # set callback function
print("[mqtt]: Connecting to broker....")
mqtt_client.connect()                      # connect to MQTT broker
print("[mqtt]: Broker connected, subscribing to topics...")
mqtt_client.subscribe("move/#")       # subscribe to topic "test/topic"
print("[mqtt]: subscribed")

# Listen for incoming messages indefinitely
while True:
    if rp2.bootsel_button() == 1: # To shutdown, hold button for 1 second
        sleep(1)
        if rp2.bootsel_button() == 1:
            mqtt_client.disconnect()
            print("[shutdown]: MQTTR shutdown")
            sys.exit()
        else:
            continue
    mqtt_client.check_msg()
    sleep(0.1)


