# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def homepage():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/2016-8-23<br/>"
        f"/api/v1.0/start/2016-8-23/end/2017-8-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Convert the query results from your precipitation analysis
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= query_date).\
    order_by(measurement.date).all()
    
    # Create a dictionary from the query results
    precipitation_data_dict = {}
    for date, precipitation in results:
        if precipitation is not None:
            precipitation_data_dict[date] = precipitation

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_data_dict)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    station_name = list(np.ravel(results))

    # Return a JSON list of stations from the dataset.
    return jsonify(station_name)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most-active station for the previous year of data.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_station_results = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= query_date).\
    filter(measurement.station == 'USC00519281').\
    order_by(measurement.date).all()

    # Create a list of dictionaries to jsonify the temperature observations
    tobs_data = {}
    for date, tobs in active_station_results:
        if tobs is not None:
            tobs_data[date] = tobs

    # Return a JSON list of temperature observations for the previous year.    
    return jsonify(tobs_data)

@app.route('/api/v1.0/start/<start>')
def start(start):
    start = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp_stats = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    temp_stats_result = session.query(*temp_stats).\
        filter(measurement.date >= start).all()

    # Format the result as a dictionary
    temp_stats_dict = {
    "Start Date": start,
    "TMIN": temp_stats_result[0][0],
    "TMAX": temp_stats_result[0][1],
    "TAVG": temp_stats_result[0][2]
    }

    return jsonify(temp_stats_dict)

@app.route('/api/v1.0/start/<start>/end/<end>')
def date_range(start, end):
    start = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    end_eq = session.query(measurement.date).order_by(desc(measurement.date)).first()
    end_str = end_eq[0]
    end = dt.datetime.strptime(end_str, '%Y-%m-%d').date()
    temp_stats = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    temp_stats_result = session.query(*temp_stats).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    
    # Format the result as a dictionary
    temp_stats_dict = {
    "Start Date": start,
    "End Date": end,
    "TMIN": temp_stats_result[0][0],
    "TMAX": temp_stats_result[0][1],
    "TAVG": temp_stats_result[0][2]
    }

    return jsonify(temp_stats_dict)

# Close the session
session.close()

if __name__ == '__main__':
    app.run(debug=True)