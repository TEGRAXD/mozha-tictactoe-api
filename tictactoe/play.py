# If you running this file, the error will occured, it'll be ModuleNotFound: No module named "tictactoe.params"; tictactoe is not a package.
# Remove "tictactoe." from line "from tictactoe.params import Object, Mode, Status"
# in tictactoe/tictactoe.py.

import os
import pathlib
import getopt, sys
import torch
from tictactoe import NeuralNetwork, Tictactoe, Move, Player
from params import Object, Mode, Status

device = "cpu"

args = sys.argv[1:]

# Options
opts = "hd:"

# Long Options
longopts = ["help", "device="]

try:
    arguments, values = getopt.getopt(args, opts, longopts)

    for crntArg, crntVal in arguments:
        if crntArg in ("-h", "--help"):
            print("Displaying Help")
        elif crntArg in ("-d", "--device"):
            print("Displaying x : {}".format(crntVal))
            if crntVal.casefold() == "cuda".casefold():
                device = "cuda" if torch.cuda.is_available() else "cpu"
            elif crntVal.casefold() == "cpu".casefold():
                device = "cpu"
            else:
                print("--device: Invalid argument {}".format(crntVal))
except getopt.error as err:
    print(str(err))

def play(model, print_progress=False):
    game = Tictactoe()
    game.toss()
    scores_list = []
    new_board_states_list = []
    
    move = Move(device)

    while(1):
        if game.status() == Status.Progress and game.turn_monitor == Object.Mozha:
            # If its the program's turn, use the Move Selector function to select the next move
            selected_move, new_board_state, score = move.model_move_selector(model, game.board, game.turn_monitor)

            scores_list.append(score[0][0])
            print(scores_list)
            new_board_states_list.append(new_board_state)
            print(new_board_states_list)

            # Make the next move
            game_status, board = game.move(game.turn_monitor, selected_move)

            if print_progress:
                print("Mozha's Move")
                print("{}\n".format(board))

        elif game.status() == Status.Progress and game.turn_monitor == Object.Player:
            while(1):
                try:
                    print("Your Turn")

                    selected_move = Player.move()
                    game_status, board = game.move(game.turn_monitor, selected_move)
                    break
                except Exception as err:
                    print(str(err))

            print("\n{}\n".format(board))
        else:
            break

    # Mozha won
    if game_status == Status.Won and game.turn_monitor != Object.Mozha:
        result = Status.Won

    # Mozha lost (When the turn_monitor is at Mozha)
    if game_status == Status.Won and game.turn_monitor == Object.Mozha:
        result = Status.Lost

    if game_status == Status.Tied:
        result = Status.Tied
    
    if print_progress:
        print("{}\n".format("You lose" if result == Status.Won else ("You win" if result == Status.Lost else "Tied")))

if __name__ == "__main__":
    print(f"Using {device} device\n")

    model = NeuralNetwork().to(device)
    model.load_state_dict(torch.load(os.path.join(os.path.join(pathlib.Path(__file__).parent.resolve(), "models"), "model_20220702204349.pt")))

    play(model, print_progress=True)
    