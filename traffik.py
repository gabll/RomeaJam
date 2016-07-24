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
            self.direction = 'West'
        else:
            self.direction = 'East'

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

if __name__ == "__main__":
    my_jam = Jam(1.123111, 2.345612, 3.45678999, 4.567893923, 'test_street',
                 9, 'hard', 247,'w',datetime.now())
    print my_jam
    my_alert = Alert(1.123111, 2.345612, 234, 'jam', 'small_jam', 'w',
                    datetime.now())
    print my_alert
    my_alert.db_insert()
