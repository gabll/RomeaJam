from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from datetime import datetime
from config import Config
import logging
from logging.handlers import RotatingFileHandler

#flask app
app = Flask(__name__)
app.config.from_object(Config())

#SQLAlchemy db
db = SQLAlchemy(app)

#global variables
chart_data = {'Arrive':[],
              'Leave':[],
              'weekday_now':None,
              'graph_labels': range(0,26,2)}
from jobs import get_chart_data
get_chart_data()

#logging to file
if not app.debug:
    log = logging.getLogger('apscheduler.executors.default')
    file_handler = RotatingFileHandler('RomeaJam.log', 'a',
                                       1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    log.addHandler(file_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('RomeaJam startup')

#APScheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

#views
from RomeaJam import views
