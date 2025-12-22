import socket
import sys
from time import sleep

import network
import rp2
from picozero import pico_led

import env
from lib.umqtt.simple import MQTTClient
from mqttr.msghandler import message_router


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
    print(f'[log]: Connected with pico ip: {wlan.ifconfig()[0]}')
    pico_led.on()
    return wlan


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


def connect_wifi():
    print("[wifi]: Connecting...")
    wlan = connect_to_wifi()
    test_connection_to_broker()
    print("[wifi]: Connected")
    return wlan


def connect_mqtt():
    print("[mqtt]: Creating client")
    client = MQTTClient(
        client_id="MQTTR-PICO",
        server=env.MQTT_BROKER,
        port=1883,
        keepalive=30
    )

    client.set_callback(message_router)
    client.set_last_will("info", "[pico]: MQTTR disconnected")

    print("[mqtt]: Connecting...")
    client.connect()
    client.subscribe("move/#")
    client.publish("info", "[pico]: MQTTR connected")

    print("[mqtt]: Connected and subscribed")
    return client
