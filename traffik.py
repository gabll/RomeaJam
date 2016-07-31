from dbconnection import dbconnection, sql_formatter
import credentials
from datetime import datetime

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

class SegmentStatus():

    def __init__(self, name, startLongitude, endLongitude, street, timestamp):
        self.name = name
        self.startLongitude = startLongitude
        self.endLongitude = endLongitude
        self.street = street
        self.timestamp = timestamp
        self.length = abs(endLongitude - startLongitude)
        if startLongitude < endLongitude:
            self.direction = 'East'
        else:
            self.direction = 'West'
        self.traffic_length_list = []
        self.severity_list = []
        self.color_list = []
        self.delayInSec_list = []
        self.packing_index = 0

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
                self.color_list.append(jam.color)
                self.delayInSec_list.append(jam.delayInSec)

    def update_packing_index(self, max_severity=4):
        """update the packing index given the jams inside the road segment"""
        weighted_traffic = sum([self.traffic_length_list[i] * self.severity_list[i]
                           for i in range(len(self.traffic_length_list))])
        self.packing_index += weighted_traffic / (self.length * max_severity)
        self.packing_index = round(self.packing_index, 4)

    def db_insert(self):
        """insert the road segment into segments table"""
        query = """INSERT INTO segments (name, startLongitude, endLongitude,
                   street, length, direction, traffic_length_list, severity_list,
                   delayInSec_list, packing_index, timestamp) VALUES ("""
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
                 "'" + sql_formatter(self.timestamp) + "');"
        conn = dbconnection(credentials.mysql_host,
                               credentials.mysql_user,
                               credentials.mysql_pwd,
                               credentials.mysql_db)
        conn.execute_query(query)
        conn.close()

if __name__ == "__main__":
    my_jam = Jam(1.123111, 3.45000, 3.456789, 2.345612, 'test_street',
                 9, 'hard', 247,'w',datetime.now())
    print my_jam.__dict__, '\n'
    my_alert = Alert(1.123111, 2.345612, 234, 'jam', 'small_jam', 'w',
                    datetime.now())
    print my_alert.__dict__, '\n'
    my_segment = SegmentStatus('segment_test', 12.270270, 12.211130, 'test_street',
                                datetime.now())
    print my_segment.__dict__, '\n'
    my_segment.add_jam(Jam(0, 12.266695, 0, 12.189606, 'test_street',
                            3, 'hard', 247,'w',datetime.now()))
    my_segment.update_packing_index()
    print my_segment.__dict__, '\n'
    # my_segment.add_jam(Jam(0, 12.210453, 0, 12.178143, 'test_street',
    #                         2, 'hard', 247,'w',datetime.now()))
    # my_segment.update_packing_index()
    # print my_segment.__dict__, '\n'
