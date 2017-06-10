from main import db
from datetime import datetime


class Shortening(db.Model):
    __tablename__ = 'shortenings'

    long_url = db.Column(db.String(2000), primary_key=True)
    short_url = db.Column(db.String(32), unique=True, index=True)
    hits = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime)
    ip = db.Column(db.String(45), index=True)

    def __init__(self, long_url, short_url, timestamp=None, ip=None):
        self.long_url = long_url
        self.short_url = short_url
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

