from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from main import Flight  # Importe a classe Flight do seu arquivo main.py

app = Flask(__name__)

# Crie uma sessão no SQLAlchemy para interagir com o banco de dados
engine = create_engine("sqlite:///opensky_states.db")
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

@app.route('/')
def home():
    # Recupere todos os voos da base de dados
    flights = Session.query(Flight).all()

    # Passe os voos para o template
    return render_template('webapp.html', flights=flights)

if __name__ == '__main__':
    app.run(debug=True)
