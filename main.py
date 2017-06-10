#!/usr/bin/env python3
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import exists
from random import sample, choice
from config import config

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = config['secret_key']

for app_setting in config['app'].items():
    app.config[app_setting[0]] = app_setting[1]

db = SQLAlchemy(app)

from routes import *
from models import *

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per second", "100 per minute"]
)

def generate_random_string(size):
    return ''.join([choice(config['alphabet']) for _ in range(size)])


def short_url_exists(short_url):
    return db.session.query(exists().where(Shortening.short_url == short_url)).scalar()


def long_url_exists(long_url):
    return db.session.query(exists().where(Shortening.long_url == long_url)).scalar()


def get_short_url(long_url):
    return db.session.query(Shortening).filter_by(long_url=long_url).first().short_url


def get_long_url(short_url):
    print("querying short url = <%s>" % short_url)
    return db.session.query(Shortening).filter_by(short_url=short_url).first().long_url


def get_all_shortenings():
    return db.session.query(Shortening).all()


def get_number_of_shortenings():
    return db.session.query(Shortening).count()


def generate_short_url(long_url):
    short_url = None
    current_size = config['short_url_size']
    attempts = 0

    while short_url is None or short_url_exists(short_url):
        short_url = generate_random_string(current_size)
        attempts += 1

        if attempts >= config['max_attempts_until_short_url_size_increases']:
            attempts = 0
            current_size += 1

    return short_url


def shorten(long_url):
    try:
        short_url = generate_short_url(long_url)
        db.session.add(Shortening(long_url, short_url, ip=get_remote_address()))
        db.session.commit()
    except Exception as e:
        print("could not shorten long_url = %s; reason: %s" % (long_url, e))

if __name__ == "__main__":
    try:
        db.create_all()
        print("Created database.")
    except:
        print("Database exists. No need to create it.")

    app.run()
