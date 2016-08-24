from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from datetime import datetime
from config import Config
import logging

app = Flask(__name__)
app.config.from_object(Config())

db = SQLAlchemy(app)

chart_data = {'Arrive':[], 'Leave':[]}
today = datetime.now().strftime("%A")
label_graph = {i:'%s-%s' % (i,i+2) for i in range(0,24,2)}

# #logging.basicConfig()
# logger = logging.getLogger()
# logger.addHandler(logging.StreamHandler())

scheduler = APScheduler()
scheduler.init_app(app)

from RomeaJam import views
