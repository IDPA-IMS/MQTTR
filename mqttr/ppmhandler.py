import time
import _thread

# =========================
# MODE
# =========================
MODE = "test"

# =========================
# CHANNEL VALUES
# =========================
CHANNEL_MIN = 1000
CHANNEL_CENTER = 1500
CHANNEL_MAX = 2000

NUM_CHANNELS = 6
channels = [CHANNEL_CENTER] * NUM_CHANNELS
_lock = _thread.allocate_lock()

# =========================
# TEST MODE
# =========================
def _set_channel_test(ch, value):
    value = max(CHANNEL_MIN, min(CHANNEL_MAX, value))
    with _lock:
        channels[ch] = value
    print(f"[TEST] set ch{ch} = {value}  Channels:", channels)

def _pulse_channel_test(ch, value, duration=0.25):
    print(f"[TEST] pulse ch{ch} = {value}")
    _set_channel_test(ch, value)
    time.sleep(duration)
    _set_channel_test(ch, CHANNEL_CENTER)

# =========================
# DEPLOYMENT MODE
# =========================
if MODE == "deployment":
    from machine import Pin

    PPM_PIN_NUM = 15
    FRAME_LENGTH_US = 22500
    PULSE_US = 400

    _ppm_pin = Pin(PPM_PIN_NUM, Pin.OUT)
    _ppm_pin.value(1)

    def _set_channel_deploy(ch, value):
        value = max(CHANNEL_MIN, min(CHANNEL_MAX, value))
        with _lock:
            channels[ch] = value

    def _pulse_channel_deploy(ch, value, duration=0.25):
        _set_channel_deploy(ch, value)
        time.sleep(duration)
        _set_channel_deploy(ch, CHANNEL_CENTER)

    def _ppm_thread():
        while True:
            with _lock:
                chs = channels[:]

            total = 0
            for ch in chs:
                _ppm_pin.value(0)
                time.sleep_us(PULSE_US)
                _ppm_pin.value(1)
                time.sleep_us(ch - PULSE_US)
                total += ch

            sync = FRAME_LENGTH_US - total
            if sync < PULSE_US:
                sync = PULSE_US

            _ppm_pin.value(0)
            time.sleep_us(PULSE_US)
            _ppm_pin.value(1)
            time.sleep_us(sync - PULSE_US)

    def start_ppm_if_needed():
        print("[PPM] Starting PPM thread.")
        _thread.start_new_thread(_ppm_thread, ())

else:
    def start_ppm_if_needed():
        print("[PPM] No thread started.")

# =========================
# PUBLIC API
# =========================
set_channel = _set_channel_deploy if MODE == "deployment" else _set_channel_test
pulse_channel = _pulse_channel_deploy if MODE == "deployment" else _pulse_channel_test

__all__ = [
    "CHANNEL_MIN",
    "CHANNEL_CENTER",
    "set_channel",
    "pulse_channel",
    "start_ppm_if_needed",
]
