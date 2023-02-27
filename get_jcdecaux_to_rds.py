import sqlalchemy as sqla
from sqlalchemy import create_engine
import traceback
import glob
import os
from pprint import pprint
import simplejson as json
import requests
from IPython.display import display
import time

URI = "dbbikes.cfjfzkae45jy.eu-west-1.rds.amazonaws.com"
PORT="3306"
DB="dbbikes"
USER="admin"
PASSWORD = "mypassword"

engine = create_engine("mysql+mysqldb://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB), echo=True)


sql = """
CREATE DATABASE IF NOT EXISTS dbbikes;
"""

engine.execute(sql)

sql = """
CREATE TABLE IF NOT EXISTS station (
address VARCHAR(256),
banking INTEGER,
bike_stands INTEGER,
bonus INTEGER,
contract_name VARCHAR(256),
name VARCHAR(256),
number INTEGER,
position_lat REAL,
position_lng REAL,
status VARCHAR(256)
)
"""

try:
    res = engine.execute("DROP TABLE IF EXISTS station")
    res = engine.execute(sql)
    print(res.fetchall())
except Exception as e:
    print(e)




sql = """
CREATE TABLE IF NOT EXISTS availability(
number INTEGER,
available_bikes INTEGER,
available_bike_stands INTEGER,
last_update INTEGER
)
"""

try:
    res = engine.execute("DROP TABLE IF EXISTS availability")
    res = engine.execute(sql)
    print(res.fetchall())
except Exception as e:
    print(e)

def station_to_db(text):
    stations = json.loads(text)
    print(type(stations), len(stations))
    for station in stations:
        print(station)
        vals = (station.get('address'),
                int(station.get('banking')),
                station.get('bike_stands'),
                int(station.get('bonus')),
                station.get('contract_name'),
                station.get('name'),
                station.get('number'),
                station.get('position').get('lat'),
                station.get('position').get('lng'),
                station.get('status'))
        engine.execute("insert into station values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", vals)
        break #Because of this break, the loop only inserts the first Station. Which is no.42.
    return

def availability_to_db(text):
    stations = json.loads(text)
    print(type(stations), len(stations))
    for station in stations:
        print(station)
        vals = (int(station.get('number')),
                int(station.get('available_bikes')),
                int(station.get('available_bike_stands')),
                int(station.get('last_update')))
        
        engine.execute("insert into availability values(%s,%s,%s,%s)", vals)
    return

def stations_fix_keys(station):
    station['position_lat'] = station['position']['lat']
    station['position_lng'] = station['position']['lng']
    return station




api_key = 'a471198f1d4a279171da8f17892b64eb12c32f33'
contract_name = 'dublin'
api_query = 'https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=a471198f1d4a279171da8f17892b64eb12c32f33'




def main():
    while True:
        
        global r
        try:
            r = requests.get('https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=a471198f1d4a279171da8f17892b64eb12c32f33')
            station_to_db(r.text)
            availability_to_db(r.text)
            stations = json.loads(r.text)
            # engine.execute(station.insert(), *map(stations_fix_keys, stations))

            time.sleep(5*60) #Scrape every 5 minutes
        except:
            print("Error. Something went wrong.") 
    
main()

