import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(autoload_with=engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """Available api routes for this module challenge."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>tobs</a><br/>"
        f"<a href='/api/v1.0/<start>'>start</a><br/>"
        f"<a href='/api/v1.0/<start>/<end>'>end</a>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
    query_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > '2016-09-01').\
        filter(Measurement.date < '2017-08-23').\
        order_by(Measurement.date).all()

    session.close()

    precipitation_data = {date: prcp for date, prcp in query_results}

    return jsonify(precipitation_data)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    #Return a JSON list of stations from the dataset.
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    list_stations = list(np.ravel(results))
    return jsonify(list_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    station_counts = session.query(Measurement.station,func.count(Measurement.station).label('observation_count')).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    session.close()

    all_stations = []
    for station in station_counts:
        station_dict = {}
        station_dict["station"] = station.station
        station_dict["observation_count"] = station.observation_count
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start=None, end=None):

    session = Session(engine)


    if not end:
        tobs_summary = session.query(
            func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)
            # Measurement.date <= end_date
        ).filter(Measurement.date >= start).all()
        session.close()

        temperatures = list(np.ravel(tobs_summary))

        return jsonify(temperatures)
    tobs_summary = session.query(
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
        # Measurement.date <= end_date
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temperatures = list(np.ravel(tobs_summary))

    return jsonify(temperatures)









if __name__ == '__main__':
     app.run(debug=True)
