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
from models import Shortening, ShorteningEncoder, DBSession
from exceptions import *
import json


class ShorteningResource(Resource):

    def get(self, short_url=None):
        util = Pitic.Instance().util

        if short_url is None:
            return list(map(lambda x: x.encode(), util.get_all_shortenings()))

        if util.short_url_exists(short_url=short_url):
            shortening = util.get_shortening(short_url=short_url)
            return shortening.encode()
        else:
            return self.create_error_response(
                    ShorteningException("Short URL is not mapped to anything"))

    def post(self, **kwargs):
        util = Pitic.Instance().util
        data = dict([(x[0].strip(), x[1].strip())
                     for x in request.form.items()])

        try:
            self.validate_post_request(data)
        except LongURLException:
            print("Invalid long URL; trying again with 'http://' prefix")
            data['long_url'] = 'http://%s' % data['long_url']

        try:
            self.validate_post_request(data)
        except Exception as e:
            return self.create_error_response(e)

        data['custom'] = 'custom' in data.keys() and data['custom'] == 'true'

        if not data['custom'] and util.long_url_exists(data['long_url']):
            print("pula")
            return util.get_shortening(long_url=data['long_url']).encode()

        try:
            if data['custom']:
                short_url = data['short_url']
            else:
                short_url = util.generate_short_url()

            shortening = Shortening(
                long_url=data['long_url'],
                short_url=short_url,
                custom=data['custom'] == True,
                ip=get_remote_address())

            util.add_shortening(shortening)

            return util.get_shortening(short_url=short_url).encode()
        except Exception as e:
            return self.create_error_response(e)

    def validate_post_request(self, data):
        required_keys = ['long_url']

        if 'custom' in data.keys():
            required_keys.append('short_url')

        for key in required_keys:
            if key not in data.keys():
                raise InvalidRequestException(
                    '<%s> must be provided in the POST request' % key)

        for key in data.keys():
            if key not in ['long_url', 'short_url', 'custom', 'ip',
                           'timestamp']:
                raise InvalidRequestException(
                    "Unrecognized request field: %s" % key)

        if 'custom' in data.keys() and data['custom'] not in ['true', 'false']:
            raise InvalidRequestException(
                "'custom' must be either 'true' or 'false'")

        util = Pitic.Instance().util

        util.validate_long_url(data['long_url'])
        if 'custom' in data.keys() and data['custom'] == 'true':
            util.validate_short_url(data['short_url'])
            if util.short_url_exists(data['short_url']):
                raise ShortURLException(
                    'Short URL <%s> is already mapped to something else.' %
                    data['short_url'])

    @staticmethod
    def create_error_response(e):
        return {'error': str(type(e)),
                'message': str(e)}, 400



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
        self.api.add_resource(ShorteningResource,
                              '/api/shortenings',
                              '/api/shortenings/',
                              '/api/shortenings/<short_url>')

    def run(self):
        self.app.run()


if __name__ == "__main__":
    pitic = Pitic.Instance()

    limiter = Limiter(
        pitic.app,
        key_func=get_remote_address,
        default_limits=config['default_limits'],
    )

    try:
        pitic.run()
    except Exception as e:
        print("Could not run app. Reason:\n%s" % e)
