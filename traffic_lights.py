import RPi.GPIO as GPIO
import time
import signal
import sys

time_main_green = 8
time_main_yellow = 2

GPIO.setwarnings(False)

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)  # MAIN RED
GPIO.setup(18, GPIO.OUT)  # MAIN YELLOW
GPIO.setup(27, GPIO.OUT)  # MAIN GREEN
GPIO.setup(22, GPIO.OUT)  # RED
GPIO.setup(23, GPIO.OUT)  # YELLOW
GPIO.setup(24, GPIO.OUT)  # GREEN


# Turn off all lights when user ends demo
def allLightsOff(signal, frame):
    GPIO.output(17, False)
    GPIO.output(18, False)
    GPIO.output(27, False)
    GPIO.output(22, False)
    GPIO.output(23, False)
    GPIO.output(24, False)
    GPIO.cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, allLightsOff)

# Loop forever
while True:
    # Main Green
    GPIO.output(17, False)
    GPIO.output(18, False)
    GPIO.output(27, True)
    # Red
    GPIO.output(22, True)
    GPIO.output(23, False)
    GPIO.output(24, False)
    time.sleep(time_main_green)

    # Main Yellow
    GPIO.output(17, False)
    GPIO.output(18, True)
    GPIO.output(27, False)
    # Red
    GPIO.output(22, True)
    GPIO.output(23, False)
    GPIO.output(24, False)
    time.sleep(time_main_yellow)

    # Main Red
    GPIO.output(17, True)
    GPIO.output(18, False)
    GPIO.output(27, False)
    # Green
    GPIO.output(22, False)
    GPIO.output(23, False)
    GPIO.output(24, True)
    time.sleep(time_main_green)

    # Main Red
    GPIO.output(17, True)
    GPIO.output(18, False)
    GPIO.output(27, False)
    # Yellow
    GPIO.output(22, False)
    GPIO.output(23, True)
    GPIO.output(24, False)
    time.sleep(time_main_yellow)
