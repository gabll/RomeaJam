import coordinates
from traffik import Jam, Alert, SegmentStatus
import requests
from datetime import datetime
from safe_schedule import SafeScheduler
import time

def get_traffic():
    """Returns traffic json with jams and alerts"""
    req = requests.get(coordinates.API_request_url)
    return dict(req.json())

def job():
    """ Get jams and alerts from API, store them in database and compute
    packing index for each road segment"""
    now = datetime.now()
    jam_list = []
    # request traffic from API
    traffic = get_traffic()
    # store jams in the database; severity starts from 0
    if traffic['jams']:
        for i in traffic['jams']:
            jam = Jam(i['startLatitude'], i['startLongitude'], i['endLatitude'],
                      i['endLongitude'], i['street'], i['severity'] + 1,
                      i['type'], i['delayInSec'], 'w', now)
            jam_list.append(jam)
            try:
                jam.db_insert()
            except:
                print 'INSERT ERROR: ', i
    # store alerts in the database
    if traffic['alerts']:
        for i in traffic['alerts']:
            alert = Alert(i['latitude'], i['longitude'], i['numOfThumbsUp'],
                           i['type'], i['subType'], 'w', now)
            try:
                alert.db_insert()
            except:
                print 'INSERT ERROR: ', i
    # bin jams into road segments, store in database
    for i in coordinates.road_segment_list:
        segm = SegmentStatus(i['name'], i['start'], i['end'], i['street'], now)
        for jam in jam_list:
            segm.add_jam(jam)
        segm.update_packing_index()
        try:
            segm.db_insert()
        except:
            print 'INSERT ERROR: ', i

#job()

# Run the job
scheduler = SafeScheduler()
scheduler.every(1).minutes.do(job)
while 1:
    scheduler.run_pending()
    time.sleep(1)
