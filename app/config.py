import os
class Configuration(object):
    APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
    DEBUG = True
    SECRET_KEY = 'flask is fun!'  # Create a unique key for your app.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/blog.db' % APPLICATION_DIR
    SQLALCHEMY_TRACK_MODIFICATIONS = False
