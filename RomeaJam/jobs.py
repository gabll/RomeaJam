from traffik import db, Jam, Alert, Segment, SegmentStatus, RoadStatus, RoadAverage
from RomeaJam import chart_data
from datetime import datetime
import pandas as pd
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
    raa1 = RoadAverage(now, (now - 5 * 60), now, 'Arrive', '5min')
    raa2 = RoadAverage(now, (now - 30 * 60), (now - 5 * 60), 'Arrive', '30min')
    db.session.add(raa1)
    db.session.add(raa2)
    ral1 = RoadAverage(now, (now - 5 * 60), now, 'Leave', '5min')
    ral2 = RoadAverage(now, (now - 30 * 60), (now - 5 * 60), 'Leave', '30min')
    db.session.add(ral1)
    db.session.add(ral2)
    db.session.commit()

def get_chart_data():
    now = datetime.fromtimestamp(time.time())
    label_dict = {i:'%s-%s' % (i,i+2) for i in range(0,24,2)}
    pd.options.mode.chained_assignment = None

    qs = db.session.query(RoadStatus).\
                 filter(RoadStatus.timestamp > datetime(now.year,now.month,now.day-22,0,0).strftime('%s')).\
                 filter(RoadStatus.timestamp <= now.strftime('%s'))
    df = pd.read_sql(qs.statement, qs.session.bind)
    df.set_index('id', inplace=True)
    df['datetime'] = pd.to_datetime(df['timestamp'],unit='s')

    df_a = df[df.category=="Arrive"]
    df_a['weekday'] = pd.DatetimeIndex(df_a.datetime).weekday
    df_a = df_a[df_a.weekday==now.weekday()]
    df_a['hour_interval'] = pd.DatetimeIndex(df_a.datetime).hour
    df_a['hour_interval'] = df_a['hour_interval'].apply(lambda x: int(x/2)*2).order(ascending=False)
    df_a = df_a.groupby(['hour_interval']).mean()
    df_a.reset_index(inplace=True)
    df_a['hour_interval'] = df_a['hour_interval'].apply(lambda x: label_dict[x])
    avg_a = [round(i,2) for i in df_a['packing_index']]

    df_l = df[df.category=="Leave"]
    df_l['weekday'] = pd.DatetimeIndex(df_l.datetime).weekday
    df_l = df_l[df_l.weekday==now.weekday()]
    df_l['hour_interval'] = pd.DatetimeIndex(df_l.datetime).hour
    df_l['hour_interval'] = df_l['hour_interval'].apply(lambda x: int(x/2)*2).order(ascending=False)
    df_l = df_l.groupby(['hour_interval']).mean()
    df_l.reset_index(inplace=True)
    df_l['hour_interval'] = df_l['hour_interval'].apply(lambda x: label_dict[x])
    avg_l = [round(i,2) for i in df_l['packing_index']]

    chart_data['Arrive'] = avg_a
    chart_data['Leave'] = avg_l
    chart_data['weekday_now'] = datetime.now().strftime("%A")
    print datetime.now(), 'chart updated!', chart_data

if __name__ == "__main__":
    parse_traffik()
    get_chart_data()
