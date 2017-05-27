from main import db
from datetime import datetime


class LongToShort(db.Model):
    __tablename__ = 'long_to_short'

    long_url = db.Column(db.String(2000), primary_key=True)
    short_url = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime)

    def __init__(self, long_url, short_url, timestamp=None):
        self.long_url = long_url
        self.short_url = short_url
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp

    def __repr__(self):
        return '<%s -> %s>' % (self.long_url, self.short_url)


class ShortToLong(db.Model):
    __tablename__ = 'short_to_long'

    short_url = db.Column(db.String(32), primary_key=True)
    long_url = db.Column(db.String(200))

    def __init__(self, short_url, long_url):
        self.short_url = short_url
        self.long_url = long_url

    def __repr__(self):
        return '<%s -> %s>' % (self.short_url, self.long_url)
