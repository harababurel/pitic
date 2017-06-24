from models import Shortening
from sqlalchemy import exists, and_
from random import choice
from config import config
from exceptions import *

import validators


class Util:

    def __init__(self, db_session):
        self.db_session = db_session

    def generate_random_string(self, size):
        return ''.join([choice(config['alphabet']) for _ in range(size)])

    # def short_url_exists(self, short_url):
    #     return self.db_session \
    #         .query(exists().where(Shortening.short_url == short_url)) \
    #         .scalar()

    # def long_url_exists(self, long_url):
    #     return self.db_session.query(exists().where(and_(
    #         Shortening.long_url == long_url,
    #         Shortening.custom == False))).scalar()

    # def get_short_url(self, long_url):
    #     return self.db_session.query(Shortening).filter(and_(
    #         Shortening.long_url == long_url,
    #         Shortening.custom == False)).first().short_url

    # def get_long_url(self, short_url):
    #     print("querying short url = <%s>" % short_url)
    #     return self.db_session \
    #         .query(Shortening) \
    #         .filter_by(short_url=short_url) \
    #         .first() \
    #         .long_url

    def get_shortening(self, *_,
                       long_url=None,
                       short_url=None,
                       custom=None):
        query = self.db_session.query(Shortening)

        if long_url is not None:
            query = query.filter_by(long_url=long_url)
        if short_url is not None:
            query = query.filter_by(short_url=short_url)
        if custom is not None:
            query = query.filter_by(custom=custom)

        return query.first()

    def shortening_exists(self, *_,
                          long_url=None,
                          short_url=None,
                          custom=None):
        shortening = self.get_shortening(
            long_url=long_url,
            short_url=short_url,
            custom=custom)

        return shortening is not None

    # def get_shortening(self, *_, long_url=None, short_url=None):
    #     results = self.db_session.query(Shortening)

    #     if long_url is not None:
    #         results = results.filter_by(long_url=long_url)

    #     if short_url is not None:
    #         results = results.filter_by(short_url=short_url)

    #     print("first result: %r" % results.first())

    #     return results.first()

    def get_all_shortenings(self):
        return self.db_session.query(Shortening).all()

    def get_number_of_shortenings(self):
        return self.db_session.query(Shortening).count()

    def generate_short_url(self):
        short_url = None
        current_size = config['short_url_size']
        attempts = 0

        while short_url is None or self.shortening_exists(short_url=short_url):
            short_url = self.generate_random_string(current_size)
            attempts += 1

            if attempts >= config['max_attempts_until_short_url_size_increases']:
                attempts = 0
                current_size += 1

        return short_url

    def validate_short_url(self, short_url):
        if not validators.between(
                len(short_url),
                min=config['min_short_url_size'],
                max=config['max_short_url_size']):
            raise ShortURLException(
                'Short URL must contain between %i and %i characters' %
                (config['min_short_url_size'],
                 config['max_short_url_size']))

        for x in short_url:
            if x not in config['alphabet']:
                raise ShortURLException(
                    'Short URL contains forbidden character: %s' % x)

    def validate_long_url(self, long_url):
        if not validators.url(long_url, public=True):
            raise LongURLException("Invalid URL: %s" % long_url)

    def add(self, obj):
        self.db_session.add(obj)
        self.db_session.commit()

    # def shorten(self, long_url, short_url=None):
    #     custom = True
    #     if short_url is None:
    #         short_url = generate_short_url()
    #         custom = False

    #     try:
    #         self.db_session.add(Shortening(
    #             long_url,
    #             short_url,
    #             custom=custom,
    #             ip=get_remote_address()))

    #         self.db_session.commit()
    #     except Exception as e:
    #         print("could not shorten long_url = %s; reason: %s" % (long_url, e))
