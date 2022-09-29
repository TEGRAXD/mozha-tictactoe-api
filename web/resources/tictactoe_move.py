from flask import request, Response
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from web.config.response import getResponse
from web.database.models.tictactoe_game import TictactoeGame
from web.database.models.tictactoe_move import TictactoeMove
from web.database.models.user import User
from mongoengine.errors import (
    ValidationError,
    MongoEngineException,
    OperationError,
)
from werkzeug.exceptions import HTTPException, BadRequest
import web.config.errors as err


import os
import pathlib
import getopt, sys
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

            if ("game" in body):
                tgame = TictactoeGame.objects.get(id=body["game"])

            # Allowing null returned data
            try:
                tmoves = TictactoeMove.objects(game=tgame).to_json()
            except TictactoeMove.DoesNotExist:
                tmoves = None

            return Response(getResponse(result=tmoves), mimetype="application/json", status=200)
        except (MongoEngineException, ValidationError, OperationError) as e:
            raise err.CustomHTTPException(code=500, description=str(e.__class__.__name__))
        except HTTPException as e:
            raise err.CustomHTTPException(code=e.code, description=e.name)
        except Exception as e:
            print(e)
            raise err.InternalServerError

class ApiTictactoeMove(Resource):
    @jwt_required()
    def get(self):
        try:
            jwt_user_id = get_jwt_identity()

            body = request.get_json()
            
            tmove = TictactoeMove.objects.get(id=body["move"])

            return Response(getResponse(result=tmove.to_json()), mimetype="application/json", status=200)
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

            try:
                user = User.objects.get(id=jwt_user_id)
            except User.DoesNotExist:
                user = None

            tgame = TictactoeGame.objects.get(id=body["game"])

            game = Tictactoe()
            # game.toss()
            game.turn_monitor = tgame.turn_monitor
            game.board = np.array(body["board"])

            scores_list = []
            new_board_states_list = []

            move = Move(device)

            # when mozha get the first turn to move
            # user will send post and the server shouldn't save it to database as a valid move.
            # instead, save mozha's move and return the correct response.

            # when user get the first turn to move
            # user will send post and the server will save it to database as a valid move.

            if game.status() == Status.Progress and game.turn_monitor == Object.Mozha:
                # If its the program's turn, use the Move Selector function to select the next move
                selected_move, new_board_state, score = move.model_move_selector(model, game.board, game.turn_monitor)
                
                scores_list.append(score[0][0])
                new_board_states_list.append(new_board_state)

                # Make the next move
                game_status, board = game.move(game.turn_monitor, selected_move)

                # Without user (Mozha create her own move)
                tmove = TictactoeMove(game=tgame, move=list(selected_move), board=board, status=game_status)
                tmove.save()

                tgame.update(turn_monitor=Object.Player)
            elif game.status() == Status.Progress and game.turn_monitor == Object.Player:
                selected_move = tuple(body["move"])

                game_status, board = game.move(game.turn_monitor, selected_move)    
                
                # Contains user (User create their own move)
                tmove = TictactoeMove(user=user, game=tgame, move=list(selected_move), board=board, status=game_status)
                tmove.save()
                
                tgame.update(turn_monitor=Object.Mozha)

            tmove = tmove.to_json()

            return Response(getResponse(result=tmove), mimetype="application/json", status=200)
        except (MongoEngineException, ValidationError, OperationError) as e:
            raise err.CustomHTTPException(code=500, description=str(e.__class__.__name__))
        except HTTPException as e:
            raise err.CustomHTTPException(code=e.code, description=e.name)
        except ValueError as e:
            raise err.CustomHTTPException(code=500, description=str(e.__class__.__name__), opt_description=str(e))
        except Exception as e:
            raise err.InternalServerError