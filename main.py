#!/usr/bin/env python3
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import exists

from random import sample, choice
from string import ascii_lowercase, ascii_uppercase

app = Flask(__name__)
app.secret_key = "asdf"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://localhost/url-shortener"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SHORT_URL_SIZE'] = 6
app.config['ALPHABET'] = ascii_lowercase + ascii_uppercase + '0123456789'

db = SQLAlchemy(app)

from routes import *
from models import *

def generate_random_string(size):
    return ''.join([choice(app.config['ALPHABET']) for _ in range(size)])

def short_url_exists(short_url):
    return db.session.query(exists().where(ShortToLong.short_url == short_url)).scalar()

def long_url_exists(long_url):
    return db.session.query(exists().where(LongToShort.long_url == long_url)).scalar()

def get_short_url(long_url):
    return db.session.query(LongToShort).filter_by(long_url=long_url).first().short_url

def get_long_url(short_url):
    print("querying short url = <%s>" % short_url)
    return db.session.query(ShortToLong).filter_by(short_url=short_url).first().long_url

def get_all_entries():
    return db.session.query(LongToShort).all()

def generate_short_url(long_url):
    short_url = None

    print("Generated short URL: %s" % short_url)

    while short_url is None or short_url_exists(short_url):
        print("Short URL already exists. Generating a new one.")
        short_url = generate_random_string(app.config['SHORT_URL_SIZE'])

    return short_url

def shorten(long_url):
    try:
        short_url = generate_short_url(long_url)
        db.session.add(LongToShort(long_url, short_url))
        db.session.add(ShortToLong(short_url, long_url))
        db.session.commit()
    except Exception as e:
        print("could not shorten long_url = %s; reason: %s" % (long_url, e))

if __name__ == "__main__":
    app.run()
