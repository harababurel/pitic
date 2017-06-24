from random import choice
from config import config
from exceptions import *

import validators


class Util:

    def __init__(self, repo):
        self.repo = repo

    def generate_random_string(self, size):
        return ''.join([choice(config['alphabet']) for _ in range(size)])

    def generate_short_url(self):
        short_url = None
        current_size = config['short_url_size']
        attempts = 0

        while short_url is None or \
                self.repo.shortenings_exist(short_url=short_url):
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
