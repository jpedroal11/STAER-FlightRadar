import requests
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import config
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

# Defina suas credenciais da API OpenSky
username = config.OPENSKY_USERNAME
password = config.OPENSKY_PASSWORD

# Crie uma sessão no SQLAlchemy para interagir com o banco de dados
Base = declarative_base()

class Flight(Base):
    __tablename__ = 'flights'
    id = Column(Integer, primary_key=True)
    icao24 = Column(String)
    callsign = Column(String)
    origin_country = Column(String)
    time_position = Column(Integer)
    last_contact = Column(Integer)
    latitude = Column(Float)    
    longitude = Column(Float) 


# Substitua "sqlite:///opensky_data.db" pelo seu banco de dados, se necessário
engine = create_engine("sqlite:///opensky_states.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def get_opensky_data():
    url = "https://opensky-network.org/api/states/all"
    auth = (username, password)
    response = requests.get(url, auth=auth)
    try:
        data = response.json()["states"]
    except KeyError:
        data = []
    return data


def save_to_database(data):
    for entry in data:
        flight = Flight(
            icao24=entry[0],
            callsign=entry[1],
            origin_country=entry[2],
            time_position=entry[3],
            last_contact=entry[4],
        )
        session.add(flight)
    session.commit()

def main():
    while True:
        opensky_data = get_opensky_data()
        save_to_database(opensky_data)
        time.sleep(60)  # Aguarde 60 segundos antes de obter dados novamente

if __name__ == "__main__":
    main()
