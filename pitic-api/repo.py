from models import Shortening, User
from sqlalchemy import exists, and_
from config import config
from exceptions import *


class Repo:

    def __init__(self, db, db_session):
        self.db = db
        self.db_session = db_session

    def get_shortenings(self, *_,
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

        return query.all()

    def get_users(self, *_, email=None):
        query = self.db_session.query(User)
        if email is not None:
            query = query.filter_by(email=email)

        return query.all()

    def shortenings_exist(self, *_,
                          long_url=None,
                          short_url=None,
                          custom=None):
        shortenings = self.get_shortenings(
            long_url=long_url,
            short_url=short_url,
            custom=custom)

        return len(shortenings) > 0

    def users_exist(self, *_, email=None):
        users = self.get_users(email=email)
        return len(users) > 0

    def get_all(self, cls):
        return self.db_session.query(cls).all()

    def get_number_of(self, cls):
        return self.db_session.query(cls).count()

    def add(self, obj):
        self.db_session.add(obj)
        self.db_session.commit()

    # def access_token_is_admin(self, access_token):
    #     return self.db_session.query(AccessToken).filter(
    #         AccessToken.token == access_token,
    #         AccessToken.admin == True).first() is not None
