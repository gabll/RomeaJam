#quick fix importing module RomeaJam when executing __main__
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))

from RomeaJam import db
from sqlalchemy.orm import class_mapper

def _repr(self):
    """string representation of objects"""
    attrs = class_mapper(self.__class__).column_attrs
    return u"<{}({})>".format(
        self.__class__.__name__,
        ', '.join(
            '%s=%r' % (k.key, getattr(self, k.key))
            for k in sorted(attrs)
        )
    )
db.Model.__repr__ = _repr

class Jam(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    startLongitude = db.Column(db.Float)
    endLongitude = db.Column(db.Float)
    startLatitude = db.Column(db.Float)
    endLatitude = db.Column(db.Float)
    street = db.Column(db.String(50))
    severity = db.Column(db.SmallInteger)
    color = db.Column(db.String(50))
    delayInSec = db.Column(db.Integer)
    source = db.Column(db.String(5))
    timestamp = db.Column(db.Integer)
    direction = db.Column(db.String(5))

    def __init__(self, startLongitude, endLongitude, startLatitude, endLatitude,
                 street, severity, color, delayInSec, source, timestamp):
        self.delayInSec = delayInSec
        self.startLatitude = startLatitude
        self.startLongitude = startLongitude
        self.endLatitude = endLatitude
        self.endLongitude = endLongitude
        self.severity = severity
        self.street = street
        self.color = color
        self.source = source
        self.timestamp = timestamp
        if startLongitude < endLongitude:
            self.direction = 'East'
        else:
            self.direction = 'West'

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    likes = db.Column(db.SmallInteger)
    category = db.Column(db.String(50))
    subcategory = db.Column(db.String(50))
    source = db.Column(db.String(5))
    timestamp = db.Column(db.Integer)

    def __init__(self, latitude, longitude, likes, category, subcategory,
                 source, timestamp):
        self.latitude = latitude
        self.longitude = longitude
        self.likes = likes
        self.category = category
        self.subcategory = subcategory
        self.source = source
        self.timestamp = timestamp

class Segment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(200))
    startLongitude = db.Column(db.Float)
    endLongitude = db.Column(db.Float)
    startLatitude = db.Column(db.Float)
    endLatitude = db.Column(db.Float)
    street = db.Column(db.String(50))
    direction = db.Column(db.String(5))
    category = db.Column(db.String(25))
    length = db.Column(db.Float)
    statuses = db.relationship("SegmentStatus", backref="segment")

    def __init__(self, label, startLongitude, endLongitude,
                startLatitude, endLatitude, street, category):
        self.label = label
        self.startLongitude = startLongitude
        self.endLongitude = endLongitude
        self.startLatitude = startLatitude
        self.endLatitude = endLatitude
        self.street = street
        if startLongitude < endLongitude:
            self.direction = 'East'
        else:
            self.direction = 'West'
        self.category = category
        self.length = abs(endLongitude - startLongitude)

class SegmentStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    segment_id = db.Column(db.Integer, db.ForeignKey('segment.id'))
    road_status_id = db.Column(db.Integer, db.ForeignKey('road_status.id'))
    timestamp = db.Column(db.Integer)
    jams_list = db.Column(db.String(200))
    delayInSec = db.Column(db.Integer)
    accident_alerts = db.Column(db.Integer)
    traffic_alerts = db.Column(db.Integer)
    packing_index = db.Column(db.Float)

    def __init__(self, timestamp, segment, jams_list='', delayInSec=0,
                accident_alerts=0, traffic_alerts=0, packing_index=0):
        self.timestamp = timestamp
        self.segment = segment
        self.jams_list = jams_list
        self.delayInSec = delayInSec
        self.accident_alerts = accident_alerts
        self.traffic_alerts = traffic_alerts
        self.packing_index = packing_index
        #internal variables
        self.traffic_length_list = []
        self.severity_list = []
        for jam in db.session.query(Jam).filter(Jam.timestamp==self.timestamp):
            self._add_jam(jam)
        self._update_packing_index()
        for alert in db.session.query(Alert).filter(Alert.timestamp==self.timestamp):
            self._add_alert(alert)

    def _add_jam(self, jam):
        """adds a jam in the current road segment
        Compute traffic as a projection of the longitude"""
        #check if same street and direction
        if jam.street == self.segment.street and jam.direction == self.segment.direction:
            sj, ej = float(jam.startLongitude), float(jam.endLongitude)
            ss, es = self.segment.startLongitude, self.segment.endLongitude
            if (self.segment.direction == 'West' and
            (sj > ss and ej < ss) or (sj < ss and sj > es)
            ) or (self.segment.direction == 'East' and
            (sj < ss and ej > ss) or (sj > ss and es > sj)):
                #traffic length
                start = float(jam.startLongitude)
                end = float(jam.endLongitude)
                #override start and end if they are outside of the segment borders
                if self.segment.direction == 'East':
                    if float(jam.startLongitude) <= self.segment.startLongitude:
                        start = self.segment.startLongitude
                    if float(jam.endLongitude) >= self.segment.endLongitude:
                        end = self.segment.endLongitude
                if self.segment.direction == 'West':
                    if float(jam.startLongitude) >= self.segment.startLongitude:
                        start = self.segment.startLongitude
                    if float(jam.endLongitude) <= self.segment.endLongitude:
                        end = self.segment.endLongitude
                #add the jam to the segment
                self.traffic_length_list.append(round(abs(end-start),4))
                self.severity_list.append(jam.severity)
                self.jams_list += '{sev:' + str(jam.severity) + ', len:' + str(round(abs(end-start),4)) + '}, '
                self.delayInSec += int(jam.delayInSec * abs(end-start)/abs(jam.endLongitude-jam.startLongitude))

    def _update_packing_index(self, max_severity=4):
        """update the packing index given the jams inside the road segment"""
        self.packing_index = 0
        weighted_traffic = sum([self.traffic_length_list[i] * self.severity_list[i]
                           for i in range(len(self.traffic_length_list))])
        self.packing_index += weighted_traffic / (self.segment.length * max_severity)
        self.packing_index = round(self.packing_index, 4)

    def _add_alert(self, alert):
        """adds an alert in the road segment if the alert is within the lat-long rectangle
        because there is no direction hint, it has to be invocked only after update_packing_index
        """
        if self.packing_index <> 0:
            if (float(alert.longitude) > min(self.segment.startLongitude, self.segment.endLongitude) and
                    float(alert.longitude) < max(self.segment.startLongitude, self.segment.endLongitude)):
                if (float(alert.latitude) > min(self.segment.startLatitude, self.segment.endLatitude) and
                        float(alert.latitude) < max(self.segment.startLatitude, self.segment.endLatitude)):
                    if alert.category == 'JAM':
                        self.traffic_alerts += 1
                    if alert.category == 'ACCIDENT':
                        self.accident_alerts += 1

class RoadStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.Integer)
    category = db.Column(db.String(50))
    snake_effect = db.Column(db.SmallInteger)
    packing_index = db.Column(db.Float)
    accident_alerts = db.Column(db.Integer)
    traffic_alerts = db.Column(db.Integer)
    statuses = db.relationship("SegmentStatus", backref="road_status")

    def __init__(self, timestamp, category, snake_effect):
        self.timestamp = timestamp
        self.category = category
        self.snake_effect = snake_effect
        for status in db.session.query(SegmentStatus).join(Segment).\
                        filter(SegmentStatus.timestamp==self.timestamp).\
                        filter(Segment.category==self.category).\
                        order_by(SegmentStatus.packing_index.desc()):
            self.statuses.append(status)
        if len(self.statuses):
            self.packing_index = sum([i.packing_index for i in
                        self.statuses[:self.snake_effect]])/self.snake_effect
        else:
            self.packing_index = 0
        self.accident_alerts = sum([i.accident_alerts for i in self.statuses])
        self.traffic_alerts = sum([i.traffic_alerts for i in self.statuses])

class RoadAverage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.Integer)
    category = db.Column(db.String(50))
    average_id = db.Column(db.String(10))
    packing_index = db.Column(db.Float)
    accident_alerts = db.Column(db.Integer)
    traffic_alerts = db.Column(db.Integer)

    def __init__(self, timestamp, from_timestamp, to_timestamp, category, average_id):
        self.timestamp = timestamp
        self.from_timestamp = from_timestamp
        self.to_timestamp = to_timestamp
        self.category = category
        self.average_id = average_id
        road_list = db.session.query(RoadStatus).\
                        filter(RoadStatus.timestamp>self.from_timestamp).\
                        filter(RoadStatus.timestamp<=self.to_timestamp).\
                        filter(RoadStatus.category==self.category).all()
        if len(road_list):
            self.packing_index = sum([i.packing_index for i in road_list])/len(road_list)
            self.accident_alerts = sum([i.accident_alerts for i in road_list])/len(road_list)
            self.traffic_alerts = sum([i.traffic_alerts for i in road_list])/len(road_list)
        else:
            self.packing_index = 0
            self.accident_alerts = 0
            self.traffic_alerts = 0


if __name__ == "__main__":
    from time import time
    my_jam = Jam(12.266695, 12.189606, 0,0, 'test_street',
                            3, 'hard', 247,'w',int(time()))

    db.session.add(my_jam)

    my_alert = Alert(7.5, 12.22, 234, 'JAM', 'small_jam', 'w',
                    int(time()))
    db.session.add(my_alert)

    my_segment = Segment('segment_test', 12.270270, 12.211130, 7,8,
                        'test_street', 'arrive')
    db.session.add(my_segment)

    my_status = SegmentStatus(int(time()), my_segment)
    db.session.add(SegmentStatus(int(time()), my_segment))
    db.session.add(SegmentStatus(int(time()), my_segment))
    db.session.add(SegmentStatus(int(time()), my_segment))

    my_road = RoadStatus(int(time()), 'arrive', 1)
    db.session.add(my_status)

    db.session.commit()

    print 'jam', my_jam, '\n'
    print 'alert', my_alert, '\n'
    print 'segment', my_segment, '\n'
    print 'segment_status', my_status, '\n'
    print 'road_status', my_road, '\n'
