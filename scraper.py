import credentials
from traffik import Jam, Alert
import requests
from datetime import datetime
from safe_schedule import SafeScheduler
import time

def get_traffic():
    """Returns traffic json with jams and alerts"""
    req = requests.get(credentials.api_url +
                     'latBottom=45.17965'+
                     '&lonLeft=12.13251'+
                     '&latTop=45.25266'+
                     '&lonRight=12.27744')
    return dict(req.json())

def job():
    """ """
    now = datetime.now()
    # request traffic from API
    traffic = get_traffic()
    # load jams in the database
    if traffic['jams']:
        for i in traffic['jams']:
            jam = Jam(i['startLatitude'], i['startLongitude'], i['endLatitude'],
                      i['endLongitude'], i['street'], i['severity'], i['type'],
                      i['delayInSec'], 'w', now)
            try:
                jam.db_insert()
            except:
                print 'INSERT ERROR: ', i
    #load alerts in the database
    if traffic['alerts']:
        for i in traffic['alerts']:
            alert = Alert(i['latitude'], i['longitude'], i['numOfThumbsUp'],
                           i['type'], i['subType'], 'w', now)
            try:
                alert.db_insert()
            except:
                print 'INSERT ERROR: ', i

# Run the job
scheduler = SafeScheduler()
scheduler.every(1).minutes.do(job)
while 1:
    scheduler.run_pending()
    time.sleep(1)
