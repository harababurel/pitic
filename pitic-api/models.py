from flask_sqlalchemy import Model
from sqlalchemy import Column, String, Integer, DateTime, \
    Boolean, ForeignKey, create_engine
from datetime import date, datetime
from config import config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from passlib.apps import custom_app_context as pwd_context

from bson import json_util
import json
import hashlib


"""
Rules:

    There can be as many custom short URLs mapped to the same long URL,
    but only one non-custom (random) one.

    Custom shortenings are *hidden from sight*: retrieving the short URL
    mapped to a long URL should only return the non-custom one.

    During a "shorten" query, if all shortenings of a long URL are custom,
    than a new random one should be generated.
"""


Base = declarative_base()


class Encodable:

    def __str__(self):
        return str(self.encode())

    def encode(self):
        return json.loads(json.dumps(self, cls=Encoder))


class Encoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, (datetime, date)):
            ret = o.isoformat()
        else:
            ret = dict([x for x in o.__dict__.items()
                        if not x[0].startswith('_')])
        return ret


class Shortening(Base, Encodable):
    __tablename__ = 'shortenings'

    long_url = Column(String(2000), index=True)
    short_url = Column(String(32), primary_key=True)
    timestamp = Column(DateTime)
    ip = Column(String(45), index=True)
    custom = Column(Boolean)

    def __init__(self, *, long_url=None, short_url=None, timestamp=None,
                 ip=None, custom=False):

        if long_url is None or short_url is None:
            raise Exception("long_url and short_url must not be None")

        self.long_url = long_url
        self.short_url = short_url
        self.custom = custom

        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp

        if ip is not None:
            self.ip = ip

    def __repr__(self):
        return '<%s shortened %s to %s>' % \
            (self.ip, self.long_url, self.short_url)


class Hit(Base, Encodable):
    __tablename__ = 'hits'

    id = Column(Integer, primary_key=True)
    short_url = Column(String(32),
                       ForeignKey('shortenings.short_url'),
                       index=True)
    timestamp = Column(DateTime)
    ip = Column(String(45), index=True)

    def __init__(self, short_url, *_, timestamp=None, ip=None):
        self.short_url = short_url

        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp

        if ip is not None:
            self.ip = ip

    def __repr__(self):
        return '<%s opened %s>' % (self.ip, self.short_url)


class User(Base, Encodable):
    __tablename__ = 'users'

    email = Column(String(100), primary_key=True)
    password_hash = Column(String(128))
    token = Column(String(32))
    admin = Column(Boolean)

    def __init__(self, email, password, *_, admin=False):
        self.email = email
        self.password_hash = pwd_context.encrypt(password)

        self.token = hashlib.md5(email.encode('utf-8')).hexdigest()
        self.admin = admin

    def _verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return "AccessToken(email=%s, token=%s, admin=%r)" % \
            (self.email, self.token, self.admin)


engine = create_engine(config['app']['SQLALCHEMY_DATABASE_URI'])
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
