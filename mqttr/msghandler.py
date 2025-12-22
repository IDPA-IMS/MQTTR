# mqttr/msghandler.py
from mqttr.ppm import (
    CHANNEL_CENTER,
    set_channel,
    pulse_channel,
)

# global temporary pulse list
_pulses = []


def get_pulses():
    return _pulses


# safe constants for throttle / AUX
HOVER_THROTTLE = CHANNEL_CENTER  # safe medium for hover throttle (hopefully)
ARM_VALUE = 1600  # AUX1 high = motors ON
DISARM_VALUE = 1000  # AUX1 low = motors OFF

# channel mapping
ROLL = 0
PITCH = 1
THROTTLE = 2
YAW = 3
AUX1 = 4


def pulse(ch, value, duration_ms=250):
    _pulses.append(pulse_channel(ch, value, duration_ms))


# Movement handlers
def _handle_move_forward(): pulse(PITCH, 1400)


def _handle_move_back():    pulse(PITCH, 1600)


def _handle_move_left():    pulse(ROLL, 1400)


def _handle_move_right():   pulse(ROLL, 1600)


def _handle_yaw_left():     pulse(YAW, 1400)


def _handle_yaw_right():    pulse(YAW, 1600)


# Throttle up/down (persistent until another command)
def _handle_move_up():      pulse(THROTTLE, 1600)


def _handle_move_down():    pulse(THROTTLE, 1200)


# Arm motors separately
def _handle_arm():    set_channel(AUX1, ARM_VALUE)


def _handle_disarm():    set_channel(AUX1, DISARM_VALUE)


# Topic router
_topic_router = {
    "move/forward": _handle_move_forward,
    "move/back": _handle_move_back,
    "move/left": _handle_move_left,
    "move/right": _handle_move_right,
    "move/up": _handle_move_up,
    "move/down": _handle_move_down,
    "move/yaw_left": _handle_yaw_left,
    "move/yaw_right": _handle_yaw_right,
    "move/disarm": _handle_disarm,
    "move/arm": _handle_arm,
}


def message_router(topic, msg):
    if isinstance(topic, bytes):
        topic = topic.decode()
    if isinstance(msg, bytes):
        msg = msg.decode()

    # ignore messages from this Pico
    if msg.startswith('[pico]'):
        return

    handler = _topic_router.get(topic)
    if handler:
        print(f"[mqttr] Running {topic}")
        handler()
    else:
        print(f"[error] No handler for '{topic}' message '{msg}'")
