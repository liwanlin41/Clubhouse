import os

# configuration file for main application?

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY','to-be-filled')
    LANGUAGES = ['en', 'es']
    # es is currently garbled English, used for testing only
