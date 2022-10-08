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
            users = User.objects.exclude('password').to_json()
            return Response(getResponse(result=users), mimetype='application/json', status=200)
        except DoesNotExist:
            raise NotExistError
        except Exception:
            raise InternalServerError

class ApiUser(Resource):
    @jwt_required()
    def get(self):
        try:
            try:
                query_id = request.args.get('id')
                query_email = None
                query_username = None

                if query_id is None:
                    query_email = request.args.get('email')
                else:
                    user = User.objects.exclude('password').get(id=query_id)
                
                if query_email is None:
                    query_username = request.args.get('username')
                else:
                    user = User.objects.exclude('password').get(email=query_email)
                
                if query_username is not None:
                    user = User.objects.exclude('password').get(username=query_username)
                
                user = user.to_json()
            except User.DoesNotExist:
                user = None

            return Response(getResponse(result=user), mimetype='application/json', status=200)
        except DoesNotExist:
            raise NotExistError
        except Exception as e:
            raise InternalServerError

    @jwt_required()
    def put(self):
        try:
            query_id = request.args.get('id')
            body = request.get_json()
            body.pop('password', None)

            user = User.objects.get(id=query_id)

            user.update(**body)

            user = user.to_json()

            return Response(getResponse(message='UPDATED', result=user), mimetype='application/json', status=200)
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
            query_id = request.args.get('id')
            
            user = User.objects.get(id=query_id)

            user.delete()

            user = user.to_json()
            
            return Response(getResponse(message='DELETED', result=user), mimetype='application/json', status=200)
        except DoesNotExist:
            raise NotExistError
        except Exception:
            raise InternalServerError

class ApiUserPassword(Resource):
    @jwt_required()
    def put(self):
        try:
            query_id = request.args.get('id')
            body = request.get_json()
            password = body.get('password')
            new_password = body.get('new_password')

            user = User.objects.get(id=query_id)

            authorized = user.check_password(password)

            if not authorized:
                raise UnauthorizedError

            user.modify(password=new_password)
            user.hash_password()
            user.save()

            return Response(getResponse(message='UPDATED', result=user.to_json()), mimetype='application/json', status=200)
        except InvalidQueryError as e:
            raise SchemaValidationError
        except DoesNotExist:
            raise NotExistError
        except UnauthorizedError:
            raise UnauthorizedError
        except ValidationError as e:
            raise UpdateError(description=e.message)
        except Exception as e:
            raise InternalServerError