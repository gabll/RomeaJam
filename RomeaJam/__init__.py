from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import credentials

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = credentials.mysql_engine_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)

import RomeaJam.views
