from flask_mongoengine import MongoEngine

mongoEngine = MongoEngine()

def init_database(app):
    mongoEngine.init_app(app)
