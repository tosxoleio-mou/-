import RPi.GPIO as GPIO
import sys

GPIO.setwarnings(False)

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)  # LIGHTS

# Turn off all lights
GPIO.output(25, False)
GPIO.cleanup()
sys.exit(0)
