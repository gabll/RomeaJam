from RomeaJam import app
from traffik import db, RoadStatus, Segment, SegmentStatus
import flask

@app.route('/')
@app.route('/index')
def homepage():
    """ serve the homepage """
    # find the last timestamp
    last_ts = db.session.query(RoadStatus).\
                         order_by(RoadStatus.id.desc()).limit(1).first().timestamp
    last_ts = 1470596452
    # find RoadStatus
    road_status = db.session.query(RoadStatus).\
                            filter(RoadStatus.timestamp==last_ts).all()
    road_status = {i.category:
                    {'packing_index': i.packing_index,
                    'traffic_alerts': i.traffic_alerts,
                    'accident_alerts': i.accident_alerts}
                  for i in road_status}
    # find SegmentStatus
    segment_status = db.session.query(SegmentStatus).join(Segment).\
                           filter(SegmentStatus.timestamp==last_ts).all()
    segment_status = [{'id': i.segment.id,
                        'category': i.segment.category,
                        'label': i.segment.label,
                        'packing_index': i.packing_index,
                        'traffic_alerts': i.traffic_alerts,
                        'accident_alerts': i.accident_alerts}
                     for i in segment_status]
    return flask.render_template('index.html',
                                road_status=road_status,
                                segment_status=segment_status)


#@app.errorhandler(404)
#def not_found(error):
#    return render_template('404.html'), 404
