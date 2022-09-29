import datetime
import json
from flask import request, Response, render_template
from flask_restful import Resource
from flask_jwt_extended import create_access_token, decode_token
from web.config.response import getResponse
from web.database.models.user import User
from mongoengine.errors import (
    FieldDoesNotExist,
    NotUniqueError,
    DoesNotExist,
    ValidationError,
    InvalidQueryError,
)
from jwt.exceptions import ExpiredSignatureError, DecodeError, InvalidTokenError
from ..config.errors import (
    SchemaValidationError,
    InternalServerError,
    ExistError,
    NotExistError,
    UnauthorizedError,
    UpdateError,
    DeleteError,
    EmailDoesNotExistsError,
    BadTokenError,
    ExpiredTokenError,
)
from ..services.mail import send_email

class ApiSignUp(Resource):
    def post(self):
        try:
            body = request.get_json()
            user = User(**body)
            user.hash_password()
            user.save()
            
            return Response(getResponse(result=user.to_json()), mimetype="application/json", status=200)
        except FieldDoesNotExist:
            raise SchemaValidationError
        except NotUniqueError:
            raise ExistError
        except Exception:
            raise InternalServerError


class ApiSignIn(Resource):
    def post(self):
        try:
            body = request.get_json()
            user = User.objects.get(email=body.get("email"))

            authorized = user.check_password(body.get("password"))

            if not authorized:
                raise UnauthorizedError

            expires = False  # False to disable expiration. Use datetime.timedelta(days=7) for expiration.
            
            access_token = create_access_token(identity=str(user.id), expires_delta=expires)

            res = {}
            res["token"] = access_token

            return Response(getResponse(result=json.dumps(res)), mimetype="application/json", status=200)
        except (UnauthorizedError, DoesNotExist):
            raise UnauthorizedError
        except Exception as e:
            print(e)
            raise InternalServerError


class ApiForgotPassword(Resource):
    def post(self):
        url = request.host_url + "reset/"
        try:
            body = request.get_json()
            email = body.get("email")
            if not email:
                raise SchemaValidationError

            user = User.objects.get(email=email)
            if not User:
                raise NotExistError

            expires = datetime.timedelta(minutes=10)
            reset_token = create_access_token(str(user.id), expires_delta=expires)

            return send_email(
                "[Mozha] Reset Your Password",
                sender="support@astaria.space",
                recipients=[user.email],
                text_body=render_template(
                    "email/reset_password.txt",
                    url=url + reset_token,
                ),
                html_body=render_template(
                    "email/reset_password.html",
                    url=url + reset_token,
                ),
            )

        except SchemaValidationError:
            raise SchemaValidationError
        except NotExistError:
            raise NotExistError
        except Exception as e:
            raise InternalServerError


class ApiResetPassword(Resource):
    def post(self):
        url = request.host_url + "reset/"
        try:
            body = request.get_json()
            reset_token = body.get("reset_token")
            password = body.get("password")

            if not reset_token or not password:
                raise SchemaValidationError

            user_id = decode_token(reset_token)["sub"]

            user = User.objects.get(id=user_id)

            user.modify(password=password)
            user.hash_password()
            user.save()

            return send_email(
                "[Mozha] Password reset successful",
                sender="support@astaria.space",
                recipients=[user.email],
                text_body="Password reset was successful",
                html_body="<p>Password reset was successful</p>",
            )

        except SchemaValidationError:
            raise SchemaValidationError
        except ExpiredSignatureError:
            raise ExpiredTokenError
        except (DecodeError, InvalidTokenError):
            raise BadTokenError
        except Exception as e:
            raise InternalServerError
