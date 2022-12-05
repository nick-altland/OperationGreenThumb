# import GPIO and time
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)

try:
    while True:
        GPIO.output(21, True)
        time.sleep(1)
        #GPIO.output(21, False)
        #time.sleep(1)
finally:
    GPIO.cleanup()
