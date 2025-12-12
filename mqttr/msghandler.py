# msghandler.py

from mqttr.ppmhandler import (
    CHANNEL_MIN,
    CHANNEL_CENTER,
    set_channel,
    pulse_channel,
    start_ppm_if_needed
)

# Start PPM (safe in both modes)
start_ppm_if_needed()

# CHANNEL MAPPING
# 0 = Roll
# 1 = Pitch
# 2 = Throttle
# 3 = Yaw

def _handle_move_forward():
    pulse_channel(1, 1400)   # pitch forward

def _handle_move_back():
    pulse_channel(1, 1600)   # pitch backward

def _handle_move_left():
    pulse_channel(0, 1400)   # roll left

def _handle_move_right():
    pulse_channel(0, 1600)   # roll right

def _handle_move_up():
    set_channel(2, 1600)     # throttle up

def _handle_move_down():
    set_channel(2, 1200)     # throttle down

def _handle_yaw_left():
    pulse_channel(3, 1400)   # rudder left

def _handle_yaw_right():
    pulse_channel(3, 1600)   # rudder right

def _handle_stop():
    set_channel(0, CHANNEL_CENTER)
    set_channel(1, CHANNEL_CENTER)
    set_channel(2, CHANNEL_MIN)
    set_channel(3, CHANNEL_CENTER)

_topic_router = {
    "move/forward": _handle_move_forward,
    "move/back": _handle_move_back,
    "move/left": _handle_move_left,
    "move/right": _handle_move_right,
    "move/up": _handle_move_up,
    "move/down": _handle_move_down,
    "move/yaw_left": _handle_yaw_left,
    "move/yaw_right": _handle_yaw_right,
    "move/stop": _handle_stop,
}

def message_router(topic, msg):
    if isinstance(topic, bytes): topic = topic.decode()
    if isinstance(msg, bytes): msg = msg.decode()

    handler = _topic_router.get(topic)
    if handler:
        print(f"\n[mqttr] Running {topic}")
        handler()
    else:
        print(f"[error] No handler for '{topic}' message '{msg}'")
