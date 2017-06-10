from main import db
from datetime import datetime

"""
Rules:

    There can be as many custom short URLs mapped to the same long URL,
    but only one non-custom (random) one.

    Custom shortenings are *hidden from sight*: retrieving the short URL
    mapped to a long URL should only return the non-custom one.

    During a "shorten" query, if all shortenings of a long URL are custom,
    than a new random one should be generated.
"""


class Shortening(db.Model):
    __tablename__ = 'shortenings'

    long_url = db.Column(db.String(2000), index=True)
    short_url = db.Column(db.String(32), primary_key=True)
    hits = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime)
    ip = db.Column(db.String(45), index=True)
    custom = db.Column(db.Boolean)

    def __init__(self, long_url, short_url, timestamp=None, ip=None, custom=False):
        self.long_url = long_url
        self.short_url = short_url
        self.custom = custom

        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp

        if ip is not None:
            self.ip = ip


    def __repr__(self):
        return '<%s shortened %s to %s>' % (self.ip, self.long_url, self.short_url)

    def __add__(self, other):
        try:
            self.hits += other
            db.session.commit()
        except:
            print("Could not add %r hits to %r" % (other, self))
        return self

    def __sub__(self, other):
        try:
            self.hits -= other
            db.session.commit()
        except:
            print("Could not subtract %r hits to %r" % (other, self))
        return self

    def reset_hits(self):
        self.hits = 0
        db.session.commit()

