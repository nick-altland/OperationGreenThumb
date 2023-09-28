# Tracks the temp

import mysql.connector
import json
import smbus
import datetime
import time
from ISStreamer.Streamer import Streamer

# Define SMBus (System Management Bus) port and address for
# I2C sensor communcation
BUS = smbus.SMBus(1)
ADDRESS = 0x48

streamer= Streamer(bucket_name="temp", bucket_key="XEPWBJXDBGND", access_key="ist_hlplr9QdjDLIbI8FSW1YmGvo_xnBErzO")


def show_table_header():
    print("Temperature Data Table")
    print("Chloe Hoff\n") # Replace with your name here!
    print("DATE\t   TIME \t   TEMP_C     TEMP_F")
    print("----------------------------------------------")

def get_temperature():
    rvalue0 = BUS.read_word_data(ADDRESS,0)
    rvalue1 = (rvalue0 & 0xff00) >> 8
    rvalue2 = rvalue0 & 0x00ff
    rvalue = (((rvalue2 * 256) + rvalue1) >> 4 ) * .0625
    return rvalue

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
    insert_sql = "INSERT INTO `temperature_data` (`timestamp`, `value_c`, `value_f`) VALUES (%s,%s,%s);"

    # Get time
    now = datetime.datetime.now()

    # Get temperature reading from sensor in C, convert to F
    celcius = get_temperature()
    fahrenheit = (celcius * 1.8 + 32)

    streamer.log("temp", fahrenheit)
    streamer.flush()

    # Display data record to screen
    timestamp = now.strftime("%m/%d/%Y %H:%M")
    outstring = str(timestamp) + "\t" + str(format(celcius,'10.4f')) \
     + "C" + str(format((fahrenheit),"10.4f")) + "F" + "\n"
    print(outstring.rstrip())

    # Insert data into database
    data = (now,celcius,fahrenheit)
    cursor.execute(insert_sql,data)

    # Commit insert to database
    database.commit()

    # Close database connection
    cursor.close()
    database.close()

    # Define interval for temperature readings (in seconds)
    time.sleep(10)

# Display table header
show_table_header()

# Call function to insert data to database and print to screen
while True:
    store_display_data()
