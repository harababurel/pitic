#!/usr/bin/env python3
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import exists, and_
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
    return db.session.query(exists().where(and_(
        Shortening.long_url == long_url,
        Shortening.custom == False))).scalar()


def get_short_url(long_url):
    return db.session.query(Shortening).filter(and_(
        Shortening.long_url == long_url,
        Shortening.custom == False)).first().short_url


def get_long_url(short_url):
    print("querying short url = <%s>" % short_url)
    return db.session.query(Shortening).filter_by(short_url=short_url).first().long_url


def get_shortening(long_url=None, short_url=None):
    results = db.session.query(Shortening)

    if long_url is not None:
        results = results.filter_by(long_url=long_url)

    if short_url is not None:
        results = results.filter_by(short_url=short_url)

    print("first result: %r" % results.first())

    return results.first()


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


def validate_short_url(short_url):
    if len(short_url) < config['min_short_url_size'] or \
       len(short_url) > config['max_short_url_size']:
        return False

    for x in short_url:
        if x not in config['alphabet']:
            return False



    return True


def shorten(long_url, short_url=None):
    custom = True
    if short_url is None:
        short_url = generate_short_url(long_url)
        custom = False

    try:
        db.session.add(Shortening(
            long_url,
            short_url,
            custom=custom,
            ip=get_remote_address()))

        db.session.commit()
    except Exception as e:
        print("could not shorten long_url = %s; reason: %s" % (long_url, e))

if __name__ == "__main__":
    try:
        print("Creating database.")
        db.create_all()
        print("Database created.")
    except Exception as e:
        print("Did not create database. Reason:\n%s" % e)
        exit(1)

    try:
        app.run()
    except Exception as e:
        print("Could not run app. Reason:\n%s" % e)
