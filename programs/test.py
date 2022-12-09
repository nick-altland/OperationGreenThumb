import mysql.connector
import json
import smbus
import datetime
import time
import RPi.GPIO as GPIO
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


# Define SMBus (System Management Bus) port and address for
# I2C sensor communcation
# ALL CODE FOR TEMP SENSOR WRITTEN BY PROFESOR EDDY, PULLED FROM LAB 07-08
BUS = smbus.SMBus(1)
ADDRESS = 0x48
MAX_MOIST = 48000
MIN_MOIST = 17000
MOISTURE = 20
ACTUAL_MAX_MOIST = MAX_MOIST - MIN_MOIST

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)

# Set up GPIO pins for the solenoid and moisture sensor
GPIO.setmode(GPIO.BCM) #use BCM because we are dealing with incoming voltage
GPIO.setup(21, GPIO.OUT) # Solenoid out
GPIO.setup(26,GPIO.IN) #Moisture in

# Table Header for display output
# Taken from lab07, edited to fit
def show_table_header():
    print("DATE\t   TIME \t    High \t Low \t Average \t Moisture")
    print("-------------------------------------------------------------------------")

# Read the sensor data from the temperature sensor, return a value in Celsius
# Taken from lab07, no changes made
def get_temperature():
    rvalue0 = BUS.read_word_data(ADDRESS,0)
    rvalue1 = (rvalue0 & 0xff00) >> 8
    rvalue2 = rvalue0 & 0x00ff
    rvalue = (((rvalue2 * 256) + rvalue1) >> 4 ) * .0625
    return rvalue

def moisture_sensor():
    # Checks the value from the moisture sensor. If it is lower then then the set level,
    # open up valve to water then close it
    moist_level = (1-(chan.value-MIN_MOIST)/ACTUAL_MAX_MOIST)*100

    if moist_level < MOISTURE:
        GPIO.output(21,True)
        time.sleep(0.25)
        GPIO.output(21,False)

    # print(moist_level)

    return moist_level

# Take data from sensor and monitor any changes
def temp_data(high, low, average):
    i = 0
    while i < 5:
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
def display_data(highTemp, lowTemp, averageTemp):
    # Get time
    now = datetime.datetime.now()

    # Call temp_data to record the tempeture data
    highTemp, lowTemp, averageTemp = temp_data(highTemp, lowTemp, averageTemp)

    # Call the moisture sensor, to check to see if the plant needs to be watered
    # Record the moisture level for output
    moist_level = moisture_sensor()

    # Display data record to screen
    # Display data written by Professor Eddy, but modified by Nick
    timestamp = now.strftime("%m/%d/%Y %H:%M")
    outstring = str(timestamp) + "\t" + str(format(highTemp, '10.4f')) + "F" \
    + str(format(lowTemp, '10.4f')) + "F" + str(format(averageTemp, '10.4f')) + "F" \
    + str(format(moist_level, '10.2f')) + '%' "\n"
    print(outstring.rstrip())

    # Return the Average temp
    return averageTemp

# Show table header
show_table_header()

# Call function to print data to screen
try:
    # Set variables for high, low, and average temps
    highTemp = 0
    lowTemp = 1000
    averageTemp = 0

    # Create an array to store the averages, so we can get an overall average at the end
    averageArray = []

    while True:
        # Call the display_data function to get the moisture level, high/low, and average temp
        newAverageTemp = display_data(highTemp, lowTemp, averageTemp)
        averageArray.append(newAverageTemp)
        averageTemp = (sum(averageArray)) / len(averageArray)


# Cleanup GPIO pins on program termination
finally:
    print("The average temp was: " + str(averageTemp))
    GPIO.cleanup()


