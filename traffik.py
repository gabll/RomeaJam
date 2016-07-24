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

class Alert():

    def __init__(self, Latitude, Longitude, likes, category, subcategory,
                 source, timestamp):
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.likes = likes
        self.category = category
        self.subcategory = subcategory
        self.source = source
        self.timestamp = timestamp
