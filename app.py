from flask import Flask, request, Response
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from web.database.client import init_database
from web.config.errors import errors
from dotenv import load_dotenv
import os
import sys

sys.path.append(".")

load_dotenv()

template_dir = os.path.abspath("web/views/templates")
app = Flask(__name__, template_folder=template_dir)

if app.config["ENV"] == os.environ.get("FLASK_ENV"):
    app.config.from_object(os.environ.get("APP_CONFIG_PROD"))
else:
    if app.config["DEBUG"]:
        app.config.from_object(os.environ.get("APP_CONFIG_DEV"))
    else:
        app.config.from_object(os.environ.get("APP_CONFIG_TEST"))

mail = Mail(app)

from web.config.routes import init_routes

api = Api(app, errors=errors)
# api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

init_database(app)
init_routes(api)

# Caught an error - cannot import name 'init_routes' from partially initialized module 'web.config.routes' (most likely due to a circular import) (D:\Projects\Python\Raphlica\raphlica\config\routes.py)
# Separate app.run() to another file. Because there's circular dependency.
# Start -> app.py -> routes.py -> reset_password.py -> services.mail.py (This file importing app from app.py whereas app is not yet defined on our app.py) -> app.py (back - because it's called circular)
# if __name__ == "__main__":
#     app.run(host=os.environ.get("HOST"), port=os.environ.get("PORT"))
