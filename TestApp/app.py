from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///opensky_states.db'
db = SQLAlchemy(app)

class Aviao(db.Model):
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

# Move the create_all() inside the app context, and drop existing tables first
with app.app_context():
    db.drop_all()
    db.create_all()

@app.route('/')
def index():
    # Attempt to retrieve data from the API
    api_data = get_data_from_api()

    if api_data != []:
        # Use data from the API
        avioes = api_data
    else:
        # Use data from the database
        avioes = Aviao.query.all()

    return render_template('index.html', avioes=avioes)

@app.route('/dados_avioes')
def dados_avioes():
    # Attempt to retrieve data from the API
    api_data = get_data_from_api()

    if api_data != []:
        # Use data from the API
        avioes = api_data
    else:
        # Use data from the database
        avioes = Aviao.query.all()

    # Check if avioes is None or an empty list
    if avioes:
        # Convert the results to a format that can be jsonify
        avioes_data = [{'id': aviao.id, 'latitude': aviao.latitude, 'longitude': aviao.longitude} for aviao in avioes]
    else:
        avioes_data = []

    return jsonify(avioes_data)

if __name__ == '__main__':
    app.run(debug=True)
