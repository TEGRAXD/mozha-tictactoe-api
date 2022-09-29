import os
import pathlib
import getopt, sys
import torch
import torch.nn as nn
from torchinfo import summary
import numpy as np
import pandas as pd
import random
from scipy.ndimage import shift
from params import Object, Mode, Status
from tictactoe.tictactoe import NeuralNetwork, Tictactoe, Move

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

print(f"Using {device} device")

def train(model, optimizer, criterion, mode, print_progress=False):
    """Function trains the Evaluator (model) by playing a game against an opponent 
    playing random moves, and updates the weights of the model after the game

    Note that the model weights are updated using SGD with a batch size of 1

    Args:
    model: The Evaluator function being trained

    Returns:
    model: The model updated using SGD
    y: The corrected scores

    """
    # Sets model in training mode
    model.train()

    if print_progress == True:
        print("Game Start\n")

    game = Tictactoe()
    game.toss()
    scores_list = []
    corrected_scores_list = []
    new_board_states_list = []
    
    movement = Move(device)

    while(1):
        if game.status() == Status.Progress and game.turn_monitor == Object.Mozha:
            # If its the program's turn, use the Move Selector function to select the next move
            selected_move, new_board_state, score = movement.model_move_selector(model, game.board, game.turn_monitor)

            scores_list.append(score[0][0])
            new_board_states_list.append(new_board_state)

            # Make the next move
            game_status, board = game.move(game.turn_monitor, selected_move)

            if print_progress:
                print("Mozha's Move")
                print("{}\n".format(board))

        elif game.status() == Status.Progress and game.turn_monitor == Object.Player:
            selected_move = movement.opponent_move_selector(game.board, game.turn_monitor, mode=mode)

            # Make the next move
            game_status, board = game.move(game.turn_monitor, selected_move)

            if print_progress:
                print("Opponent's Move")
                print("{}\n".format(board))

        else:
            # if not print_progress:
            #     print("\n{}'s Move".format("Opponent" if game.turn_monitor == Object.Mozha else "Mozha"))
            #     print("{}\n".format(board))
            break

    # Correct the scores, assigning 1.0/0.0/-1.0 to the winning/drawn/losing final board state,
    # and assigning the other previous board states the score of their next board state
    new_board_states_list = tuple(new_board_states_list)
    new_board_states_list = np.vstack(new_board_states_list)

    # Mozha won
    if game_status == Status.Won and game.turn_monitor != Object.Mozha:
        corrected_scores_list = shift(torch.tensor(scores_list), -1, cval=1.0)
        result = Status.Won

    # Mozha lost (When the turn_monitor is at Mozha)
    if game_status == Status.Won and game.turn_monitor == Object.Mozha:
        corrected_scores_list = shift(torch.tensor(scores_list), -1, cval=-1.0)
        result = Status.Lost

    if game_status == Status.Tied:
        corrected_scores_list = shift(torch.tensor(scores_list), -1, cval=0.0)
        result = Status.Tied
  

    x = new_board_states_list
    y = corrected_scores_list

    def unison_shuffled_copies(a, b):
        assert len(a) == len(b)
        p = np.random.permutation(len(a))
        return a[p], b[p]

    # Shuffle x and y in unison
    x, y = unison_shuffled_copies(x, y)
    x = x.reshape(-1, 9)

    x = torch.tensor(x).to(device)
    y = torch.tensor(y).to(device)
    y = y.unsqueeze(1)


    # Prediction
    pred = model(x)
    loss = criterion(pred, y)
    
    # Backpropagation
    optimizer.zero_grad() # Sets the gradients of all optimized [torch.Tensor]s to zero. 
    loss.backward() # Computes the gradient of current tensor w.r.t. graph leaves.
    optimizer.step()

    if print_progress:
        print("Mozha has {}\n".format("Win" if result == Status.Won else ("Lost" if result == Status.Lost else "Tied")))
        print("Loss : {}\n".format(loss.item()))

    return model, y, loss, result

if __name__ == "__main__":
    model = NeuralNetwork().to(device)
    model.load_state_dict(torch.load(os.path.join(pathlib.Path().resolve(), "model_20220702204349.pt")))

    print(model)
    summary(model)

    # Hyper Parameters
    learning_rate = 0.001
    momentum = 0.8
    epoch = 200000

    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum, nesterov=False)
    criterion = nn.MSELoss()

    dataFrame = pd.DataFrame()

    mode_list = [Mode.Easy, Mode.Hard]

    wins = 0
    loses = 0
    tieds = 0

    for counter in range(0, epoch):
        mode_selected = np.random.choice(mode_list, 1, p=[(1 / len(mode_list)) for _ in mode_list])
        
        if ((counter+1) % (round(epoch/10, -1))) == 0 or counter == 0:
            print("Game #{}".format(counter+1))
            print("Mode : {}\n".format("Easy" if mode_selected[0] == Mode.Easy else "Hard"))

        model, y, loss, result  = train(model, optimizer, criterion, mode_selected, print_progress=False)

        if result == Status.Won:
            wins += 1
        elif result == Status.Lost:
            loses += 1
        else:
            tieds += 1

        dataFrame = pd.concat([dataFrame, pd.DataFrame([{"counter": counter, "result": result}])], ignore_index=True)

    # Save model
    # modelFilename = "model_" + datetime.today().strftime("%Y%m%d%H%M%S")
    # torch.save(model.state_dict(), os.path.join(pathlib.Path().resolve(), modelFilename + ".pt"))
    # print("Model saved as ", modelFilename)

    print("\nMozha's Won : ", wins)
    print("Mozha's Lost : ", loses)
    print("Tied : ", tieds)
    print("\nWin percentage : ", (wins/(wins+loses+tieds)) * 100)
    print("Lose percentage : ", (loses/(wins+loses+tieds)) * 100)
    print("Tied percentage : ", (tieds/(wins+loses+tieds)) * 100)

    bins = np.arange(1, 20) * epoch/20
    dataFrame["counter_bins"] = np.digitize(dataFrame["counter"], bins, right=True)
    counts = dataFrame.groupby(["counter_bins", "result"]).counter.count().unstack()

    ax = counts.plot(kind="bar", stacked=True, figsize=(17, 5))
    
    L = ax.legend()

    for legend in L.get_texts():
        if int(legend.get_text()) == Status.Won:
            legend.set_text("Win")
        elif int(legend.get_text()) == Status.Lost:
            legend.set_text("Lose")
        else:
            legend.set_text("Tie")

    ax.set_xlabel("Count of Games in Bins of {}s".format(epoch/20))
    ax.set_ylabel("Counts of Draws/Losses/Wins")
    ax.set_title("Distribution of Results Vs Count of Games Played")

    # plt.savefig(os.path.join(pathlib.Path().resolve(), modelFilename + ".png"))