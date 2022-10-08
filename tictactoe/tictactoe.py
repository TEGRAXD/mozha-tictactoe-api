# https://www.kaggle.com/dhanushkishore/a-self-learning-tic-tac-toe-program

import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import random
from tictactoe.params import Object, Mode, Status

class NeuralNetwork(nn.Sequential):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        # Fully connected layer: input_size, output_size
        self.fc1 = nn.Linear(9, 18).double()
        self.fc2 = nn.Linear(18, 9).double()
        self.fc3 = nn.Linear(9, 1).double()

        # Dropout layer
        self.dropout1 = nn.Dropout(0.1).double()
        self.dropout2 = nn.Dropout(0.1).double()

        # self.seq_block = nn.Sequential(
        #     nn.Linear(9, 18),
        #     nn.ReLU(),
        #     nn.Dropout(0.1),
        #     nn.Linear(18, 9),
        #     nn.ReLU(),
        #     nn.Dropout(0.1),
        #     nn.Linear(9, 1)
        # ).double()

        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.05)
            nn.init.zeros_(module.bias.data)
            # module.weight.data.normal_(mean=0.0, std=1.0)
            # module.bias.data.zero_()
            # print(module.weight)
            # nn.init.normal_(module.weight)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout1(x)
        x = self.fc2(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc3(x)
        # x = self.seq_block(x)
        return x

class Tictactoe(object):
    def __init__(self):
        self.board = np.full((3, 3), Object.Placeholder)
    
    def status(self):
        # Check for a win along rows
        for i in range(self.board.shape[0]):
            if Status.Progress not in self.board[i, :] and len(set(self.board[i, :])) == 1:
                return Status.Won

        # Check for a win along columns
        for j in range(self.board.shape[1]):
            if Status.Progress not in self.board[:, j] and len(set(self.board[:, j])) == 1:
                return Status.Won
        
        # Check for a win along diagonals
        if Status.Progress not in np.diag(self.board) and len(set(np.diag(self.board))) == 1:
            return Status.Won
        
        # Check for a win along diagonals
        # fliplr: Flip an array horizontally (axis=1) is equivalent to flip(m, 1)
        if Status.Progress not in np.diag(np.fliplr(self.board)) and len(set(np.diag(np.fliplr(self.board)))) == 1:
            return Status.Won
        
        # Check for a draw
        if not Status.Progress in self.board:
            return Status.Tied
        else:
            return Status.Progress
            

    def toss(self):
        turn = np.random.choice([Object.Mozha, Object.Player], size=1, replace=False)

        if turn.mean() == Object.Mozha:
            self.turn_monitor = Object.Mozha
        else:
            self.turn_monitor = Object.Player
        
        return self.turn_monitor

    def move(self, player, coord):
        if self.board[coord] != Object.Placeholder or self.status() != Status.Progress or self.turn_monitor != player:
            raise ValueError('Invalid selected move')
        
        self.board[coord] = player
        self.turn_monitor = Object.Player if player == Object.Mozha else Object.Mozha

        return self.status(), self.board

    def legal_moves_generator(current_board_state, turn_monitor):
        legal_moves_dict = {}

        for i in range(current_board_state.shape[0]):
            for j in range(current_board_state.shape[1]):
                if current_board_state[i, j] == Object.Placeholder:
                    board_state_copy = current_board_state.copy()
                    board_state_copy[i, j] = turn_monitor
                    legal_moves_dict[(i, j)] = board_state_copy.flatten()
        return legal_moves_dict

class Move():
    def __init__(self, device):
        self.device = device

    def legal_moves_generator(self, current_board_state, turn_monitor):
        """Function that returns the set of all possible legal moves and resulting board states, 
        for a given input board state and player

        Args:
        current_board_state: The current board state
        turn_monitor: 1 if it's the player who places the mark 1's turn to play, 0 if its his opponent's turn

        Returns:
        legal_moves_dict: A dictionary of a list of possible next coordinate-resulting board state pairs
        The resulting board state is flattened to 1 d array

        """
        legal_moves_dict = {}
        for i in range(current_board_state.shape[0]):
            for j in range(current_board_state.shape[1]):
                if current_board_state[i, j] == Object.Placeholder:
                    board_state_copy = current_board_state.copy()
                    board_state_copy[i, j] = turn_monitor
                    legal_moves_dict[(i, j)] = board_state_copy.flatten()
        return legal_moves_dict

    def model_move_selector(self, model, current_board_state, turn_monitor):
        """Function that selects the next move to make from a set of possible legal moves

        Args:
        model: The Evaluator function to use to evaluate each possible next board state
        turn_monitor: 1 if it's the player who places the mark 1's turn to play, 0 if its his opponent's turn

        Returns:
        selected_move: The numpy array coordinates where the player should place thier mark
        new_board_state: The flattened new board state resulting from performing above selected move
        score: The score that was assigned to the above selected_move by the Evaluator (model)

        """
        tracker = {}
        legal_moves_dict = self.legal_moves_generator(current_board_state, turn_monitor)
        for legal_move_coord in legal_moves_dict:
            score = model(torch.tensor(legal_moves_dict[legal_move_coord].reshape(1, 9)).to(self.device))
            tracker[legal_move_coord] = score
        selected_move = max(tracker, key=tracker.get)
        new_board_state = legal_moves_dict[selected_move]
        score = tracker[selected_move]

        return selected_move, new_board_state, score

    def row_winning_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan rowwise and identify coordinate amongst the legal coordinates that will
        result in a winning board state

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will lead to win for the opponent
        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor
            # check for a win along rows
            for i in range(current_board_state_copy.shape[0]):
                if Object.Placeholder not in current_board_state_copy[i, :] and len(set(current_board_state_copy[i, :])) == 1:
                    selected_move = legal_move_coord
                    return selected_move


    def column_winning_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan column wise and identify coordinate amongst the legal coordinates that will
        result in a winning board state

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will lead to win for the opponent
        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor
            for j in range(current_board_state_copy.shape[1]):
                if Object.Placeholder not in current_board_state_copy[:, j] and len(set(current_board_state_copy[:, j])) == 1:
                    selected_move = legal_move_coord
                    return selected_move


    def diag1_winning_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan diagonal and identify coordinate amongst the legal coordinates that will
        result in a winning board state

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will lead to win for the opponent

        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor
            if Object.Placeholder not in np.diag(current_board_state_copy) and len(set(np.diag(current_board_state_copy))) == 1:
                selected_move = legal_move_coord
                return selected_move


    def diag2_winning_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan second diagonal and identify coordinate amongst the legal coordinates that will
        result in a winning board state

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will lead to win for the opponent

        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor
            if Object.Placeholder not in np.diag(np.fliplr(current_board_state_copy)) and len(set(np.diag(np.fliplr(current_board_state_copy)))) == 1:
                selected_move = legal_move_coord
                return selected_move

    def row_block_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan rowwise and identify coordinate amongst the legal coordinates 
        that will prevent the program 
        from winning

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will block 1 from winning

        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor

            for i in range(current_board_state_copy.shape[0]):
                if Object.Placeholder not in current_board_state_copy[i, :] and (current_board_state_copy[i, :] == Object.Mozha).sum() == 2:
                    if not (Object.Placeholder not in current_board_state[i, :] and (current_board_state[i, :] == Object.Mozha).sum() == 2):
                        selected_move = legal_move_coord
                        return selected_move


    def column_block_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan column wise and identify coordinate amongst the legal coordinates that will prevent 1 
        from winning

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will block 1 from winning

        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor

            for j in range(current_board_state_copy.shape[1]):
                if Object.Placeholder not in current_board_state_copy[:, j] and (current_board_state_copy[:, j] == Object.Mozha).sum() == 2:
                    if not (Object.Placeholder not in current_board_state[:, j] and (current_board_state[:, j] == Object.Mozha).sum() == 2):
                        selected_move = legal_move_coord
                        return selected_move


    def diag1_block_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan diagonal 1 and identify coordinate amongst the legal coordinates that will prevent 1 
        from winning

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will block 1 from winning

        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor
            
            if Object.Placeholder not in np.diag(current_board_state_copy) and (np.diag(current_board_state_copy) == Object.Mozha).sum() == 2:
                if not (Object.Placeholder not in np.diag(current_board_state) and (np.diag(current_board_state) == Object.Mozha).sum() == 2):
                    selected_move = legal_move_coord
                    return selected_move


    def diag2_block_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan second diagonal wise and identify coordinate amongst the legal coordinates that will
        result in a column having only 0s

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will lead to two 0s being there (and no 1s)

        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor

            if Object.Placeholder not in np.diag(np.fliplr(current_board_state_copy)) and (np.diag(np.fliplr(current_board_state_copy)) == Object.Mozha).sum() == 2:
                if not (Object.Placeholder not in np.diag(np.fliplr(current_board_state)) and (np.diag(np.fliplr(current_board_state)) == Object.Mozha).sum() == 2):
                    selected_move = legal_move_coord
                    return selected_move

    def row_second_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan rowwise and identify coordinate amongst the legal coordinates that will
        result in a row having two 0s and no 1s

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will lead to two 0s being there (and no 1s)

        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor

            for i in range(current_board_state_copy.shape[0]):
                if Object.Mozha not in current_board_state_copy[i, :] and (current_board_state_copy[i, :] == Object.Player).sum() == 2:
                    if not (Object.Mozha not in current_board_state[i, :] and (current_board_state[i, :] == Object.Player).sum() == 2):
                        selected_move = legal_move_coord
                        return selected_move


    def column_second_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan column wise and identify coordinate amongst the legal coordinates that will
        result in a column having two 0s and no 1s

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will lead to two 0s being there (and no 1s)

        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor

            for j in range(current_board_state_copy.shape[1]):
                if Object.Mozha not in current_board_state_copy[:, j] and (current_board_state_copy[:, j] == Object.Player).sum() == 2:
                    if not (Object.Mozha not in current_board_state[:, j] and (current_board_state[:, j] == Object.Player).sum() == 2):
                        selected_move = legal_move_coord
                        return selected_move


    def diag1_second_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan diagonal wise and identify coordinate amongst the legal coordinates that will
        result in a column having two 0s and no 1s

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will lead to two 0s being there (and no 1s)

        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor

            if Object.Mozha not in np.diag(current_board_state_copy) and (np.diag(current_board_state_copy) == Object.Player).sum() == 2:
                if not (Object.Mozha not in np.diag(current_board_state) and (np.diag(current_board_state) == Object.Player).sum() == 2):
                    selected_move = legal_move_coord
                    return selected_move


    def diag2_second_move_check(self, current_board_state, legal_moves_dict, turn_monitor):
        """Function to scan second diagonal wise and identify coordinate amongst 
        the legal coordinates that will result in a column having two 0s and no 1s

        Args:
        legal_moves_dict: Dictionary of legal next moves
        turn_monitor: whose turn it is to move

        Returns:
        selected_move: The coordinates of numpy array where opponent places their mark

        """
        legal_move_coords = list(legal_moves_dict.keys())
        random.shuffle(legal_move_coords)
        for legal_move_coord in legal_move_coords:
            current_board_state_copy = current_board_state.copy()
            current_board_state_copy[legal_move_coord] = turn_monitor
            
            if Object.Mozha not in np.diag(np.fliplr(current_board_state_copy)) and (np.diag(np.fliplr(current_board_state_copy)) == Object.Player).sum() == 2:
                if not (Object.Mozha not in np.diag(np.fliplr(current_board_state)) and (np.diag(np.fliplr(current_board_state)) == Object.Player).sum() == 2):
                    selected_move = legal_move_coord
                    return selected_move


    def opponent_move_selector(self, current_board_state, turn_monitor, mode):
        """Function that picks a legal move for the opponent

        Args:
        current_board_state: Current board state
        turn_monitor: whose turn it is to move
        mode: whether hard or easy mode

        Returns:
        selected_move: The coordinates of numpy array where placing the 0 will lead to two 0s being there (and no 1s)

        """
        legal_moves_dict = self.legal_moves_generator(current_board_state, turn_monitor)

        winning_move_checks = [self.row_winning_move_check, self.column_winning_move_check,
                            self.diag1_winning_move_check, self.diag2_winning_move_check]
        block_move_checks = [self.row_block_move_check, self.column_block_move_check,
                            self.diag1_block_move_check, self.diag2_block_move_check]
        second_move_checks = [self.row_second_move_check, self.column_second_move_check,
                            self.diag1_second_move_check, self.diag2_second_move_check]

        if mode == Mode.Hard:
            random.shuffle(winning_move_checks)
            random.shuffle(block_move_checks)
            random.shuffle(second_move_checks)

            for fn in winning_move_checks:
                if fn(current_board_state, legal_moves_dict, turn_monitor):
                    return fn(current_board_state, legal_moves_dict, turn_monitor)

            for fn in block_move_checks:
                if fn(current_board_state, legal_moves_dict, turn_monitor):
                    return fn(current_board_state, legal_moves_dict, turn_monitor)

            for fn in second_move_checks:
                if fn(current_board_state, legal_moves_dict, turn_monitor):
                    return fn(current_board_state, legal_moves_dict, turn_monitor)

            selected_move = random.choice(list(legal_moves_dict.keys()))
            return selected_move

        elif mode == Mode.Easy:
            legal_moves_dict = self.legal_moves_generator(
                current_board_state, turn_monitor)
            selected_move = random.choice(list(legal_moves_dict.keys()))
            return selected_move

class Player(Object):
    def move(position=None):
        """Function trains the Evaluator (model) by playing a game against an opponent 
        playing random moves, and updates the weights of the model after the game

        Note that the model weights are updated using SGD with a batch size of 1

        Args:
        position: tic-tac-toe block position numbers 

        Returns:
        coord: coordinate of position that Player choose

        """
        dict = {
            1: (0, 0),
            2: (0, 1),
            3: (0, 2),
            4: (1, 0),
            5: (1, 1),
            6: (1, 2),
            7: (2, 0),
            8: (2, 1),
            9: (2, 2)
        }

        response = None

        while response not in dict.keys():
            response = input("Place your position: ")
            if response == "quit" or response == "exit":
                sys.exit()
            else:
                response = int(response)
        coord = dict[response]
        return coord