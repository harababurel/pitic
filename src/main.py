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

        if util.shortening_exists(short_url=short_url):
            return util.get_shortening(short_url=short_url).encode()
        else:
            return self.create_error_response(
                ShorteningException("Short URL is not mapped to anything"))

    def post(self, **kwargs):
        util = Pitic.Instance().util
        req = dict([(x[0].strip(), x[1].strip())
                    for x in request.form.items()])

        try:
            self.validate_post_request(req)
        except Exception as e:
            return self.create_error_response(e)

        req['custom'] = 'custom' in req.keys() and req['custom'] == 'true'

        if not req['custom'] and util.shortening_exists(
                long_url=req['long_url'],
                custom=False):
            return util.get_shortening(
                long_url=req['long_url'],
                custom=False).encode()

        try:
            if req['custom']:
                short_url = req['short_url']
            else:
                short_url = util.generate_short_url()

            shortening = Shortening(
                long_url=req['long_url'],
                short_url=short_url,
                custom=req['custom'],
                ip=get_remote_address())

            util.add_shortening(shortening)

            return util.get_shortening(short_url=short_url).encode()
        except Exception as e:
            return self.create_error_response(e)

    def validate_post_request(self, req):
        required_keys = ['long_url']

        if 'custom' in req.keys():
            if req['custom'] == 'true':
                required_keys.append('short_url')
            elif req['custom'] == 'false':
                pass
            else:
                raise InvalidRequestException(
                    "'custom' must be either 'true' or 'false'")

        for key in required_keys:
            if key not in req.keys():
                raise InvalidRequestException(
                    '<%s> must be provided in the POST request' % key)

        for key in req.keys():
            if key not in ['long_url', 'short_url', 'custom', 'ip',
                           'timestamp']:
                raise InvalidRequestException(
                    "Unrecognized request field: %s" % key)

        util = Pitic.Instance().util

        try:
            util.validate_long_url(req['long_url'])
        except LongURLException:
            req['long_url'] = "http://%s" % req['long_url']
        util.validate_long_url(req['long_url'])

        if 'custom' in req.keys() and req['custom'] == 'true':
            util.validate_short_url(req['short_url'])
            if util.shortening_exists(short_url=req['short_url']):
                raise ShortURLException(
                    'Short URL <%s> is already mapped to something else.' %
                    req['short_url'])

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
