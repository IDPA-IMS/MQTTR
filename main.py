from time import sleep
import rp2
import sys
from lib.umqtt.simple import MQTTClient
import env
import mqttr.utils
from mqttr.msghandler import message_router

# WiFi credentials
ssid = env.WIFI_SSID
password = env.WIFI_PASSWORD

print("[startup]: Starting MQTTR")

# Exit if WiFi credentials are missing
if ssid == "" or password == "":
    print("[error]: Wifi SSID or password not set in env.py")
    sys.exit()


# === MAIN ENTRYPOINT ===
mqttr.utils.connect_to_wifi()
mqttr.utils.test_connection_to_broker()

# Create MQTT client
mqtt_client = MQTTClient(client_id="MQTTR-PICO",server=env.MQTT_BROKER,port=1883)

print("[mqtt]: MQTT started")

mqtt_client.set_callback(mqttr.msghandler.message_router)

print("[mqtt]: Connecting to broker....")

mqtt_client.connect()

print("[mqtt]: Broker connected, subscribing to topics...")

mqtt_client.subscribe("move/#")

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
