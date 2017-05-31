from string import ascii_lowercase, ascii_uppercase

config = {
    'secret_key': "asdf",
    'short_url_size': 6,
    'alphabet': ascii_lowercase + ascii_uppercase + '0123456789',

    'app': {
        'SQLALCHEMY_DATABASE_URI': "postgresql://localhost/url-shortener",
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }
}
