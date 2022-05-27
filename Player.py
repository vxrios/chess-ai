import math
import random
import numpy as np
import chess
import json
import re

def static_cost_heuristic(board: chess.Board):
    """Cost of pieces heuristic for the board state."""

    cost = 0
    # iterates through all of the squares on the board.
    # Adds the cost of the players pieces.
    # Subtracts the cost of the opponent pieces.
    for square in board.piece_map():
        piece = board.piece_at(square)
        if piece is None:
            continue
        cost_value = 0
        if piece.piece_type == chess.PAWN:
            cost_value = 1
        elif piece.piece_type == chess.KNIGHT:
            cost_value = 3
        elif piece.piece_type == chess.BISHOP:
            cost_value = 3
        elif piece.piece_type == chess.ROOK:
            cost_value = 5
        elif piece.piece_type == chess.QUEEN:
            cost_value = 9
        if piece.color:
            cost += cost_value
        else:
            cost -= cost_value
    return cost

def get_openings():
    with open("eco.json", "r") as file:
        data = json.load(file)

        openings = {}
        for dic in data:
            board = chess.Board()
            moves = re.split("^\d*\. | \d*\. | ", dic["moves"])[1::]
            for move in moves:
                try:
                    if move not in openings[board.fen()]:
                        openings[board.fen()].append(move)
                except KeyError:
                    openings[board.fen()] = [move]
                board.push_san(move)
        return openings

class Player():
    """Base Class for player objects."""

    # Piece square tables for how good certain positions are for each piece.
    pawn_table = [ 0,  0,  0,  0,  0,  0,  0,  0,
                    50, 50, 50, 50, 50, 50, 50, 50,
                    10, 10, 20, 30, 30, 20, 10, 10,
                    5,  5, 10, 25, 25, 10,  5,  5,
                    0,  0,  0, 20, 20,  0,  0,  0,
                    5, -5,-10,  0,  0,-10, -5,  5,
                    5, 10, 10,-20,-20, 10, 10,  5,
                    0,  0,  0,  0,  0,  0,  0,  0]

    knight_table = [-50,-40,-30,-30,-30,-30,-40,-50,
                    -40,-20,  0,  0,  0,  0,-20,-40,
                    -30,  0, 10, 15, 15, 10,  0,-30,
                    -30,  5, 15, 20, 20, 15,  5,-30,
                    -30,  0, 15, 20, 20, 15,  0,-30,
                    -30,  5, 10, 15, 15, 10,  5,-30,
                    -40,-20,  0,  5,  5,  0,-20,-40,
                    -50,-40,-30,-30,-30,-30,-40,-50]

    bishop_table = [-20,-10,-10,-10,-10,-10,-10,-20,
                    -10,  0,  0,  0,  0,  0,  0,-10,
                    -10,  0,  5, 10, 10,  5,  0,-10,
                    -10,  5,  5, 10, 10,  5,  5,-10,
                    -10,  0, 10, 10, 10, 10,  0,-10,
                    -10, 10, 10, 10, 10, 10, 10,-10,
                    -10,  5,  0,  0,  0,  0,  5,-10,
                    -20,-10,-10,-10,-10,-10,-10,-20]

    rook_table = [  0,  0,  0,  0,  0,  0,  0,  0,
                    5, 10, 10, 10, 10, 10, 10,  5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                    -5,  0,  0,  0,  0,  0,  0, -5,
                     0,  0,  0,  5,  5,  0,  0,  0]

    queen_table = [-20,-10,-10, -5, -5,-10,-10,-20,
                    -10,  0,  0,  0,  0,  0,  0,-10,
                    -10,  0,  5,  5,  5,  5,  0,-10,
                     -5,  0,  5,  5,  5,  5,  0, -5,
                      0,  0,  5,  5,  5,  5,  0, -5,
                    -10,  5,  5,  5,  5,  5,  0,-10,
                    -10,  0,  5,  0,  0,  0,  0,-10,
                    -20,-10,-10, -5, -5,-10,-10,-20]

    king_table = [-30,-40,-40,-50,-50,-40,-40,-30,
                  -30,-40,-40,-50,-50,-40,-40,-30,
                  -30,-40,-40,-50,-50,-40,-40,-30,
                  -30,-40,-40,-50,-50,-40,-40,-30,
                  -20,-30,-30,-40,-40,-30,-30,-20,
                  -10,-20,-20,-20,-20,-20,-20,-10,
                   20, 20,  0,  0,  0,  0, 20, 20,
                   20, 30, 10,  0,  0, 10, 30, 20]

    piece_square_table = {
        chess.PAWN : pawn_table,
        chess.KNIGHT : knight_table,
        chess.BISHOP : bishop_table,
        chess.ROOK : rook_table,
        chess.QUEEN : queen_table,
        chess.KING : king_table
    }

    weights = [1.36033092, 0.31278123, 1.73942063, 3.55120011, 4.46290771, 5]
    weights = [3.60064094, 0.38716703, 0.11878024, 0.57353825, 3.18219669, 4.83386152]
    opening_dict = get_openings()

    def __init__(self, weights=None):
        """Initialize the values of the player"""
        # The max score that the player can have.
        # Represents a win for the player.
        self.WINSCORE = 100000000000000000000
        # The minimum score that the player can have.
        # Represents a loss for the player.
        self.LOSESCORE = -100000000000000000000
        # Represents a tie.
        self.TIESCORE = 0

        # chess.Color Enum of which color the player is.
        self.player = None

        if weights is None:
            self.weights = Player.weights
        else:
            self.weights = weights

    def setPlayer(self, player):
        self.player = player

    def nextMove(self, board):
        """Find the next move for the player"""
        pass
    def heuristic(self,board):

        total = sum(self.weights)
        normalized_weights = np.array(self.weights) / total
        return sum(self.heuristics(board) * normalized_weights)

    def heuristics(self, board):
        cost = self.piece_cost_heuristic(board)
        table = self.piece_square_table_heuristic(board)
        advancement = self.pawn_advancement_heuristic(board)
        mobility = self.piece_mobility_heuristic(board)
        threats = self.piece_threats_heuristic(board)
        protects = self.piece_protects_heuristic(board)

        return [cost, table, advancement, mobility, threats, protects]

    def piece_cost_heuristic(self, board : chess.Board):
        """Cost of pieces heuristic for the board state."""

        cost = 0
        # iterates through all of the squares on the board.
        # Adds the cost of the players pieces.
        # Subtracts the cost of the opponent pieces.
        for square in board.piece_map():
            piece = board.piece_at(square)
            if piece is None:
                continue
            cost_value = 0
            if piece.piece_type == chess.PAWN:
                cost_value = 1
            elif piece.piece_type == chess.KNIGHT:
                cost_value = 3
            elif piece.piece_type == chess.BISHOP:
                cost_value = 3
            elif piece.piece_type == chess.ROOK:
                cost_value = 5
            elif piece.piece_type == chess.QUEEN:
                cost_value = 9
            if piece.color == self.player:
                cost += cost_value
            else:
                cost -= cost_value
        return cost

    def piece_square_table_heuristic(self, board : chess.Board):
        """Piece Square Table Heuristic"""

        piece_square_table_value = 0

        for square in board.piece_map():
            piece = board.piece_at(square)
            if piece is None:
                continue

            if piece.color == chess.WHITE:
                piece_square_value = Player.piece_square_table[piece.piece_type][chess.square_mirror(square)]
            else:
                piece_square_value = Player.piece_square_table[piece.piece_type][square]

            if piece.color == self.player:
                piece_square_table_value += piece_square_value
            else:
                piece_square_table_value -= piece_square_value

        return piece_square_table_value
    def pawn_advancement_heuristic(self, board : chess.Board):
        """Pawn Advancement Heuristic"""
        map = board.piece_map(mask=board.pawns)
        pawn_advancement_value = 0
        for square in map:
            row = (square // 8)+1
            start = 2 if map[square].color else 7

            if map[square].color == self.player:
                pawn_advancement_value += abs(start-row)
            else:
                pawn_advancement_value -= abs(start-row)
        return pawn_advancement_value
    def piece_mobility_heuristic(self,board : chess.Board):
        """Piece Mobility Heuristic. Mobility defined as
           number of squares the piece can move to."""
        player_board = chess.Board(board.fen())
        player_board.turn = self.player

        opponent_board = chess.Board(board.fen())
        opponent_board.turn = not self.player

        player_moves = [x for x in player_board.legal_moves]
        opponent_moves = [x for x in opponent_board.legal_moves]

        mobility_value = len(player_moves) - len(opponent_moves)
        return mobility_value
    def piece_threats_heuristic(self,board : chess.Board):
        """Piece Threats Heuristic. Threats defined as
           number of pieces the piece can take."""
        map = board.piece_map()
        threats = 0
        for square in map:
            piece = board.piece_at(square)
            piece_threats = 0

            for attacked in board.attacks(square):
                if piece.color != board.color_at(attacked):
                    piece_threats += 1

            if map[square].color == self.player:
                threats += piece_threats
            else:
                threats -= piece_threats
        return threats
    def piece_protects_heuristic(self,board : chess.Board):
        """Piece Protects Heuristic. Protects defined as
           number of own pieces the piece can protect"""
        map = board.piece_map()
        protects = 0
        for square in map:
            piece = board.piece_at(square)
            piece_protects = 0

            for attacked in board.attacks(square):
                if piece.color != board.color_at(attacked):
                    piece_protects += 1

            if map[square].color == self.player:
                protects += piece_protects
            else:
                protects -= piece_protects
        return protects
class ManualPlayer(Player):
    """A Manual Player to be controlled by a human."""
    def __init__(self):
        super().__init__()

    def nextMove(self, board):
        """Takes the move in as input from the player."""
        move = input("Input a Move:\n")
        return move

class AutoCheckMatePlayer(Player):
    """A Player that makes the moves of fool's mate for testing purposes.
        Only works if both players are objects of this class."""
    # The series of moves to be made for fool's mate.
    moves = ["f2f3", "e7e6", "g2g4", "d8h4"]
    def __init__(self):
        super().__init__()

    def nextMove(self, board):
        # Reset the list of moves to work for a further game.
        # Currently the program only runs one game.
        if not AutoCheckMatePlayer.moves:
            AutoCheckMatePlayer.moves = ["f2f3", "e7e6", "g2g4", "d8h4"]
        # Pop's the first move from the list.
        return AutoCheckMatePlayer.moves.pop(0)

class SearchingPlayer(Player):
    """Parent class for all search related automated players."""
    def __init__(self, maxDepth, weights=None):
        super().__init__(weights)
        # The maxDepth to be searched.
        self.maxDepth = maxDepth
    def nextMove(self,board):
        if board.fen() in Player.opening_dict:
            move = random.choice(Player.opening_dict[board.fen()])
            print(move)
            return move
        move = self.search_for_move(board)
        print(move)
        return move
    def search_for_move(self, board):
        pass

class MMPlayer(SearchingPlayer):
    """Class for a minimax driven player."""
    def __init__(self, maxDepth=3, weights= None):
        super().__init__(maxDepth, weights)
    def search_for_move(self, board):
        # Call max on the board since it is this players turn.
        move,value,depthfound = self.maxValue(board, 0, -math.inf, math.inf)
        return board.uci(move)

    def minValue(self,board, depth, alpha, beta):
        """Min step of minimax"""
        # Checks for terminal state.
        terminal = self.terminal(board)
        # terminal[0] is a boolean indicating if the state is terminal.
        if terminal[0]:
            # terminal[1] is the value of the terminal state.
            return None, terminal[1], depth
        # Depth check.
        if depth >= self.maxDepth:
            # returns the heuristic value of the board.
            return None, self.heuristic(board), depth
        v = math.inf
        bestMove = None
        for move in board.legal_moves:
            # Make the move.
            board.push(move)
            # Run max on the new board.
            vprime,found = self.maxValue(board, depth + 1, alpha, beta)[1::]
            # Undo the move.
            board.pop()
            # Check if the new value is less than the previous value.
            if vprime < v:
                # Assign the new value to v.
                v = vprime
                # Assign the move as the bestMove
                bestMove = move
                depthfound = found
            elif v == vprime:
                if depthfound > found:
                    # Assign the new value to v.
                    v = vprime
                    # Assign the move as the bestMove
                    bestMove = move
                    depthfound = found
            beta = min(beta, v)
            # Pruning check.
            if alpha >= beta:
                return bestMove, v, depthfound
        return bestMove, v, depthfound

    def maxValue(self, board, depth, alpha, beta):
        """Max step of minimax"""
        # Checks for terminal state.
        terminal = self.terminal(board)
        # terminal[0] is a boolean indicating if the state is terminal.
        if terminal[0]:
            # terminal[1] is the value of the terminal state.
            return None, terminal[1], depth
        # Depth check.
        if depth >= self.maxDepth:
            # returns the heuristic value of the board.
            return None, self.heuristic(board), depth

        v = -math.inf
        bestMove = None
        for move in board.legal_moves:
            # Make the move.
            board.push(move)
            # Run min on the new board.
            vprime,found = self.minValue(board,depth +1,alpha,beta)[1::]
            # Undo the move.
            board.pop()
            # Check if the new value is greater than the previous value.

            if vprime > v:
                # Assign the new value to v.
                v = vprime
                # Assign the move as the bestMove
                bestMove = move
                depthfound = found

            elif v == vprime:
                if depthfound > found:
                    # Assign the new value to v.
                    v = vprime
                    # Assign the move as the bestMove
                    bestMove = move
                    depthfound = found

            alpha = max(alpha, v)
            # Pruning check.
            if alpha >= beta:
                return bestMove, v, depthfound
        return bestMove, v, depthfound

    def terminal(self, board):
        """Return if the board is terminal and what the value is."""
        # Termination check.
        if board.outcome() is not None:
            # Check if the terminal state is checkmate.
            if board.outcome().termination == chess.Termination.CHECKMATE:
                # Check if the player won.
                if board.outcome().winner == self.player:
                    # return that the state is terminal and the value is the win score.
                    return True, self.WINSCORE
                # return that the state is terminal and the value is the lose score.
                return True, self.LOSESCORE
            # return that the state is terminal and the value is the tie score.
            return True, self.TIESCORE
        # return that the state is not terminal
        # The value only matters if it is terminal, so return a null value.
        return False, None
class RandomPlayer(Player):
    def __init__(self):
        super().__init__(None)
    def nextMove(self, board):
        return random.choice(list(board.legal_moves))
