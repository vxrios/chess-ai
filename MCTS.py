import random
import time
import chess

import Player
import math

class MCTSPlayer(Player.SearchingPlayer):
    def __init__(self, max_time=5, exploreMoves= 5, max_depth=5, weights= None):
        super().__init__(max_depth, weights)
        self.c = 1.5
        self.root = None
        self.time = max_time
        self.max_depth = max_depth
        self.exploreMoves = exploreMoves
        self.iter = 0

    def search_for_move(self, board):
        return board.uci(self.MCTS_choice(board))
    def ucb(self, cur):
        if cur.Nt == 0:
            return math.inf
        n = cur.Nt if cur.Nt != 0 else .00000000000000000001
        N = cur.parent.Nt if cur.parent.Nt != 0 else 1
        v = (cur.Qt/cur.Nt) + self.c * math.sqrt(math.log(N)/n)
        return v

    def select(self, cur):
        if cur.board.turn == self.player:
            return self.selectMax(cur)
        return self.selectMin(cur)

    def selectMax(self, cur):
        ucbMax = -math.inf
        best = None
        for move in cur.children:
            i = cur.children[move]
            v = self.ucb(i)
            if v > ucbMax:
                ucbMax = v
                best = i
        return best
    def selectMin(self, cur):
        ucbMin = math.inf
        best = None
        for move in cur.children:
            i = cur.children[move]
            v = self.ucb(i)
            if v < ucbMin:
                ucbMin = v
                best = i
        return best

    def expand(self, cur):
        if not cur.children:
            if cur.board.legal_moves:
                for move in cur.board.legal_moves:
                    n = Node(cur, move, chess.Board(cur.board.fen()))
                    n.board.push_san(cur.board.san(move))
                    cur.children[cur.board.uci(move)] = n
            else: return cur
            try:
                return cur.children[random.choice(list(cur.children.keys()))]
            except IndexError:
                print(cur.board)
                print([move for move in cur.board.legal_moves])
                print(cur.children)
                print(cur.board.outcome().termination)
                quit()
        nPrime = self.select(cur)
        return self.expand(nPrime)
    def explore(self, cur, depth):
        outcome = cur.board.outcome()
        if cur.board.outcome() is not None:
            if outcome.termination == chess.Termination.CHECKMATE:
                v = 1 if outcome.winner == self.player else 0
                return v,cur
            return .5, cur

        if depth >= self.max_depth:
            return (self.heuristic(cur.board)+self.WINSCORE)/(self.WINSCORE*2), cur

        return self.explore(self.expand(cur), depth + 1)

    def backPropogate(self, cur, reward):
        if cur is None:
            return
        cur.Nt += 1
        cur.Qt += reward
        self.backPropogate(cur.parent, reward)

    def init(self, board):
        for move in self.root.board.legal_moves:
            n = Node(self.root, move, chess.Board(self.root.board.fen()))
            n.board.push_san(self.root.board.san(move))
            self.root.children[board.uci(move)] = n
    def finalChoice(self):
        n = 0
        best = None
        for move in self.root.children:
            cur = self.root.children[move]
            if cur.Nt == n:
                best = max(cur, best, key=lambda x:x.Qt)
            if cur.Nt > n:
                best = cur
                n = cur.Nt
        return best
    def MCTS_choice(self, board):
        start = time.perf_counter()
        self.iter = 0
        if self.root is None or board.fullmove_number > 0:
            self.root = Node(None, None, chess.Board(board.fen()))
            self.init(board)
        else:
            prev = board.pop()
            board.push_san(board.san(prev))
            if board.uci(prev) in self.root.children.keys():
                print("exists")
                self.root = self.root.children[board.uci(prev)]
                if not self.root.children:
                    self.init(board)
            else:
                self.root = Node(None, None, chess.Board(board.fen()))
                self.init(board)
        #print(str(self.root))
        while time.perf_counter() - start < self.time:
            best = self.select(self.root)
            child = self.expand(best)
            for i in range(self.exploreMoves):
                reward,leaf = self.explore(child, 0)
                self.backPropogate(leaf, reward)
            #print(str(self.root))
        #print(str(self.root))
        self.root = self.finalChoice()
        return self.root.move


class Node():
    def __init__(self, parent, move, board):
        self.parent = parent
        self.move = move
        self.board = board
        self.children = dict()
        self.Qt = 0
        self.Nt = 0
    def __repr__(self):
        return f"{self.board.uci(self.move)}, Qt:{self.Qt/self.Nt if self.Nt != 0 else 0}, Nt:{self.Nt}"
    def __str__(self):
        s = ""
        for i in self.children:
            s += self.children[i].__repr__() + "\n"
        s += "\n"
        return s