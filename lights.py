import RPi.GPIO as GPIO
import signal
import sys

GPIO.setwarnings(False)

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)  # LIGHTS


# Turn off all lights when user ends demo
def allLightsOff(signal, frame):
    GPIO.output(25, False)
    GPIO.cleanup()
    sys.exit(0)


signal.signal(signal.SIGINT, allLightsOff)

# Loop forever
while True:
    # Lights on
    GPIO.output(25, True)
