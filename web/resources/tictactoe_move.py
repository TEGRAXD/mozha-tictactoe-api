from flask import request, Response
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from web.config.response import getResponse
from web.database.models.tictactoe_game import TictactoeGame
from web.database.models.tictactoe_move import TictactoeMove
from web.database.models.user import User
# from mongoengine.errors import (
#     ValidationError,
#     MongoEngineException,
#     OperationError,
# )
# from werkzeug.exceptions import HTTPException, BadRequest

import web.config.errors as err
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, \
    DoesNotExist, ValidationError, InvalidQueryError

import os
import pathlib
import torch
import numpy as np

from tictactoe.tictactoe import NeuralNetwork, Tictactoe, Move, Player
from tictactoe.params import Object, Mode, Status

device = "cpu"

model = NeuralNetwork().to(device)
model.load_state_dict(torch.load(os.path.join(os.path.join(os.path.join(pathlib.Path(__file__).parent.parent.parent.resolve(), "tictactoe"), "models"), "model_20220702204349.pt")))
print(" * Neural Network model loaded!")

class ApiTictactoeMoves(Resource):
    @jwt_required()
    def get(self):
        try:
            jwt_user_id = get_jwt_identity()

            body = request.get_json()

            if 'move' not in body:
                raise ValidationError
            
            tgame = TictactoeGame.objects.get(id=body['game'])

            # Allowing null returned data
            try:
                tmoves = TictactoeMove.objects.get(game=tgame).to_json()
            except TictactoeMove.DoesNotExist:
                tmoves = None

            return Response(getResponse(result=tmoves), mimetype="application/json", status=200)
        except ValidationError:
            raise err.SchemaValidationError
        except DoesNotExist:
            raise err.NotExistError
        except Exception as e:
            raise err.InternalServerError

class ApiTictactoeMove(Resource):
    @jwt_required()
    def get(self):
        try:
            jwt_user_id = get_jwt_identity()

            body = request.get_json()

            if 'move' not in body:
                raise ValidationError
            
            tmove = TictactoeMove.objects.get(id=body['move'])

            return Response(getResponse(result=tmove.to_json()), mimetype="application/json", status=200)
        except ValidationError:
            raise err.SchemaValidationError
        except DoesNotExist:
            raise err.NotExistError
        except Exception as e:
            raise err.InternalServerError

    @jwt_required()
    def post(self):
        try:
            jwt_user_id = get_jwt_identity()

            body = request.get_json()
            
            user = User.objects.get(id=jwt_user_id)

            if 'game' not in body:
                raise ValidationError

            tgame = TictactoeGame.objects.get(id=body['game'])

            try:
                tmoves = TictactoeMove.objects.get(game=tgame)
            except TictactoeMove.DoesNotExist:
                tmoves = None
                turn = 1
            else:
                turn = len(tmoves) + 1

            if 'turn_monitor' not in body:
                raise ValidationError
            
            if 'board' not in body:
                raise ValidationError

            game = Tictactoe()
            game.turn_monitor = body['turn_monitor']
            game.board = np.array(body['board'])
            
            move = Move(device)

            tmove = None

            if game.status() == Status.Progress and game.turn_monitor == Object.Mozha:
                # If its Mozha's turn, use the Model Move Selector method to predict and select the next move
                selected_move = move.model_move_selector(model, game.board, game.turn_monitor)

                # Make the next move
                game_status, board = game.move(game.turn_monitor, selected_move)

                # Without user (Mozha create her own move)
                tmove = TictactoeMove(game=tgame, turn=turn, turn_monitor=Object.Mozha, move=list(selected_move), board=board, status=game_status)
                tmove.save()
            elif game.status() == Status.Progress and game.turn_monitor == Object.Player:
                if 'move' not in body:
                    raise ValidationError
                
                selected_move = tuple(body['move'])

                # Move method could produce ValueError with 'Invalid selected move' message 
                game_status, board = game.move(game.turn_monitor, selected_move)    
                
                # Contains user (User create their own move)
                tmove = TictactoeMove(user=user, game=tgame, turn=turn, turn_monitor=Object.Player, move=list(selected_move), board=board, status=game_status)
                tmove.save()

            tmove = tmove.to_json()

            return Response(getResponse(result=tmove), mimetype='application/json', status=200)
        except (FieldDoesNotExist, ValidationError):
            raise err.SchemaValidationError
        except ValueError as e:
            raise err.CustomHTTPException(code=400, description='Invalid selected move')
        except Exception as e:
            raise err.InternalServerError