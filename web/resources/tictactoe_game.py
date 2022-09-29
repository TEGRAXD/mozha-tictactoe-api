from flask import request, Response
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from web.config.response import getResponse
from web.database.models.tictactoe_game import TictactoeGame
from web.database.models.user import User
from mongoengine.errors import (
    ValidationError,
    MongoEngineException,
    OperationError,
)
from werkzeug.exceptions import HTTPException, BadRequest
import web.config.errors as err

class ApiTictactoeGames(Resource):
    @jwt_required()
    def get(self):
        try:
            jwt_user_id = get_jwt_identity()

            body = request.get_json()

            print(body["user"])

            if ("user" in body):
                user = User.objects.get(id=body["user"])
            else:
                user = User.objects.get(id=jwt_user_id)

            # Allowing null returned data
            try:
                tgames = TictactoeGame.objects(user=user).to_json()
            except TictactoeGame.DoesNotExist:
                tgames = None

            return Response(getResponse(result=tgames), mimetype="application/json", status=200)
        except (MongoEngineException, ValidationError, OperationError) as e:
            print(e)
            raise err.CustomHTTPException(code=500, description=str(e.__class__.__name__))
        except HTTPException as e:
            raise err.CustomHTTPException(code=e.code, description=e.name)
        except Exception as e:
            raise err.InternalServerError

class ApiTictactoeGame(Resource):
    @jwt_required()
    def get(self):
        try:
            jwt_user_id = get_jwt_identity()

            body = request.get_json()

            user = User.objects.get(id=jwt_user_id)

            tgame = TictactoeGame.objects.get(id=body["game"]).to_json()

            return Response(getResponse(result=tgame), mimetype="application/json", status=200)
        except (MongoEngineException, ValidationError, OperationError) as e:
            raise err.CustomHTTPException(code=500, description=str(e.__class__.__name__))
        except HTTPException as e:
            raise err.CustomHTTPException(code=e.code, description=e.name)
        except Exception as e:
            raise err.InternalServerError

    @jwt_required()
    def post(self):
        try:
            jwt_user_id = get_jwt_identity()

            body = request.get_json()

            user = User.objects.get(id=jwt_user_id)

            tgame = TictactoeGame(**body, user=user)
            tgame.save()

            tgame = tgame.to_json()

            return Response(getResponse(result=tgame), mimetype="application/json", status=200)
        except (MongoEngineException, ValidationError, OperationError) as e:
            raise err.CustomHTTPException(code=500, description=str(e.__class__.__name__))
        except HTTPException as e:
            raise err.CustomHTTPException(code=e.code, description=e.name)
        except Exception as e:
            raise err.InternalServerError
