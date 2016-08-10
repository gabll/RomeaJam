import flask
from dbconnection import dbconnection
import credentials
import traffik
import coordinates

app = flask.Flask(__name__)

# Homepage
@app.route("/")
def homepage():
    """ serve the homepage """
    # find the last timestamp
    last_ts_qry = "SELECT timestamp FROM segments ORDER BY id DESC LIMIT 1;"
    conn = dbconnection(credentials.mysql_host,
                           credentials.mysql_user,
                           credentials.mysql_pwd,
                           credentials.mysql_db)
    last_ts = conn.execute_query(last_ts_qry).fetchone()['timestamp']
    conn.close()
    # Create RoadStatus Objects
    road_east = traffik.RoadStatus('East', last_ts)
    road_west = traffik.RoadStatus('West', last_ts)
    road_data = {'Arrive': road_east.__dict__, 'Leave': road_west.__dict__}
    return flask.render_template('index.html', road_data=road_data, coo=coordinates.road_segment_list)


# Debug mode for Flask
app.debug=True

# Start the server
app.run(host='0.0.0.0', port=5000)
