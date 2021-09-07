import RPi.GPIO as GPIO
import sys

GPIO.setwarnings(False)

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)  # MAIN RED
GPIO.setup(18, GPIO.OUT)  # MAIN YELLOW
GPIO.setup(27, GPIO.OUT)  # MAIN GREEN
GPIO.setup(22, GPIO.OUT)  # RED
GPIO.setup(23, GPIO.OUT)  # YELLOW
GPIO.setup(24, GPIO.OUT)  # GREEN

# Turn off all lights
GPIO.output(17, False)
GPIO.output(18, False)
GPIO.output(27, False)
GPIO.output(22, False)
GPIO.output(23, False)
GPIO.output(24, False)
GPIO.cleanup()
sys.exit(0)
