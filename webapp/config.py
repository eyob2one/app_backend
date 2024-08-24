import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOT_TOKEN = os.environ.get('BOT_TOKEN') or '7514207604:AAE_p_eFFQ3yOoNn-GSvTSjte2l8UEHl7b8'
