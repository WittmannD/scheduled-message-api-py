import os


class Config(object):
    PORT = os.environ.get('PORT')

    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')


class ProductionConfig(Config):
    ENV = 'production'
    FLASK_ENV = 'production'
    SECRET_KEY = os.environ.get('SECRET_KEY')


class DevelopmentConfig(Config):
    ENV = 'development'
    FLASK_ENV = 'development'
    DEBUG = True
    FLASK_DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_ECHO = False
    SECRET_KEY = 'development_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
