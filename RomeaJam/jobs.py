from traffik import db, Jam, Alert, Segment, SegmentStatus, RoadStatus, RoadAverage
import credentials
import requests
import time

def get_traffic():
    """Returns traffic json with jams and alerts"""
    req = requests.get(credentials.API_request_url)
    return dict(req.json())

def parse_traffik():
    """Create and store traffik objects to the database"""
    now = int(time.time())
    # request traffic from API
    traffic = get_traffic()
    # Create and commit jams
    if traffic['jams']:
        for i in traffic['jams']:
            db.session.add(Jam(i['startLongitude'], i['endLongitude'],
                               i['startLatitude'],  i['endLatitude'],
                               i['street'], i['severity'] + 1,
                               i['type'], i['delayInSec'], 'w', now))
            db.session.commit()
    # Create and commit alerts
    if traffic['alerts']:
        for i in traffic['alerts']:
            db.session.add(Alert(i['latitude'], i['longitude'], i['numOfThumbsUp'],
                           i['type'], i['subType'], 'w', now))
            db.session.commit()
    # Create and commit segments status
    for segment in db.session.query(Segment):
        segment_status = SegmentStatus(now,segment)
        db.session.add(segment_status)
        db.session.commit()
    # Create and commit road status
    rs1 = RoadStatus(now, 'Arrive', 3)
    rs2 = RoadStatus(now, 'Leave', 3)
    db.session.add(rs1)
    db.session.add(rs2)
    db.session.commit()
    # Create and commit road averages used for trends
    ra1 = RoadAverage(now, (now - 5 * 60), now, 'Arrive', '5min')
    ra2 = RoadAverage(now, (now - 30 * 60), (now - 5 * 60), 'Arrive', '30min')
    db.session.add(ra1)
    db.session.add(ra2)
    db.session.commit()

if __name__ == "__main__":
    parse_traffik()
