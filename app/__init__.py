# -*- coding: utf-8 -*-
from flask import Flask
from flask_mail import Mail
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from help_functions import *

app = Flask(__name__)

app.config.from_pyfile('config.py')

mail = Mail(app)

mongo = PyMongo(app)

bootstrap = Bootstrap(app)

socketio = SocketIO(app)

from app import views