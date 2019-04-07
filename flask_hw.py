import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)
app = Flask(__name__)

@app.route("/")
def welcome():
    return(
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    precip_list = []
    for date, prcp in results:
        data_dic = {}
        data_dic["date"] = date
        data_dic["prcp"] = prcp
        precip_list.append(data_dic)
    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations():
    stations_q = session.query(Station.name).all()
    stations_list = list(np.ravel(stations_q))
    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastest_year = int(latest_date[0][0:4])
    latest_month = int(latest_date[0][5:7])
    latest_day = int(latest_date[0][8:10])
    start_date = dt.date(lastest_year, latest_month, latest_day) - dt.timedelta(days=365)
    one_year_dates = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > start_date).order_by(Measurement.date).all()

    date_temp_list = []
    for date, temp in one_year_dates:
        dt_dic = {}
        dt_dic["date"] = date
        dt_dic["temp"] = temp
        date_temp_list.append(dt_dic)
    
    return jsonify(date_temp_list)
    
@app.route('/api/v1.0/<start>')
def startfunc(start):
    start_year = int(start[0:4])
    start_month = int(start[5:7])
    start_day = int(start[8:10])
    start_date = dt.date(start_year, start_month, start_day)

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    start_info = session.query(*sel).filter(Measurement.date >= start_date).all()

    start_list = []
    for s_min, s_avg, s_max in start_info:
        dt_dic = {}
        dt_dic["Min"] = s_min
        dt_dic["Avg"] = s_avg
        dt_dic["Max"] = s_max
        start_list.append(dt_dic)
    
    return jsonify(start_list)

@app.route('/api/v1.0/<start>/<end>')
def rangeunc(start, end):
    start_year = int(start[0:4])
    start_month = int(start[5:7])
    start_day = int(start[8:10])
    start_date = dt.date(start_year, start_month, start_day)

    end_year = int(end[0:4])
    end_month = int(end[5:7])
    end_day = int(end[8:10])
    end_date = dt.date(end_year, end_month, end_day)


    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    range_info = session.query(*sel).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    range_list = []
    for s_min, s_avg, s_max in range_info:
        dt_dic = {}
        dt_dic["Min"] = s_min
        dt_dic["Avg"] = s_avg
        dt_dic["Max"] = s_max
        range_list.append(dt_dic)

    
    return jsonify({"Results": f"The temp norms between {str(start_date)}  and {str(end_date)} are {range_list}."})



if __name__ == '__main__':
    app.run(debug=True)