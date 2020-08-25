import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Mesaurement = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    session = Session(engine)
    data_start = session.query(Mesaurement.date).order_by(Mesaurement.date).first()
    data_end = session.query(Mesaurement.date).order_by(Mesaurement.date.desc()).first()
    session.close()

    return (
        f"Welcome to the Homepage!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/REPLACE w/ START DATE<br/>"
        f"/api/v1.0/start_end/REPLACE w/ START DATE/REPLACE w/ END DATE<br/><br/>"
        f"This api has information between {data_start[0]} and {data_end[0]}.<br/>"
        f"Please use date structure: YYYY-MM-DD. For example: /api/v1.0/start/2013-05-06 or  /api/v1.0/start_end/2013-05-06/2014-05-05"

    )

@app.route("/api/v1.0/precipitation")
def percipitation():
    session = Session(engine)
    results = session.query(Mesaurement.date, Mesaurement.prcp).all()
    session.close

    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

        """List all available api routes."""
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    result = session.query(Station.name,Station.id,Station.elevation,Station.latitude,Station.station,Station.longitude).all()
    session.close()

    station_list = []
    for name, id, elevation, latitude, station, longitude in result:
        station_dict = {}
        station_dict["name"] = name
        station_dict["id"] = id
        station_dict["elevation"] = elevation
        station_dict["latitude"] = latitude
        station_dict["station"] = station
        station_dict["longitude"] = longitude
        station_list.append(station_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
        # Calculate the date 1 year ago from the last data point in the database
    session = Session(engine)
    d = session.query(func.strftime('%Y-%m-%d', Mesaurement.date, '-1 years')).order_by(Mesaurement.date.desc()).all()
    session.close()
    s = [items[0] for items in d]

    sel = [Mesaurement.station,
       func.count(Mesaurement.station)] 

    session = Session(engine)   
    q = session.query(*sel).group_by(Mesaurement.station).order_by(func.count(Mesaurement.station).desc()).all()
    session.close()

    stat = [item[0] for item in q]

    # Perform a query to retrieve the data and precipitation scores
    session = Session(engine)
    data = session.query(Mesaurement.date, Mesaurement.tobs).\
        filter(Mesaurement.station == stat[0]).\
        filter(Mesaurement.date >= s[0]).\
        order_by(Mesaurement.date).all()
    session.close()

    tobs_list = []
    for date, tobs in data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

        """List all available api routes."""
    return jsonify(tobs_list)

@app.route("/api/v1.0/start/<start>")
def start_date(start):
    try:
        clean_start = start.replace(" ", "")

        session = Session(engine)
        min = session.query(func.min(Mesaurement.tobs)).filter(Mesaurement.date >= str(clean_start)).first()
        max= session.query(func.max(Mesaurement.tobs)).filter(Mesaurement.date >= str(clean_start)).first()
        avg = session.query(func.avg(Mesaurement.tobs)).filter(Mesaurement.date >= str(clean_start)).first()
        session.close()

        l = []
        d = {
            "start date":clean_start,
            "min": min,
            "max": max,
            "avg":avg
        }
        l.append(d)
        return jsonify(l)

    except:
        return jsonify({"error": f"The date you provided {clean_start} can not be found."}), 404

@app.route("/api/v1.0/start_end/<start>/<end>")
def start_end(start, end):

    try:
        clean_start = start.replace(" ", "")
        clean_end = end.replace(" ", "")

        session = Session(engine)
        min = session.query(func.min(Mesaurement.tobs))\
            .filter((Mesaurement.date >= str(clean_start))&(Mesaurement.date <= str(clean_end))).first()
        max= session.query(func.max(Mesaurement.tobs))\
            .filter((Mesaurement.date >= str(clean_start))&(Mesaurement.date <= str(clean_end))).first()
        avg = session.query(func.avg(Mesaurement.tobs))\
            .filter((Mesaurement.date >= str(clean_start))&(Mesaurement.date <= str(clean_end))).first()
        session.close()

        l = []
        d = {
            "start date":clean_start,
            "end date":clean_end,
            "min": min,
            "max": max,
            "avg":avg
        }
        l.append(d)
        return jsonify(l)

    except:
        return jsonify({"error": f"There is an error. Please Try again"}), 404


if __name__ == '__main__':
    app.run(debug=True)

