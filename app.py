from os import getenv
from flask import Flask

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

from routes import login
from routes import news
from routes import notices
from routes import polls
from routes import feedback
from routes import manage_users
from routes import profile
