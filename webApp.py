from flask import Flask, render_template
import sqlite3
from openksylib import OpenSkyApi

app = Flask(__name__)

@app.route('/')
def index():
    # Connect to the SQLite database
    conn = sqlite3.connect('opensky_states.db')
    cursor = conn.cursor()

    # Fetch the plane data from the database
    cursor.execute('SELECT * FROM flights')
    planes = cursor.fetchall()

    # Close the connection
    conn.close()

    # Render the template with plane data
    return render_template('index.html', planes=planes)

if __name__ == '_main_':
    app.run(debug=True)