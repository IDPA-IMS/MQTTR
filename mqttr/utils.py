import network
import rp2
import sys

import socket
from picozero import pico_led
from time import sleep
import env

# Function to connect to WiFis
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(env.WIFI_SSID, env.WIFI_PASSWORD)

    # Wait for connection
    while not wlan.isconnected():
        if rp2.bootsel_button() == 1:  # The connection process is cancelable
            sys.exit()
        print('[wifi]: Waiting for connection...')
        pico_led.on()  # Blinking LED when connecting
        sleep(0.5)
        pico_led.off()
        sleep(0.5)

    # Set gateway as mqtt broker
    env.MQTT_BROKER = wlan.ifconfig()[2]
    local_ip = wlan.ifconfig()[0]
    print(f'[log]: Connected with pico ip: {local_ip}')
    pico_led.on()
    return local_ip

# Test connection to MQTT broker
def test_connection_to_broker():
    s = socket.socket()
    try:
        print("[test]: Testing raw TCP connection...")
        s.settimeout(10)
        s.connect((env.MQTT_BROKER, 1883))
        print("[success]: TCP connection OK")
    except Exception as e:
        print("[error]: TCP connection failed:", e)
        pico_led.off()
        sys.exit()
    finally:
        s.close()
