#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

from random import sample, choice
from config import config

from repo import Repo
from util import Util
from singleton import Singleton
from models import Shortening, Hit, DBSession
from exceptions import *
import json


class RedirectResource(Resource):

    def get(self, short_url=None):
        repo = Pitic.Instance().repo

        try:
            shortening = repo.get_shortenings(short_url=short_url)[0]
        except IndexError:
            return '', 404

        repo.add(Hit(short_url, ip=get_remote_address()))
        return redirect(shortening.long_url, code=302)


class HitResource(Resource):

    def get(self, id=None):
        repo = Pitic.Instance().repo

        if id is None:
            return self.all_hits_response()

    def all_hits_response(self):
        return list(map(lambda x: x.encode(),
                        Pitic.Instance().repo.get_all(Hit)))


class ShorteningResource(Resource):

    def get(self, short_url=None):
        repo = Pitic.Instance().repo

        if short_url is None:
            return self.all_shortenings_response()

        try:
            shortening = repo.get_shortenings(short_url=short_url)[0]
            return shortening.encode()
        except IndexError:
            return self.create_error_response(
                ShorteningException("Short URL is not mapped to anything"))

    def post(self, **kwargs):
        repo = Pitic.Instance().repo
        req = dict([(x[0].strip(), x[1].strip())
                    for x in request.form.items()])

        print(req)

        try:
            self.validate_post_request(req)
        except Exception as e:
            return self.create_error_response(e)

        req['custom'] = req.get('custom') == 'true'

        if not req['custom']:
            try:
                shortening = repo.get_shortenings(
                    long_url=req['long_url'],
                    custom=False)[0]
                return shortening.encode()
            except:
                pass

        try:
            short_url = req['short_url'] if req['custom'] \
                else Pitic.Instance().util.generate_short_url()

            shortening = Shortening(
                long_url=req['long_url'],
                short_url=short_url,
                custom=req['custom'],
                ip=get_remote_address())

            repo.add(shortening)

            return repo.get_shortenings(short_url=short_url)[0].encode()
        except Exception as e:
            return self.create_error_response(e)

    def validate_post_request(self, req):
        required_keys = ['long_url']

        if 'custom' in req:
            if req['custom'] == 'true':
                required_keys.append('short_url')
            elif req['custom'] == 'false':
                pass
            else:
                raise InvalidRequestException(
                    "'custom' must be either 'true' or 'false'")

        for key in required_keys:
            if key not in req:
                raise InvalidRequestException(
                    '<%s> must be provided in the POST request' % key)

        for key in req:
            if key not in ['long_url', 'short_url', 'custom', 'ip',
                           'timestamp']:
                raise InvalidRequestException(
                    "Unrecognized request field: %s" % key)

        util = Pitic.Instance().util
        repo = Pitic.Instance().repo

        try:
            util.validate_long_url(req['long_url'])
        except LongURLException:
            req['long_url'] = "http://%s" % req['long_url']
        util.validate_long_url(req['long_url'])

        if req.get('custom') == 'true':
            util.validate_short_url(req['short_url'])

            if repo.shortenings_exist(short_url=req['short_url']):
                raise ShortURLException(
                    'Short URL <%s> is already mapped to something else.' %
                    req['short_url'])

    def all_shortenings_response(self):
        return list(map(lambda x: x.encode(),
                        Pitic.Instance().repo.get_all(Shortening)))

    @staticmethod
    def create_error_response(e):
        return {
            'error': str(type(e)),
            'message': str(e)
        }, 400


@Singleton
class Pitic(object):

    def __init__(self):
        self.app = Flask(__name__)
        self.load_config()

        # self.db = SQLAlchemy(self.app)
        # self.db_session = DBSession()

        self.repo = Repo(SQLAlchemy(self.app), DBSession())
        self.util = Util(self.repo)

        self.api = Api(self.app)
        self.add_api_resources()

    def load_config(self):
        self.app.secret_key = config['secret_key']

        for app_setting in config['app'].items():
            self.app.config[app_setting[0]] = app_setting[1]

    def add_api_resources(self):
        self.api.add_resource(RedirectResource, '/<short_url>')
        self.api.add_resource(ShorteningResource,
                              '/api/shortenings',
                              '/api/shortenings/',
                              '/api/shortenings/<short_url>')
        self.api.add_resource(HitResource,
                              '/api/hits',
                              '/api/hits/',
                              '/api/hits/<int:id>')

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
