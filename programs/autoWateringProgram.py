import mysql.connector
import json
import smbus
import datetime
import time
import RPi.GPIO as GPIO

# Constants
MOIST_LEVEL = 40 # What is the acceptable minimum moisture level
CHECK_RATE = 1  # How often do we want the program to run, in minutes

# Define SMBus (System Management Bus) port and address for
# I2C sensor communcation
# ALL CODE FOR TEMP SENSOR WRITTEN BY PROFESOR EDDY, PULLED FROM LAB 07-08
BUS = smbus.SMBus(1)
ADDRESS = 0x48

# Set up GPIO pins for the solenoid and moisture sensor
GPIO.setmode(GPIO.BCM) #use BCM because we are dealing with incoming voltage
GPIO.setup(21, GPIO.OUT) # Solenoid out

# Table Header for display output
# Taken from lab07, edited to fit
def show_table_header():
    print("DATE\t   TIME \t    Temp \t Moisture")
    print("------------------------------------------------")

# Read the sensor data from the temperature sensor, return a value in Celsius
# Taken from lab07, no changes made
def get_temperature():
    rvalue0 = BUS.read_word_data(ADDRESS,0)
    rvalue1 = (rvalue0 & 0xff00) >> 8
    rvalue2 = rvalue0 & 0x00ff
    rvalue = (((rvalue2 * 256) + rvalue1) >> 4 ) * .0625
    return rvalue

def moisture_sensor(level):
    # Checks the value from the moisture sensor. If it is lower then then the set level,
    return level

# Take data from sensor and monitor any changes
def temp_data():
    # Get temperature reading from sensor in C, convert to F
    celcius = get_temperature()
    temp = (celcius * 1.8 + 32)

    # Return the temp
    return temp

# Display data to the screen, then send it to the database. Main loop
# Starter code borrowed from lab07, but heavily modified
def display_data():
    # Get time
    now = datetime.datetime.now()

    # Call temp_data to record the tempeture data
    temp = temp_data()

    # Call the moisture sensor, to check to see if the plant needs to be watered
    # Record the moisture level for output
    moist_level = moisture_sensor(41)

    # Display data record to screen
    # Display data written by Professor Eddy, but modified by Nick
    timestamp = now.strftime("%m/%d/%Y %H:%M")
    outstring = str(timestamp) + "\t" + str(format(temp, '10.4f')) + "F" \
    + str(format(moist_level, '10.0f'))
    print(outstring.rstrip())

    return temp, moist_level

# Show table header
show_table_header()

# Call function to print data to screen
try:
    # Set variables to see if plant needs watering, average temp, and mins to sleep
    needWatering = 0
    averageTemp = 0
    minsToSleep = 0
    timesWatered = 0

    # Create an array to store the averages, so we can get an overall average at the end
    averageArray = []

    while True:
        # Call the display_data function to get the moisture level and new temp
        newTemp, needWatering = display_data()
        averageArray.append(newTemp) # Add new temp to the array of temps

        # Check to see if the soil is dry enough to water
        if needWatering > MOIST_LEVEL:
            GPIO.output(21,True)
            time.sleep(15)
            GPIO.output(21,False)
            # Add one to the times the plant was watered
            timesWatered += 1

        # Orient the cycle to now start every 15 min, on the hour (00, 15, 30, 45, etc...)
        minsToSleep = CHECK_RATE - datetime.datetime.now().minute % CHECK_RATE
        time.sleep(minsToSleep * 60)

# Cleanup GPIO pins on program termination
finally:
    # Call function to print data to screen
    averageTemp = (sum(averageArray)) / len(averageArray)
    print("The average temp was: " + str(averageTemp) + " and the plant was watered " + str(timesWatered) + " times")
    GPIO.cleanup()


