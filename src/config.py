from string import ascii_lowercase, ascii_uppercase

config = {
    'secret_key': 'asdf',
    'short_url_size': 6,
    'min_short_url_size': 1,
    'max_short_url_size': 50,
    'max_attempts_until_short_url_size_increases': 3,
    'default_limits': ["10 per second", "100 per minute"],

    'alphabet': ascii_lowercase + ascii_uppercase + '0123456789_-',

    'app': {
        'SQLALCHEMY_DATABASE_URI': "postgresql://localhost/url-shortener",
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'DEBUG': True,
    }
}
