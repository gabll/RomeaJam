from RomeaJam import app, chart_data
from traffik import db, RoadStatus, Segment, SegmentStatus, RoadAverage
import flask
from flask_track_usage import TrackUsage
from flask_track_usage.storage.sql import SQLStorage

usage_storage = SQLStorage(db=db)
track = TrackUsage(app, usage_storage)

@track.include
@app.route('/')
@app.route('/index')
def homepage():
    """ serve the homepage """
    # find the last timestamp
    last_ts = db.session.query(RoadStatus).\
                         order_by(RoadStatus.id.desc()).limit(1).first().timestamp

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
    #Find RoadAverage
    raa = db.session.query(RoadAverage).\
                           filter(RoadAverage.timestamp==last_ts).\
                           filter(RoadAverage.category=='Arrive').all()
    raa = {i.average_id: i.packing_index for i in raa}
    if raa['30min']:
        raa = int((raa['5min']-raa['30min'])/raa['30min']*100)
    else:
        raa = raa['5min']*100
    ral = db.session.query(RoadAverage).\
                           filter(RoadAverage.timestamp==last_ts).\
                           filter(RoadAverage.category=='Leave').all()
    ral = {i.average_id: i.packing_index for i in ral}
    if ral['30min']:
        ral = int((ral['5min']-ral['30min'])/ral['30min']*100)
    else:
        ral = ral['5min']*100

    return flask.render_template('index.html',
                                road_status=road_status,
                                segment_status=segment_status,
                                road_average={'Arrive':raa, 'Leave':ral},
                                chart_data=chart_data)
