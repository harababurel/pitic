#!/usr/bin/env python3
from flask import Flask, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy


from random import sample, choice
from config import config

from util import Util
from singleton import Singleton
from models import Shortening, DBSession


class ShorteningResource(Resource):
    def get(self, short_url):
        # return {'long_url': 'http://google.com'}
        return self.retrieve(short_url)

    def retrieve(self, short_url):
        if short_url is None or short_url == 'favicon.ico':
            return {'long_url': None}

        util = Pitic.Instance().util

        if util.short_url_exists(short_url):
            shortening = util.get_shortening(short_url=short_url)
            # shortening += 1
            return str(shortening)
        else:
            return  {'long_url': None}

@Singleton
class Pitic(object):

    def __init__(self):
        self.app = Flask(__name__)
        self.load_config()

        self.db = SQLAlchemy(self.app)
        self.db_session = DBSession()

        self.util = Util(self.db_session)

        self.api = Api(self.app)
        self.add_api_resources()

    def load_config(self):
        self.app.secret_key = config['secret_key']

        for app_setting in config['app'].items():
            self.app.config[app_setting[0]] = app_setting[1]

    def add_api_resources(self):
        self.api.add_resource(ShorteningResource, '/api/<short_url>')

    def run(self):
        self.app.run()

# limiter = Limiter(
#     app,
#     key_func=get_remote_address,
#     default_limits=["10 per second", "100 per minute"]
# )
if __name__ == "__main__":
    pitic = Pitic.Instance()
    # try:
    #     print("Creating database.")
    #     pitic.create_db()
    #     print("Database created.")
    # except Exception as e:
    #     print("Did not create database. Reason:\n%s" % e)
    #     exit(1)
    try:
        pitic.run()
    except Exception as e:
        print("Could not run app. Reason:\n%s" % e)
