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
        }
    ]
    SCHEDULER_VIEWS_ENABLED = True
