from flask import Flask, render_template, jsonify, request
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

    # Retrieve filter values from request parameters
    on_ground_filter = request.args.get('on_ground_filter', 'all')
    country_filter = request.args.get('country_filter', 'all')


     # Connect to the SQLite database
    conn = sqlite3.connect('opensky_states.db')
    cursor = conn.cursor()

    # Fetch the plane data from the database

    query = "SELECT * FROM flights WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
        
    #query = "SELECT * FROM flights WHERE 1"
    if on_ground_filter != 'all':
        query += f" AND on_ground = {1 if on_ground_filter == 'true' else 0}"
    if country_filter != 'all':
        query += f" AND origin_country = '{country_filter}'"

    cursor.execute(query)
    avioes = cursor.fetchall()

    cursor.execute('SELECT name FROM countries ORDER BY name')
    unique_countries = [row[0] for row in cursor.fetchall()]
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
            "velocity": aviao[10],
            "true_track": aviao[11],
            "vertical_rate": aviao[12],
            "geo_altitude": aviao[14]
        })

    return render_template('index.html', avioes=jsonAvioes, unique_countries = unique_countries)

@app.route('/dados_avioes')
def dados_avioes():

    # Retrieve filter values from request parameters
    on_ground_filter = request.args.get('on_ground_filter', 'all')
    country_filter = request.args.get('country_filter', 'all')

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
        query = "SELECT * FROM flights WHERE 1"

        if on_ground_filter != 'all':
            query += f" AND on_ground = {1 if on_ground_filter == 'true' else 0}"
        if country_filter != 'all':
            query += f" AND origin_country = '{country_filter}'"

        cursor.execute(query)
        planes = cursor.fetchall()

        cursor.execute('SELECT name FROM countries ORDER BY name')
        unique_countries = [row[0] for row in cursor.fetchall()]

        # Close the connection
        conn.close()

        # Render the template with plane data

        return render_template("index.html", planes=planes, unique_countries=unique_countries)

    # Check if avioes is None or an empty list
    if planes:
        # Convert the results to a format that can be jsonify
        planes_data = [{'id': plane.id, 'latitude': plane.latitude, 'longitude': plane.longitude} for plane in planes]
    else:
        planes_data = []

    return jsonify(planes_data)

if __name__ == '__main__':
    app.run(debug=True)
