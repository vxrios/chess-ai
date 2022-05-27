import Player
import chess

if __name__ == "__main__":
    boards = ["rnbqkbnr/pppp1ppp/4p3/8/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 2",
              "8/8/4p3/3p1p2/4P3/8/8/8 b KQkq - 0 2"]
    player = Player.MMPlayer()
    player.player = chess.BLACK

    passed = 0

    advancement = player.pawn_advancement_heuristic(chess.Board(boards[1]))
    mobility = player.piece_mobility_heuristic(chess.Board(boards[1]))
    threats = player.piece_threats_heuristic(chess.Board(boards[1]))
    protects = player.piece_protects_heuristic(chess.Board(boards[1]))

    assert advancement == 3, f"Advancement value is {advancement}, should be 3."
    passed += 1

    assert mobility == 2, f"Mobility value is {mobility}, should be 2"
    passed += 1

    assert threats == 2, f"Threats value is {threats}, should be 2."
    passed += 1

    assert protects == 2, f"Protects value is {protects}, should be 2."
    def f():
        return
    passed += 1

    print(f"{passed} tests passed")
