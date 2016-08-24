from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from datetime import datetime
from config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config())

db = SQLAlchemy(app)

chart_data = {'Arrive':[],
              'Leave':[],
              'weekday_now':None,
              'graph_labels': range(0,26,2)}
from jobs import get_chart_data
get_chart_data()

# logger = logging.getLogger()
# logger.addHandler(logging.StreamHandler())

scheduler = APScheduler()
scheduler.init_app(app)

from RomeaJam import views
