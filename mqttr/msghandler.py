from mqttr.ppm import (
    CHANNEL_CENTER,
    set_channel,
    pulse_channel, CHANNEL_MIN,
)

# global temporary pulse list
_pulses = []

def get_pulses():
    return _pulses

# safe constants for throttle / AUX
HOVER_THROTTLE = CHANNEL_CENTER  # safe medium for hover throttle (hopefully)
ARM_VALUE = 1600  # AUX1 high = motors ON
DISARM_VALUE = 1000  # AUX1 low = motors OFF
CURRENT_THROTTLE = CHANNEL_MIN
THROTTLE_STEP = 20
RAMP_DELAY_MS = 80


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

def _handle_move_back(): pulse(PITCH, 1600)

def _handle_move_left(): pulse(ROLL, 1400)

def _handle_move_right(): pulse(ROLL, 1600)

def _handle_yaw_left(): pulse(YAW, 1400)

def _handle_yaw_right(): pulse(YAW, 1600)

# Throttle up/down
def _handle_move_up():
    global CURRENT_THROTTLE
    CURRENT_THROTTLE = min(1800, CURRENT_THROTTLE + THROTTLE_STEP)
    set_channel(THROTTLE, CURRENT_THROTTLE)

def _handle_move_down():
    global CURRENT_THROTTLE
    CURRENT_THROTTLE = max(1000, CURRENT_THROTTLE - THROTTLE_STEP)
    set_channel(THROTTLE, CURRENT_THROTTLE)

# Dis-/Arm motors
def _handle_arm():
    global CURRENT_THROTTLE
    # aux1 high = armed
    set_channel(AUX1, ARM_VALUE)
    # go to safe throttle
    CURRENT_THROTTLE = 1000
    set_channel(THROTTLE, CURRENT_THROTTLE)

def _handle_disarm():
    global CURRENT_THROTTLE
    # reset throttle to safe value
    CURRENT_THROTTLE = CHANNEL_MIN
    set_channel(THROTTLE, CURRENT_THROTTLE)
    # Aux1 low = disarmed
    set_channel(AUX1, DISARM_VALUE)

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

    handler = _topic_router.get(topic)
    if handler:
        print(f"[mqttr] Running {topic}")
        handler()
    else:
        print(f"[error] No handler for '{topic}' message '{msg}'")
