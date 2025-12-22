import sys
from time import sleep

import rp2
from picozero import pico_led

import env
import mqttr.utils
from mqttr.msghandler import get_pulses, message_router
from mqttr.ppm import update_pulses, output_ppm_frame

print("[startup]: Starting MQTTR")

# disarm on startup
message_router(b"move/disarm", b"1")

# check if env vars are set
if env.WIFI_SSID == "" or env.WIFI_PASSWORD == "":
    print("[error]: Wifi SSID or password not set in env.py")
    sys.exit()

# global vars
mqtt_client = None
wlan = None

try:
    # WIFI
    wlan = mqttr.utils.connect_wifi()

    # MQTT
    mqtt_client = mqttr.utils.connect_mqtt()

    # main loop
    print("[main]: Entering loop")
    mqtt_client.publish('info', '[pico]: Entering loop')

    while True:
        # BOOTSEL shutdown (hold the bootsel for one second and it will shutdown)
        if rp2.bootsel_button() == 1:
            sleep(1)
            if rp2.bootsel_button() == 1:
                mqtt_client.publish('info', '[pico]: Bootsel pressed')
                raise KeyboardInterrupt

        try:
            # check for incoming messages
            mqtt_client.check_msg()

        except Exception as e:
            # catch exceptions if check_msg fails (that happens when out of range or disconnections)
            try:
                # try to handle failure gracefully
                mqtt_client.publish('info', '[pico]: check_msg failed: ' + repr(e))
                mqtt_client.disconnect()
            except:
                pass  # throw the error further (see catch belw)
            try:
                if not wlan.isconnected():  # reconnect wifi if that is the issue
                    wlan = mqttr.utils.connect_wifi()
                mqtt_client = mqttr.utils.connect_mqtt()
            except Exception as e:
                pass

        # pulse counter
        pulses = get_pulses()  # gets a list of all pulses that are in the list
        pulses[:] = update_pulses(pulses)  # removes and reassigns all pulses which have been executed

        # send the ppm output
        output_ppm_frame()

except Exception as e:
    # General exception handling
    mqtt_client.publish('info', '[pico]: error: ' + repr(e))
    print("[error]:", repr(e))

finally:
    # Disconnect from MQTT and WiFi
    if mqtt_client:
        try:
            mqtt_client.publish('info', '[pico]: exiting loop')
            mqtt_client.disconnect()
            print("[mqtt]: Disconnected")
        except Exception as e:
            print("[mqtt]: Disconnect failed:", e)

    if wlan:
        try:
            wlan.disconnect()
            wlan.active(False)
            print("[wifi]: Disconnected")
        except Exception as e:
            print("[wifi]: Disconnect failed:", e)

    # and turn off the LED and pico
    pico_led.off()
    print("[shutdown]: MQTTR stopped")
    sys.exit()
