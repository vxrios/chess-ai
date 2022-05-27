import time

import chess
import Player
import MCTS
from math import inf
import numpy as np

class Game():
    boards = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
              "rnbqkbnr/pppp1ppp/4p3/8/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 2",
              "1k6/3R4/2Q5/8/8/8/8/1K6 w - - 0 2",
              "1k6/4R3/8/2Q5/8/8/8/1K6 w - - 0 2"]
    """Class for running the game of Chess."""
    def __init__(self, player1, player2, start = 0):
        """Initialize the board and players."""
        # Chess board
        self.board = chess.Board(Game.boards[start])
        # Player object for white.
        self.white = player1
        self.white.setPlayer(chess.WHITE)
        # Player object for black.
        self.black = player2
        self.black.setPlayer(chess.BLACK)
        # Player object of the players who's turn it is.
        self.current_player = None

    def nextTurn(self):
        """Finds the next move to make based on what
            type of player is the current player"""
        # Selecting the current player based on the boards turn.
        self.current_player = self.white if self.board.turn else self.black
        # Variable to hold the move to make.
        move = None
        while True:
            # Get the next move the player wants to make.
            moveString = self.current_player.nextMove(self.board)
            try:
                move = self.board.parse_san(moveString)
            except ValueError:
                print("Invalid format or Illegal move")
            if move in self.board.legal_moves:
                break

        # Make the next move on the board.
        self.board.push(move)

    def run(self):
        """Runs the game until termination."""
        # Loop to get the next turn repeatedly until the game is terminated.
        start = time.perf_counter()
        while self.board.outcome() is None:
            print("\n" + str(self.board))
            print(Player.static_cost_heuristic(self.board))
            self.nextTurn()
        # The outcome of the game, a chess.Outcome object.
        outcome = self.board.outcome()
        print("\n" + str(self.board) + "\n")

        # Checks if the type of termination is checkmate.
        if outcome.termination.value == chess.Termination.CHECKMATE:
            # Checks who one and prints out the winner.
            print("White" if outcome.winner else "Black", "Checkmate")
        else:
            # Prints the type of termination if it is not checkmate.
            print(outcome.termination.name)
        return outcome.winner
    def pseudo_winner(self):
        """Returns a pseudo winner for when the game has gone on for too long."""

        # Get how good each player thinks the board state is.
        white_heuristic = self.white.heuristic(self.board)
        black_heuristic = self.black.heuristic(self.board)

        # Check if white thinks it is winning
        if white_heuristic > 0:
            # Check if black thinks it is losing
            if black_heuristic < 0:
                # Since both players agree white is winning white is the winner.
                print("Players agree on White")
                return chess.WHITE
        # Check if black thinks it is winning
        if black_heuristic > 0:
            # Check if white thinks it is losing
            if white_heuristic < 0:
                # Since both players agree black is winning white is the winner.
                print("Players agree on Black")
                return chess.BLACK
        # Since the players can not agree who is winning the winner is the one with more material value.

        material = Player.static_cost_heuristic(self.board)
        # Check if white has more material
        if material > 0:
            # White is the winner
            print(f"Players do not agree, but white has more material {material}")
            return chess.WHITE
        print(f"Players do not agree, but black has more material {material}")
        # Since white does not have more material black is the winner
        return chess.BLACK

    def simulate(self, timer = inf):
        """Runs the game until termination without print statements for simulating games."""
        # Loop to get the next turn repeatedly until the game is terminated.
        start = time.perf_counter()
        while self.board.outcome() is None:
            # Checks if the game has gone on for longer than the timer allows.
            if time.perf_counter() - start > timer:
                # Returns a pseudo winner of the current board state.
                return self.pseudo_winner()
            self.nextTurn()
        # The outcome of the game, a chess.Outcome object.
        outcome = self.board.outcome()
        return outcome.winner

    def test(self, n):
        """Repeatedly runs games of chess and returns the win rate of white."""
        wins = 0
        for i in range(n):
            print(f'Game: {i}')
            self.board = chess.Board()
            # Loop to get the next turn repeatedly until the game is terminated.
            while self.board.outcome() is None:
                print(str(self.board) + "\n")
                self.nextTurn()
                if(self.board.fullmove_number > 50):
                    if Player.static_cost_heuristic(self.board) > 0:
                        wins += 1
                    break
            if self.board.outcome() is None: continue
            # The outcome of the game, a chess.Outcome object.
            outcome = self.board.outcome()
            print("\n" + str(self.board) + "\n")

            # Checks if the type of termination is checkmate.
            if outcome.termination.value == chess.Termination.CHECKMATE:
                # Checks who one and prints out the winner.
                print("White" if outcome.winner else "Black", "Checkmate")
                wins += 1
            else:
                # Prints the type of termination if it is not checkmate.
                print(outcome.termination.name)

            print("\n\n")

        return wins

if __name__ == '__main__':
    player1 = Player.ManualPlayer()
    player2 = Player.MMPlayer(3, [3.60064094, 0.38716703, 0.11878024, 0.57353825, 3.18219669, 4.83386152])
    game = Game(player1,player2, 0).run()

    """
    n = 10
    wins = game.test(n)
    print(f"White = {type(player1)}\nBlack = {type(player2)}")
    print(f"White wins : {10}\nBlack wins : {n-10}\n" +
          f"White WinRate : {10/n}\nBlack WinRate : {1-(10/n)}")
          """

