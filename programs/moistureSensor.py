#import libraries
import time
import RPi.GPIO as GPIO

#GPIO setup -- sensor is on 15. Set board to BCM so we can use hat
SENSOR_PIN = 15

GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN,GPIO.IN)

AIR = 620 #Moisture level in Air
WATER = 310 #Moisture level in water

try:

    while True:

       soilMoisture = GPIO.input(SENSOR_PIN) #readsin from the sensor
       print(soilMoisture) #print value
       soilPercent = map(soilMoisture, AIR, WATER, 0, 100)


       if soilPercent >= 100:
          print("100 %")

       elif soilPercent <=0:
          print("0 %")

       elif soilPercent >0 and soilPercent < 100:
          print(soilPercent)
          print("%")

finally:
    #cleanup the GPIO pins before ending
    GPIO.cleanup()


