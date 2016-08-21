from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from config import Config
#import logging

app = Flask(__name__)
app.config.from_object(Config())

db = SQLAlchemy(app)

#logging.basicConfig()
scheduler = APScheduler()
scheduler.init_app(app)

from RomeaJam import views, traffik
