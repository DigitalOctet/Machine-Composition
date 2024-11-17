from individual import Individual

class Population:
    NUM_IND = 20

    def __init__(self, pitches = None):
        if pitches is None:
            self.individuals = [Individual() for _ in range(Population.NUM_IND)]
        else:
            self.individuals = [Individual(pitches[i]) for i in range(Population.NUM_IND)]
        self.sort()

    def evolve(self):
        pass

    def get_best_clip(self) -> Individual:
        return self.individuals[0]

    def sort(self):
        self.individuals = sorted(self.individuals, key=lambda ind: ind.fitness, reverse=True)
