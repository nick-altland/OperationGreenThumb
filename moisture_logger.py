# CS121 - Temperature Sensor Lab

import mysql.connector
import json
import smbus
import datetime
import time
import RPi.GPIO as GPIO

MOIST_LEVEL = 40


#this is for initial state
from ISStreamer.Streamer import Streamer

# Define SMBus (System Management Bus) port and address for
# I2C sensor communcation
BUS = smbus.SMBus(1)
ADDRESS = 0x48

#streamer is the way to import the data from initial state
streamer= Streamer(bucket_name="moisture", bucket_key="RRETLXESPNUM", access_key="ist_hlplr9QdjDLIbI8FSW1YmGvo_xnBErzO")
watering_streamer= Streamer(bucket_name="watering", bucket_key="SNNKJH7FCEC5", access_key="ist_hlplr9QdjDLIbI8FSW1YmGvo_xnBErzO")

# Set up GPIO pins for the solenoid and moisture sensor
GPIO.setmode(GPIO.BCM) #use BCM because we are dealing with incoming voltage
GPIO.setup(21, GPIO.OUT) # Solenoid out


def show_table_header():
    print("Moisture Data Table")
    print("DATE\t   TIME \t   Moisture Level")
    print("----------------------------------------------")
    
   
# def get_temperature():
#     rvalue0 = BUS.read_word_data(ADDRESS,0)
#     rvalue1 = (rvalue0 & 0xff00) >> 8
#     rvalue2 = rvalue0 & 0x00ff
#     rvalue = (((rvalue2 * 256) + rvalue1) >> 4 ) * .0625
#     return rvalue

def moisture_sensor(level):
    # Checks the value from the moisture sensor. If it is lower then then the set level,
    return level

def store_display_data():
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

    # SQL insert statment
    insert_sql = "INSERT INTO `moisture_data` (`timestamp`, `moisture_level') VALUES (%s,%s);"

    # Get time
    now = datetime.datetime.now()

    # Get temperature reading from sensor in C, convert to F
   #  celcius = get_temperature()
   #  fahrenheit = (celcius * 1.8 + 32)
    moist_level = moisture_sensor(2)

    streamer.log("moisture", moist_level)
    streamer.flush()

    # Display data record to screen
    timestamp = now.strftime("%m/%d/%Y %H:%M")
    outstring = str(timestamp) + "\t" + str(format(moist_level,'10.4f'))
    print(outstring.rstrip())

    # Insert data into database
    data = (now,moist_level)
    cursor.execute(insert_sql,data)

    # Commit insert to database
    database.commit()

    # Close database connection
    cursor.close()
    database.close()

    # Define interval for temperature readings (in seconds)
    minsToSleep = 15 - datetime.datetime.now().minute % 15
    time.sleep(minsToSleep *60)

# Display table header
show_table_header()

# Call function to insert data to database and print to screen
while True:
    store_display_data()
    
    needWatering = 0
    timesWatered = 0
    
    if needWatering > MOIST_LEVEL:
            GPIO.output(21,True)
            time.sleep(15)
            GPIO.output(21,False)
            # Add one to the times the plant was watered
            timesWatered += 1
	    water_insert_sql = "INSERT INTO `watering_data` (`timestamp`, `on/off`) VALUES (%s, %s);"
            watering_streamer.log("watering", on/off)
            watering_streamer.flush()
            data = (now,1)
            cursor.execute(water_insert_sql,data)
            database.commit()
            # Close database connection
            cursor.close()
            database.close()
            

GPIO.cleanup()
