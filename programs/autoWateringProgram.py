import mysql.connector
import json
import smbus
import datetime
import time
import RPi.GPIO as GPIO

# Constants
MIN_IN_DAY = 96

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
    print("DATE\t   TIME \t    High \t Low \t Average")
    print("-----------------------------------------------------------")

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
    # open up valve to water then close it
    if level % 2 == 0:
        GPIO.output(21,True)
        time.sleep(1)
        GPIO.output(21,False)

# Take data from sensor and monitor any changes
def temp_data(high, low, average):
    i = 0
    while i <= 1:
        # Get temperature reading from sensor in C, convert to F
        celcius = get_temperature()
        temp = (celcius * 1.8 + 32)

        # Set high/low using a series of if loops
        if temp > high:
            high = temp

        if temp < low:
            low = temp

        i+=1
        # Sleep for a second
        time.sleep(1)

    # Save the average
    average = (high + low)/2

    # Return the high, low, and average
    return high, low, average

# Display data to the screen, then send it to the database. Main loop
# Starter code borrowed from lab07, but heavily modified
def display_data(count):
    # Set variables for high, low, and average temps
    highTemp = 0
    lowTemp = 1000
    averageTemp = 0

    # Get time
    now = datetime.datetime.now()

    # Call temp_data to record the tempeture data
    highTemp, lowTemp, averageTemp = temp_data(highTemp, lowTemp, averageTemp)

    # Call the moisture sensor, to check to see if the plant needs to be watered
    moisture_sensor(count)

    # Display data record to screen
    # Display data written by Professor Eddy, but modified by Nick
    timestamp = now.strftime("%m/%d/%Y %H:%M")
    outstring = str(timestamp) + "\t" + str(format(highTemp, '10.4f')) + "F" \
    + str(format(lowTemp, '10.4f')) + "F" + str(format(averageTemp, '10.4f')) + "F" + "\n"
    print(outstring.rstrip())

# Show table header
show_table_header()

# Call function to print data to screen
while True:
    count = 0
    while count < MIN_IN_DAY:
        display_data(count)
        count+=1

# Cleanup GPIO pins on program termination


