# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, null
from datetime import datetime
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>  Enter a start date in the yyyy-mm-dd format.<br/>"
        f"/api/v1.0/<start>/<end>   Enter a start date after v1.0/ and an end date after the last / in the yyyy-mm-dd format.  Ensure your end date is after your start date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    year_precip = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > '2016-08-23').all()
    session.close()
    precipitation = []
    for date, prcp in year_precip:
        precip_dict = {}
        precip_dict[date] = prcp
        precipitation.append(precip_dict)
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(station))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temp():
    session = Session(engine)
    year_temp = session.query(Measurement.date, Measurement.tobs). \
        filter(Measurement.date > '2016-08-23').\
        filter(Measurement.station == "USC00519281").all()
    session.close()
    temperature = []
    for date, tobs in year_temp:
        temp_dict = {}
        temp_dict[date] = tobs
        temperature.append(temp_dict)
    return jsonify(temperature)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    date = start
    exists = session.query(Measurement.date).\
        filter(Measurement.date == date).first() is not None
    if exists is False:
        return jsonify({"error": "Date not found. Please ensure you have entered your date in the yyyy-mm-dd format"}), 404
        session.close()
    else:
        sel = [func.min(Measurement.tobs),
            func.max(Measurement.tobs),
            func.avg(Measurement.tobs)]
        temp_stats = session.query(*sel). \
            filter(Measurement.date > date).all()
        temperature_stats = list(np.ravel(temp_stats))
        return jsonify(temperature_stats)
    session.close()


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    start_date = start
    end_date = end
    exists_1 = session.query(Measurement.date).\
        filter(Measurement.date == start_date).first() is not None
    exists_2 = session.query(Measurement.date).\
        filter(Measurement.date == end_date).first() is not None
    if exists_1 is False:
        return jsonify({"error": "Start date not found.  Please ensure you have entered your start date in the yyyy-mm-dd format"}), 404
        session.close()
    elif exists_2 is False:
        return jsonify({"error": "End date not found.  Please ensure you have entered your end date in the yyyy-mm-dd format"}), 404
        session.close()
    else:
        sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]
        inclusive_start = datetime.strptime(start_date, "%Y-%m-%d") - dt.timedelta(days=1)
        inclusive_end = datetime.strptime(end_date, "%Y-%m-%d") + dt.timedelta(days=1)
        temp_stats_2 = session.query(*sel). \
            filter(Measurement.date.between(inclusive_start, inclusive_end)).all()
        temperature_stats_2 = list(np.ravel(temp_stats_2))
        return jsonify(temperature_stats_2)
    session.close()

if __name__ == "__main__":
    app.run(debug=True)