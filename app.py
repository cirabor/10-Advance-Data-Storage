import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, render_template, redirect, jsonify
#from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite",echo=False)

# Declare a Base using `automap_base()`
Base = automap_base()

# Reflect Database into ORM classes
Base.prepare(engine, reflect=True)

#view all the classes
Base.classes.keys()

# Save a reference to the measurenment table as 'Measurement'
Measurement = Base.classes.measurement

# Save a reference to the station table as 'Station'
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)


# Flask Routes

@app.route("/")
def welcome():
    return (
        "<h1>Hawaii Precipitation and Weather Data</h1>"
        "<h3>Pick from the available routes below:</h3>"
        "Precipiation from 2016-08-23 to 2017-08-23.<br/>"
        "/api/v1.0/precipitation<br/><br/>"
        "A list of all the weather stations in Hawaii.<br/>"
        "/api/v1.0/stations<br/><br/>"
        "The Temperature Observations (tobs) from 2016-08-23 to 2017-08-23.<br/>"
        "/api/v1.0/tobs<br/><br/>"
        "Type in a single date (i.e., 2015-01-01) to see the min, max and avg temperature since that date.<br/>"
        "/api/v1.0/temp/start<br/><br/>"
        "Type in a date range (i.e., 2015-01-01/2015-01-10) to see the min, max and avg temperature for that range.<br/>"
        "/api/v1.0/temp/start/end<br/>"
    )

dateprevyr = dt.date(2017, 8, 23) - dt.timedelta(days=365)
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query for the dates and temperature observations from the last year.
    Convert the query results to a Dictionary using date as the 'key 'and 'tobs' as the value."""


    # Retrieve the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date > dateprevyr).\
                        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of for the precipitation data
    precipitation_data = []
    for prcp_data in results:
        prcp_data_dict = {}
        prcp_data_dict["Date"] = prcp_data.date
        prcp_data_dict["Precipitation"] = prcp_data.prcp
        precipitation_data.append(prcp_data_dict)
        

    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def station():
    """Return a json list of stations from the dataset."""
    # Query all the stations
    results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list of all_stations.
    all_station = []
    for station in results:
        station_dict = {}
        station_dict["Station"] = station.station
        station_dict["Station Name"] = station.name
        station_dict["Latitude"] = station.latitude
        station_dict["Longitude"] = station.longitude
        station_dict["Elevation"] = station.elevation
        all_station.append(station_dict)
    
    return jsonify(all_station)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    # Query all the stations and for the given date. 
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
                    group_by(Measurement.date).\
                    filter(Measurement.date > dateprevyr).\
                    order_by(Measurement.station).all()
                    
    # Create a dictionary from the row data and append to a list of for the temperature data.
    temp_data = []
    for tobs_data in results:
        tobs_data_dict = {}
        tobs_data_dict["Station"] = tobs_data.station
        tobs_data_dict["Date"] = tobs_data.date
        tobs_data_dict["Temperature"] = tobs_data.tobs
        temp_data.append(tobs_data_dict)
    
    return jsonify(temp_data)
    
@app.route("/api/v1.0/temp/start")
def start_stats(start=None):
    """Return a json list of the minimum temperature, the average temperature, and the
    max temperature for a given start date"""
    # Query all the stations and for the given date. 
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= "2016-06-23").filter(Measurement.date <="2017-08-23").all()

    # Create a dictionary from the row data and append to a list of the temperature data.
    temp_stats = []
    
    for Tmin, Tmax, Tavg in results:
        temp_stats_dict = {}
        temp_stats_dict["Minimum Temp"] = Tmin
        temp_stats_dict["Maximum Temp"] = Tmax
        temp_stats_dict["Average Temp"] = Tavg
        temp_stats.append(temp_stats_dict)
    
    return jsonify(temp_stats)
    

@app.route("/api/v1.0/temp/<start>/<end>")
def calc_temps(start = None, end= None):
    """Return a json list of the minimum temperature, the average temperature, 
    and the max temperature for a given start-end date range."""
    
    # Query all the stations and for the given range of dates. 
   
    returns = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

        # Create a dictionary from the row data and append to a list of for the temperature data.
    begin_end_temps = []
    
    for Tmin, Tmax, Tavg in returns:
        begin_end_temps_dict = {}
        begin_end_temps_dict["Minimum Temp"] = Tmin
        begin_end_temps_dict["Maximum Temp"] = Tmax
        begin_end_temps_dict["Average Temp"] = Tavg
        begin_end_temps.append(begin_end_temps_dict)
    
    return jsonify(begin_end_temps)

if __name__ == '__main__':
    app.run(debug=True)