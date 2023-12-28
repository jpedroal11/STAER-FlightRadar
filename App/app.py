from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
import sqlite3

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///opensky_states.db'
db = SQLAlchemy(app)

class Plane(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    icao24 = db.Column(db.String)
    callsign = db.Column(db.String)
    origin_country = db.Column(db.String)
    time_position = db.Column(db.Integer)
    last_contact = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

def get_data_from_api():
    url = "https://opensky-network.org/api/states/all"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        return data["states"] if "states" in data else []
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return []

@app.route('/')
def index():
     # Connect to the SQLite database
    conn = sqlite3.connect('opensky_states.db')
    cursor = conn.cursor()

    # Fetch the plane data from the database
    cursor.execute('SELECT * FROM flights')
    avioes = cursor.fetchall()

    # Close the connection
    conn.close()

    # Render the template with plane data

    jsonAvioes = []
    for aviao in avioes:
        jsonAvioes.append({
            "id":aviao[0],
            "icao24": aviao[1],
            "callsign": aviao[2],
            "origin_country": aviao[3], 
            "time_position": aviao[4],
            "last_contact": aviao[5],
            "longitude": aviao[6],
            "latitude": aviao[7],
            "baro_altitude": aviao[8],
            "on_ground": aviao[9],
            "true_track": aviao[10],
            "vertical_rate": aviao[11]
        })

    return render_template('index.html', avioes=jsonAvioes)

@app.route('/dados_avioes')
def dados_avioes():
    # Attempt to retrieve data from the API
    api_data = get_data_from_api()

    if api_data != []:
        # Use data from the API
        planes = api_data
    else:
         # Connect to the SQLite database
        conn = sqlite3.connect("opensky_states.db")
        cursor = conn.cursor()

        # Fetch the plane data from the database
        cursor.execute("SELECT * FROM flights")
        planes = cursor.fetchall()

        # Close the connection
        conn.close()

        # Render the template with plane data

        return render_template("index.html", planes=planes)

    # Check if avioes is None or an empty list
    if planes:
        # Convert the results to a format that can be jsonify
        planes_data = [{'id': plane.id, 'latitude': plane.latitude, 'longitude': plane.longitude} for plane in planes]
    else:
        planes_data = []

    return jsonify(planes_data)

if __name__ == '__main__':
    app.run(debug=True)
