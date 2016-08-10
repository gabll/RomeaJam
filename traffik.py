from dbconnection import dbconnection, sql_formatter
import credentials
# from datetime import datetime
from time import time

class Jam():

    def __init__(self, startLatitude, startLongitude, endLatitude, endLongitude,
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

    def db_insert(self):
        """insert the jam into the jams table"""
        query = """INSERT INTO jams (startLatitude, startLongitude, endLatitude,
                   endLongitude, street, severity, color, delayInSec, source,
                   timestamp, direction) VALUES ("""
        query += "'" + sql_formatter(self.startLatitude) + "'," \
                 "'" + sql_formatter(self.startLongitude) + "'," \
                 "'" + sql_formatter(self.endLatitude) + "'," \
                 "'" + sql_formatter(self.endLongitude) + "'," \
                 "'" + sql_formatter(self.street) + "'," \
                 "'" + sql_formatter(self.severity) + "'," \
                 "'" + sql_formatter(self.color) + "'," \
                 "'" + sql_formatter(self.delayInSec) + "'," \
                 "'" + sql_formatter(self.source) + "'," \
                 "'" + sql_formatter(self.timestamp) + "'," \
                 "'" + sql_formatter(self.direction) + "');"
        conn = dbconnection(credentials.mysql_host,
                               credentials.mysql_user,
                               credentials.mysql_pwd,
                               credentials.mysql_db)
        conn.execute_query(query)
        conn.close()

def get_jam(timestamp):
    """returns a jam from the database given the timestamp"""
    pass

class Alert():

    def __init__(self, latitude, longitude, likes, category, subcategory,
                 source, timestamp):
        self.latitude = latitude
        self.longitude = longitude
        self.likes = likes
        self.category = category
        self.subcategory = subcategory
        self.source = source
        self.timestamp = timestamp

    def db_insert(self):
        """insert the alert into the jams table"""
        query = """INSERT INTO alerts (latitude, longitude, likes,
                   category, subcategory, source, timestamp) VALUES ("""
        query += "'" + sql_formatter(self.latitude) + "'," \
                 "'" + sql_formatter(self.longitude) + "'," \
                 "'" + sql_formatter(self.likes) + "'," \
                 "'" + sql_formatter(self.category) + "'," \
                 "'" + sql_formatter(self.subcategory) + "'," \
                 "'" + sql_formatter(self.source) + "'," \
                 "'" + sql_formatter(self.timestamp) + "');"
        conn = dbconnection(credentials.mysql_host,
                               credentials.mysql_user,
                               credentials.mysql_pwd,
                               credentials.mysql_db)
        conn.execute_query(query)
        conn.close()

def get_alerts(timestamp):
    """returns a list of alerts from the database given the timestamp"""
    result = []
    qry = ("SELECT * FROM alerts WHERE timestamp = " + str(timestamp) + ";")
    conn = dbconnection(credentials.mysql_host,
                           credentials.mysql_user,
                           credentials.mysql_pwd,
                           credentials.mysql_db)
    cursor = conn.execute_query(qry)
    for i in cursor.fetchall():
        result.append(Alert(i['latitude'], i['longitude'], i['likes'],
                            i['category'], i['subcategory'], i['source'],
                            i['timestamp']))
    conn.close()
    return result

class SegmentStatus():

    def __init__(self, name, startLongitude, endLongitude, street, timestamp,
                startLatitude, endLatitude, traffic_length_list=None,
                severity_list=None, delayInSec_list=None,
                accident_alerts=0, traffic_alerts=0, packing_index=0):
        self.name = name
        self.startLongitude = startLongitude
        self.endLongitude = endLongitude
        self.street = street
        self.timestamp = timestamp
        self.startLatitude = startLatitude
        self.endLatitude = endLatitude
        self.length = abs(endLongitude - startLongitude)
        if startLongitude < endLongitude:
            self.direction = 'East'
        else:
            self.direction = 'West'
        if traffic_length_list is None:
            self.traffic_length_list = []
        if severity_list is None:
            self.severity_list = []
        if delayInSec_list is None:
            self.delayInSec_list = []
        self.accident_alerts = accident_alerts
        self.traffic_alerts = traffic_alerts
        self.packing_index = packing_index

    def add_jam(self, jam):
        """adds a jam in the current road segment
        Compute traffic as a projection of the longitude"""
        #check if same street and direction
        if jam.street == self.street and jam.direction == self.direction:
            if (self.direction == 'West' and
            (float(jam.startLongitude) < self.startLongitude and float(jam.startLongitude) > self.endLongitude) or
            (float(jam.endLongitude) < self.startLongitude and float(jam.endLongitude) > self.endLongitude)
            ) or (self.direction == 'East' and
            (float(jam.startLongitude) > self.startLongitude and float(jam.startLongitude) < self.endLongitude) or
            (float(jam.endLongitude) > self.startLongitude and float(jam.endLongitude) < self.endLongitude)):
                #traffic length
                start = float(jam.startLongitude)
                end = float(jam.endLongitude)
                #override start and end if they are outside of the segment borders
                if self.direction == 'East':
                    if float(jam.startLongitude) <= self.startLongitude:
                        start = self.startLongitude
                    if float(jam.endLongitude) >= self.endLongitude:
                        end = self.endLongitude
                if self.direction == 'West':
                    if float(jam.startLongitude) >= self.startLongitude:
                        start = self.startLongitude
                    if float(jam.endLongitude) <= self.endLongitude:
                        end = self.endLongitude
                #add the jam to the segment
                self.traffic_length_list.append(round(abs(end-start),4))
                self.severity_list.append(jam.severity)
                self.delayInSec_list.append(jam.delayInSec)

    def update_packing_index(self, max_severity=4):
        """update the packing index given the jams inside the road segment"""
        weighted_traffic = sum([self.traffic_length_list[i] * self.severity_list[i]
                           for i in range(len(self.traffic_length_list))])
        self.packing_index += weighted_traffic / (self.length * max_severity)
        self.packing_index = round(self.packing_index, 4)

    def add_alert(self, alert):
        """adds an alert in the road segment if the alert is within the lat-long rectangle
        because there is no direction hint, it has to be invocked only after update_packing_index
        """
        if self.packing_index <> 0:
            if (float(alert.longitude) > min(self.startLongitude, self.endLongitude) and
                    float(alert.longitude) < max(self.startLongitude, self.endLongitude)):
                if (float(alert.latitude) > min(self.startLatitude, self.endLatitude) and
                        float(alert.latitude) < max(self.startLatitude, self.endLatitude)):
                    if alert.category == 'JAM':
                        # todo: weight by subcategory, thumbs_up
                        self.traffic_alerts += 1
                    if alert.category == 'ACCIDENT':
                        self.accident_alerts += 1

    def db_insert(self):
        """insert the road segment into segments table
        TODO: add latitude"""
        query = """INSERT INTO segments (name, startLongitude, endLongitude,
                   street, length, direction, traffic_length_list, severity_list,
                   delayInSec_list, packing_index, accident_alerts,
                   traffic_alerts, startLatitude, endLatitude, timestamp) VALUES ("""
        query += "'" + sql_formatter(self.name) + "'," \
                 "'" + sql_formatter(self.startLongitude) + "'," \
                 "'" + sql_formatter(self.endLongitude) + "'," \
                 "'" + sql_formatter(self.street) + "'," \
                 "'" + sql_formatter(self.length) + "'," \
                 "'" + sql_formatter(self.direction) + "'," \
                 "'" + sql_formatter(self.traffic_length_list) + "'," \
                 "'" + sql_formatter(self.severity_list) + "'," \
                 "'" + sql_formatter(self.delayInSec_list) + "'," \
                 "'" + sql_formatter(self.packing_index) + "'," \
                 "'" + sql_formatter(self.accident_alerts) + "'," \
                 "'" + sql_formatter(self.traffic_alerts) + "'," \
                 "'" + sql_formatter(self.startLatitude) + "'," \
                 "'" + sql_formatter(self.endLatitude) + "'," \
                 "'" + sql_formatter(self.timestamp) + "');"
        conn = dbconnection(credentials.mysql_host,
                               credentials.mysql_user,
                               credentials.mysql_pwd,
                               credentials.mysql_db)
        conn.execute_query(query)
        conn.close()

def get_segments(timestamp):
    """returns a list of segments from the database given the timestamp"""
    result = []
    qry = ("SELECT * FROM segments WHERE timestamp = " + str(timestamp) + ";")
    conn = dbconnection(credentials.mysql_host,
                           credentials.mysql_user,
                           credentials.mysql_pwd,
                           credentials.mysql_db)
    cursor = conn.execute_query(qry)
    for i in cursor.fetchall():
        result.append({'id': i['id'], 'segment': SegmentStatus(i['name'], i['startLongitude'], i['endLongitude'],
                   i['street'], i['timestamp'], i['startLatitude'],
                   i['endLatitude'], i['traffic_length_list'],
                   i['severity_list'], i['delayInSec_list'],
                   i['accident_alerts'], i['traffic_alerts'],
                   i['packing_index'])})
    conn.close()
    return result

class RoadStatus():

    def __init__(self, direction, timestamp):
        self.timestamp = timestamp
        self.direction = direction
        self.segment_list = []
        qry = ("SELECT * FROM segments"
               + " WHERE timestamp = " + str(self.timestamp)
               + " AND direction = '" + str(self.direction) + "';")
        conn = dbconnection(credentials.mysql_host,
                               credentials.mysql_user,
                               credentials.mysql_pwd,
                               credentials.mysql_db)
        cursor = conn.execute_query(qry)
        for i in cursor.fetchall():
            self.segment_list.append(SegmentStatus(i['name'], i['startLongitude'],
                i['endLongitude'], i['street'], i['timestamp'],
                i['startLatitude'], i['endLatitude'], i['traffic_length_list'],
                i['severity_list'], i['delayInSec_list'],
                i['accident_alerts'], i['traffic_alerts'], i['packing_index']))
        conn.close()
        if len(self.segment_list):
            self.packing_index = sum([i.packing_index for i in self.segment_list])/len(self.segment_list)
        else:
            self.packing_index = 0
        self.accident_alerts = sum([i.accident_alerts for i in self.segment_list])
        self.traffic_alerts = sum([i.traffic_alerts for i in self.segment_list])
        
if __name__ == "__main__":
    my_jam = Jam(1.123111, 3.45000, 3.456789, 2.345612, 'test_street',
                 9, 'hard', 247,'w',time())
    print my_jam.__dict__, '\n'
    my_alert = Alert(7.5, 12.22, 234, 'JAM', 'small_jam', 'w',
                    time())
    print my_alert.__dict__, '\n'
    my_segment = SegmentStatus('segment_test', 12.270270, 12.211130, 'test_street',
                                time(),7,8)
    print 'segment', my_segment.__dict__, '\n'
    my_segment.add_jam(Jam(0, 12.266695, 0, 12.189606, 'test_street',
                            3, 'hard', 247,'w',time()))
    my_segment.update_packing_index()
    my_segment.add_alert(my_alert)
    print 'segment', my_segment.__dict__, '\n'

    print [al.__dict__ for al in get_alerts(1470740573)], '\n'
    print [se['segment'].__dict__ for se in get_segments(1470083873)], '\n'

    my_road = RoadStatus('East', 1470683787)
    print my_road.__dict__, '\n'
