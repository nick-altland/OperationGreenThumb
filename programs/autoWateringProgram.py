#Import libraries
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

# Constants
MOIST_LEVEL = 4 # How many seconds the solenoid will be open
CHECK_RATE = 1  # How often do we want the program to run, in minutes
MAX_MOIST = 47000  # Max moisture for the sensor
MIN_MOIST = 18000   # Min moisture for the sensor
MOISTURE = 20  # What percent moisture we want

ACTUAL_MAX_MOIST = MAX_MOIST - MIN_MOIST #After sensors is calebrated

# Define SMBus (System Management Bus) port and address for
# I2C sensor communcation
# ALL CODE FOR TEMP SENSOR WRITTEN BY PROFESOR EDDY, PULLED FROM LAB 07-08
BUS = smbus.SMBus(1)
ADDRESS = 0x48

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)

# This is for initial state
from ISStreamer.Streamer import Streamer

# Streamers to import data from the inital states.
# Structure borrowed from lab 08, but modified
# Streamer for the moisture levels
moist_streamer= Streamer(bucket_name="moisture", bucket_key="XCLS9WHG5QQH", access_key="ist_X2Iuw5yA30z4RVis-xsDv096lT0LkzaC")
# Streamer for the Watering
# watering_streamer= Streamer(bucket_name="watering",bucket_key="QS5TRLT67KNP", access_key="ist_X2Iuw5yA30z4RVis-xsDv096lT0LkzaC")
# Streamer for the temp levels
temp_streamer= Streamer(bucket_name="temp_charts", bucket_key="SJDT8SAWR34E", access_key="ist_X2Iuw5yA30z4RVis-xsDv096lT0LkzaC")

# Set up GPIO pins for the solenoid and moisture sensor
GPIO.setmode(GPIO.BCM) #use BCM because we are dealing with incoming voltage
GPIO.setup(21, GPIO.OUT) # Solenoid out
GPIO.setup(26, GPIO.IN)  # moisture sensor in

# Table Header for display output
# Taken from lab07, edited to fit
def show_table_header():
    print("DATE\t   TIME \t    Temp \t Moist %")
    print("------------------------------------------------")

# Read the sensor data from the temperature sensor, return a value in Celsius
# Taken from lab07, no changes made
def get_temperature():
    rvalue0 = BUS.read_word_data(ADDRESS,0)
    rvalue1 = (rvalue0 & 0xff00) >> 8
    rvalue2 = rvalue0 & 0x00ff
    rvalue = (((rvalue2 * 256) + rvalue1) >> 4 ) * .0625
    return rvalue

def moisture_sensor():
    # Checks the value from the moisture sensor. If it is lower then the desired number, open up valve to water then close it
    moist_level = (1-(chan.value-MIN_MOIST)/ACTUAL_MAX_MOIST)*100

    if moist_level < MOISTURE:
        GPIO.output(21,True)
        time.sleep(0.25)
        GPIO.output(21,False)
    # print(chan.value)
    # print(moist_level)

    return moist_level

# Take data from sensor and monitor any changes
def temp_data():
    # Get temperature reading from sensor in C, convert to F
    celcius = get_temperature()
    temp = (celcius * 1.8 + 32)

    # Return the temp
    return temp

def commit_temp(database, cursor, now, temp):
    # SQL insert statment for temp
    insert_temp_sql = "INSERT INTO `temp_data` (`timestamp`, `temp`) VALUES (%s,%s);"

    # Insert temp data into database
    data = (now, temp)
    cursor.execute(insert_temp_sql,data)

    # Commit insert to database
    database.commit()

    # Streamer to send data to graph
    temp_streamer.log("temp_charts", temp)
    temp_streamer.flush()
    return

def commit_moisture(database, cursor, now, moist_level):
    # SQL insert statment for moist
    insert_moist_sql = "INSERT INTO `moisture_data` (`timestamp`, `moisture_level`) VALUES (%s,%s);"

    # Insert moisture data into database
    data = (now, moist_level)
    cursor.execute(insert_moist_sql, data)

    # Commit insert to database
    database.commit()

    # Streamer to send data to graph
    moist_streamer.log("moisture", moist_level)
    moist_streamer.flush()
    return

def commit_needs_watering(database, cursor, now):
    # SQL insert statment for if the plant has been watered
    water_insert_sql = "INSERT INTO `watering_data` (`timestamp`, `watered`) VALUES (%s, %s);"

    # Insert moisture data into database
    data = (now, 1)
    cursor.execute(water_insert_sql, data)

    # Commit insert to database
    database.commit()

    # Streamer to send data to graph
    # watering_streamer.log("watering", 1)
    # watering_streamer.flush()

    return

# Function for setting up connection to database
# Code structure from lab 07
def database_info(now, temp, moist_level):
    # Load database user credentials from JSON
    credentials = json.load(open("credentials.json", "r"))

    # Connect to database
    database = mysql.connector.connect(
        host=credentials["host"],
        user=credentials["user"],
        passwd=credentials["password"],
        database=credentials["database"]
    )

    # Create cursor object that executes database commands
    cursor = database.cursor()

    # Send temp data to database
    commit_temp(database, cursor, now, temp)

    # Send moisture data to database
    commit_moisture(database, cursor, now, moist_level)

    # if moist_level < MOIST_LEVEL:
        #commit_needs_watering(database, cursor, now)

    # Close cursor and database
    cursor.close()
    database.close()

    return

# Display data to the screen, then send it to the database. Main loop
# Starter code borrowed from lab07, but heavily modified
def store_display_data():
    # Get time
    now = datetime.datetime.now()

    # Call temp_data to record the tempeture data
    temp = temp_data()

    # Call the moisture sensor, to check to see if the plant needs to be watered
    # Record the moisture level for output
    moist_level = moisture_sensor()

    # Display data record to screen
    # Display data written by Professor Eddy, but modified by Nick
    timestamp = now.strftime("%m/%d/%Y %H:%M")
    outstring = str(timestamp) + "\t" + str(format(temp, '10.4f')) + "F" \
    +"\t" + str(format(moist_level, '7.0f')) + "%" + "\n"
    print(outstring.rstrip())

    #Return the temp and moisture level
    return temp, moist_level, now

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
        newTemp, moist_level, now = store_display_data()
        averageArray.append(newTemp) # Add new temp to the array of temps

        # Call Database to store information
        database_info(now, newTemp, moist_level)

        # Orient the cycle to now start every 15 min, on the hour (00, 15, 30, 45, etc...)
        minsToSleep = CHECK_RATE - datetime.datetime.now().minute % CHECK_RATE
        time.sleep(1) #time.sleep(minsToSleep * 60)


# Cleanup GPIO pins on program termination
finally:
    # Call function to print data to screen
    averageTemp = (sum(averageArray)) / len(averageArray)
    print("The average temp was: " + str(format(averageTemp, "10.4f")))
    GPIO.cleanup()


