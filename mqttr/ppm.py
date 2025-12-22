import time

from machine import Pin

# Note: Everywhere you read US microseconds are meant

# Channel Constants
# Pulse widths (in microseconds) accepted by the flight controller
CHANNEL_MIN = 885
CHANNEL_CENTER = 1500
CHANNEL_MAX = 2115

# Channel Configs
# Number of RC channels
NUM_CHANNELS = 5
# pulse width for each channel (initialized to center)
# [roll, pitch, throttle, yaw, aux1] --> these are the values skyline32 needs + aux1 which i configured for arm/disarm ops
channels = [CHANNEL_CENTER] * NUM_CHANNELS

# PPM SIGNAL CONFIGURATION

# GPIO pin
# IMPORTANT NOTE: PPM PIN NUM is GP<num> and not <num> on the board!
# Resource: https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#pinout-and-design-files-4 Pico W pinout
PPM_PIN_NUM = 18

# Total length of one complete PPM frame (microseconds)
# This includes all channels plus the sync gap
FRAME_LENGTH_US = 22500

# Length of the short LOW pulse that separates channels (microseconds)
# This is the PPM marker pulse
PULSE_US = 400

# GPIO (general purpose input/output) init
# Create a GPIO pin object and configure it as an output
_ppm_pin = Pin(PPM_PIN_NUM, Pin.OUT)

# Set the pin high initially (PPM idle state is HIGH)
_ppm_pin.value(1)


# Functions

# Set a channel to a specific pulse width.
def set_channel(id, value):
    global channels

    # Ignore invalid channels (if set channel but id is out of range)
    if not 0 <= id < NUM_CHANNELS:
        return

    # parse value to int
    value = int(value)

    # clamp value to valid ranges
    if value < CHANNEL_MIN:
        value = CHANNEL_MIN
    if value > CHANNEL_MAX:
        value = CHANNEL_MAX

    # Store the pulse width for this channel.
    channels[id] = value


# Temporarily set a channel to a value, and then return the scheduled end time (so it can be set back to center later)
def pulse_channel(ch, value, duration_ms=250):
    # Set channel immediately to the requested value
    set_channel(ch, value)

    # Calculate when the pulse should end (current time + duration)
    end_time = time.ticks_add(time.ticks_ms(), duration_ms)

    # Return the scheduled end time and channel index
    return end_time, ch


# Check active pulses and reset channels whose pulse duration has expired.
def update_pulses(pulses):
    # Get the current time in milliseconds
    now = time.ticks_ms()

    # List of pulses that are still active
    still_active = []

    # (these values are being set in the function above.)
    for end_time, ch in pulses:
        # If the pulse has expired
        if time.ticks_diff(end_time, now) <= 0:
            # Reset channel back to center position
            set_channel(ch, CHANNEL_CENTER)
        else:
            # Keep pulse active
            still_active.append((end_time, ch))

    # Return only pulses that are still running
    return still_active


# Generate and output one complete PPM frame.
def output_ppm_frame():
    total = 0  # Tracks total time used so far in the frame

    # Loop through each channel and output its timing
    for width in channels:
        # Ensure channel width is within valid bounds
        width = max(CHANNEL_MIN, min(CHANNEL_MAX, int(width)))

        # Pull the line low to mark the start of a channel
        _ppm_pin.value(0)
        time.sleep_us(PULSE_US)  # start marker

        # calculate the high gap (channel value minus marker)
        high_us = width - PULSE_US

        # Prevent extremely short high times (otherwise it could be interpreted as a marker)
        if high_us < 50:
            high_us = 50

        # Set the line HIGH and wait for the channel duration
        _ppm_pin.value(1)
        time.sleep_us(high_us)

        # Add this channel's time to the frame total
        total += PULSE_US + high_us

    # Frame sync gap
    # Calculate how much time remains to complete the frame
    sync = FRAME_LENGTH_US - total

    # Ensure sync gap is at least one marker pulse long
    if sync < PULSE_US:
        sync = PULSE_US

    # Send final LOW marker
    _ppm_pin.value(0)
    time.sleep_us(PULSE_US)

    # Stay HIGH for the rest of the sync gap
    _ppm_pin.value(1)
    time.sleep_us(sync - PULSE_US)
