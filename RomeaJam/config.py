import credentials

class Config(object):
    #SQLAlchemy
    SQLALCHEMY_DATABASE_URI = credentials.mysql_engine_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    #APScheduler
    JOBS = [
        {
            'id': 'parse_traffik',
            'func': 'RomeaJam.jobs:parse_traffik',
            'trigger': 'interval',
            'seconds': 60
        },
        {
            'id': 'get_chart_data',
            'func': 'RomeaJam.jobs:get_chart_data',
            'trigger': 'cron',
            'hour': 0,
            'minute': 1
        }
    ]
    SCHEDULER_VIEWS_ENABLED = True

    #Track-Usage
    TRACK_USAGE_USE_FREEGEOIP = False
    TRACK_USAGE_INCLUDE_OR_EXCLUDE_VIEWS = 'include'
