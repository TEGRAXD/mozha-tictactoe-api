from dotenv import load_dotenv
import os

load_dotenv()

class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MONGODB_SETTINGS = {
        "db": os.environ.get("DB_NAME"),
        "host": os.environ.get("DB_URL") + os.environ.get("DB_NAME"),
    }


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = os.environ.get("DEBUG")


class TestingConfig(Config):
    TESTING = os.environ.get("TESTING")
