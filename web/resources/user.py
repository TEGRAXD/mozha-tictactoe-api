from flask import request, Response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from web.config.response import getResponse
from web.database.models.user import User
from mongoengine.errors import (
    FieldDoesNotExist,
    NotUniqueError,
    DoesNotExist,
    ValidationError,
    InvalidQueryError,
)
from ..config.errors import (
    SchemaValidationError,
    InternalServerError,
    ExistError,
    NotExistError,
    UnauthorizedError,
    UpdateError,
    DeleteError,
)

class ApiUsers(Resource):
    @jwt_required()
    def get(self):
        try:
            users = User.objects.exclude("password").to_json()
            return Response(getResponse(result=users), mimetype="application/json", status=200)
        except DoesNotExist:
            raise NotExistError
        except Exception:
            raise InternalServerError

class ApiUser(Resource):
    @jwt_required()
    def get(self):
        try:
            # jwt_user_id = get_jwt_identity()

            query_id = request.args.get("id")
            user = User.objects.exclude("password").get(id=query_id).to_json()
            return Response(user, mimetype="application/json", status=200)
        except DoesNotExist:
            raise NotExistError
        except Exception:
            raise InternalServerError

    @jwt_required()
    def put(self):
        try:
            query_id = request.args.get("id")
            body = request.get_json()
            body.pop("password", None)

            user = User.objects.get(id=query_id)

            user.update(**body)

            return Response(getResponse(message="UPDATED", result=user.to_json()), mimetype="application/json", status=200)
        except InvalidQueryError:
            raise SchemaValidationError
        except DoesNotExist:
            raise NotExistError
        except ValidationError as e:
            raise UpdateError(description=e.message)
        except Exception as e:
            raise InternalServerError

    @jwt_required()
    def delete(self):
        try:
            query_id = request.args.get("id")
            user = User.objects.get(id=query_id)
            user.delete()
            
            return Response(getResponse(message="DELETED", result=user.to_json()), mimetype="application/json", status=200)
        except DoesNotExist:
            raise NotExistError
        except Exception:
            raise InternalServerError

class ApiUserPassword(Resource):
    @jwt_required()
    def put(self):
        try:
            # jwt_user_id = get_jwt_identity()

            # body = request.get_json()
            # user = User.objects.get(email=body.get("email"))
            query_id = request.args.get("id")
            body = request.get_json()
            password = body.get("password")
            new_password = body.get("new_password")

            user = User.objects.get(id=query_id)

            authorized = user.check_password(password)

            if not authorized:
                raise UnauthorizedError

            user.modify(password=new_password)
            user.hash_password()
            user.save()

            return Response(getResponse(message="UPDATED", result=user.to_json()), mimetype="application/json", status=200)
        except InvalidQueryError as e:
            print(e)
            raise SchemaValidationError
        except DoesNotExist:
            raise NotExistError
        except UnauthorizedError:
            raise UnauthorizedError
        except ValidationError as e:
            print(e)
            raise UpdateError(description=e.message)
        except Exception as e:
            print(e)
            raise InternalServerError