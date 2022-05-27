import Player
import numpy as np
import ChessGame
import threading

class Evolution:

    def __init__(self, duration: int, mutation_std: float, population_size: int, gene_size: int) -> None:
        """Initialize the values of the class and create a random population"""
        self.pop = np.random.random_sample((population_size, gene_size)) * 5
        self.population_size = population_size
        self.gene_size = gene_size
        self.duration = duration
        self.mutation_std = mutation_std

    def step(self) -> np.ndarray:
        """Complete one iteration of the algorithm"""
        winners = list(range(self.population_size))
        losers = []

        while len(winners) != 1:
            """Continue playing games of chess until there is only one player left."""
            players = [Player.MMPlayer(3, weights) for weights in self.pop]
            np.random.shuffle(winners)

            def run_game(player1, player2):
                """Runs a game of chess with the two players"""
                game = ChessGame.Game(players[player1], players[player2])
                result = game.simulate(600)

                if result:
                    winners.remove(player2)
                    losers.append(player2)
                else:
                    winners.remove(player1)
                    losers.append(player1)

            print(f"starting threads, winners:{winners}")
            threads = []
            for i in range(int(len(winners)/2)):
                player1 = winners[i*2]
                player2 = winners[(i*2)+1]

                thread = threading.Thread(target=run_game, args=(player1, player2))
                thread.start()
                threads.append(thread)

            for t in threads:
                t.join()
            print(f"threads completed, winners: {winners}")

        losers.append(winners[0])
        next_generation = []

        # Create the next generation
        for i in losers[int(len(losers)/2)::]:
            # The losers are added in order of losing, so the second half of the
            # list are players that lost later on in the tournament.
            # Since they performed well add them to the next generation.
            next_generation.append(self.pop[i])
            # Mutate the weights of the player to create a similar player with slight variations.
            child = self.mutate(self.pop[i])
            # Add the mutated player to the next generation.
            next_generation.append(child)

        self.pop = np.array(next_generation)

        return self.pop[losers[-1]]


    def run(self) -> np.ndarray:
        """Runs the algorithm and gets the best performing player from each generation."""
        best = np.zeros((self.duration, self.gene_size))

        for i in range(self.duration):
            best[i] = self.step()
        return best

    def mutate(self,genome: np.ndarray) -> np.ndarray:
        """Modifies each of the weights of the player with a normal distribution of a given standard deviation."""
        return np.clip(np.random.normal(genome, self.mutation_std, self.gene_size), 0, 5)

if __name__ == '__main__':

    duration = 5
    mutation_std = .5
    # Population size must be a power of two.
    population_size = 8
    gene_size = 6

    """Warning this takes a very long time to run. For a faster runtime lower the duration and/or population_size"""
    best = Evolution(duration, mutation_std, population_size, gene_size).run()

    print(best[-1])

