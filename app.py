from flask import *
import mysql.connector
import json
import sys

app = Flask(__name__)

credentials = json.load(open("credentials.json", "r"))


@app.route('/temp', methods=['GET'])
def temp():
    database = mysql.connector.connect(
        host=credentials["host"],
        user=credentials["user"],
        passwd=credentials["password"],
        database=credentials["database"]
    )
    cursor = database.cursor()

    since_timestamp = request.args.get("since")
    print(since_timestamp)
    if since_timestamp is None:
        since_timestamp = "0"
    cursor.execute("SELECT * FROM temperature_data WHERE timestamp > '" + since_timestamp + "';")
    data = cursor.fetchall()

    cursor.close()
    database.close()
    return json.dumps(data)
    
    
@app.route('/moisture', methods=['GET'])
def moisture():
    database = mysql.connector.connect(
        host=credentials["host"],
        user=credentials["user"],
        passwd=credentials["password"],
        database=credentials["database"]
    )
    cursor = database.cursor()

    since_timestamp = request.args.get("since")
    print(since_timestamp)
    if since_timestamp is None:
        since_timestamp = "0"
    cursor.execute("SELECT * FROM moisture_data WHERE timestamp > '" + since_timestamp + "';")
    data = cursor.fetchall()

    cursor.close()
    database.close()
    return json.dumps(data)


@app.route('/', methods=['GET'])
def default():
    return redirect(url_for('temp_chart'))


@app.route('/temp_chart', methods=['GET'])
def temp_chart():
    return render_template("temp_chart.html", name="Operation Green Thumb")

@app.route('/is_chart', methods=['GET'])
def is_chart():
   return render_template("is_chart.html", name="Operation Green Thumb")

@app.route('/moisture_chart', methods=['GET'])
def moisture_chart():
   return render_template("moisture_chart.html", name="Operation Green Thumb")
