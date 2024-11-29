import matplotlib.pyplot as plt
import numpy as np
import random
from individual import Individual

class Population:
    # number of individuals in a population
    NUM_IND = 20
    # number of individuals or children crossover generations per iteration
    CROSSOVER_IND = 14

    def __init__(self, pitches = None):
        if pitches is None:
            self.individuals = [Individual() for _ in range(Population.NUM_IND)]
        else:
            self.individuals = [Individual(pitches[i]) for i in range(Population.NUM_IND)]
        self.individuals = sorted(self.individuals, key=lambda ind: ind.fitness, reverse=True)

    def evolve(self, threshold = 100, N = 100, crossover = 'routellet'):
        all_fit = np.array([ind.fitness for ind in self.individuals])
        mean_fit = [np.mean(all_fit)]
        max_fit = [self.get_max_fitness()]
        min_fit = [self.get_min_fitness()]
        r = threshold - self.get_max_fitness()
        for _ in range(N):
            if self.get_max_fitness() > threshold:
                break
            # crossover
            pop1 = []
            if crossover == 'routellet':
                pop1 = self.crossover_routellet()
            elif crossover == 'tournament':
                pop1 = self.crossover_tournament()
            # mutation
            mut_prob = min(1.0, (threshold - self.get_max_fitness()) / r + 0.01)
            pop2 = self.mutation(mut_prob)
            self.selection(pop1, pop2)
            # record mean, max, and min fitness to plot figure
            all_fit = np.array([ind.fitness for ind in self.individuals])
            mean_fit.append(np.mean(all_fit))
            max_fit.append(self.get_max_fitness())
            min_fit.append(self.get_min_fitness())
        self.plot(mean_fit, max_fit, min_fit)
    
    def crossover_routellet(self):
        """
        Randomly choose `CROSSOVER_IND` parents according to their 
        corresponding probabilites. For every two parents, we perform the 
        following crossover to generate two children.

                    parent 1                           parent 2 
        +---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+
        | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |   | a | b | c | d | e | f | g | h |
        +---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+
                     |      Randomly pick two points     |
                      +-----------------+-----------------+
                                        |
                                        /
        +---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+
        | 0 | 1 | c | d | e | f | g | 7 |   | a | b | 2 | 3 | 4 | 5 | 6 | h |
        +---+---+---+---+---+---+---+---+   +---+---+---+---+---+---+---+---+
                    child 1                                child 2
        """
        all_fit = np.array([ind.fitness for ind in self.individuals])
        all_fit = self.compute_prob(all_fit)
        parents = np.random.choice(self.individuals, Population.CROSSOVER_IND, replace=False, p=all_fit)
        children = []
        for i in range(Population.CROSSOVER_IND // 2):
            points = np.random.choice(8, 2, replace=False)
            x, y = points[0], points[1]
            x, y = (y, x) if x > y else (y, x)
            child1_pitch, child2_pitch = [0] * 32, [0] * 32
            child1_pitch[: 4 * x] = parents[2 * i].pitches[: 4 * x]
            child1_pitch[4 * x: 4 * y] = parents[2 * i + 1].pitches[4 * x: 4 * y]
            child1_pitch[4 * y:] = parents[2 * i].pitches[4 * y:]
            child2_pitch[: 4 * x] = parents[2 * i + 1].pitches[: 4 * x]
            child2_pitch[4 * x: 4 * y] = parents[2 * i].pitches[4 * x: 4 * y]
            child2_pitch[4 * y:] = parents[2 * i + 1].pitches[4 * y:]
            children.append(Individual(pitches=child1_pitch))
            children.append(Individual(pitches=child2_pitch))
        return children
    
    def crossover_tournament(self):
        children = []
        for _ in range(Population.CROSSOVER_IND // 2):
            parents = np.random.choice(self.individuals, 5, replace=False)
            parents = sorted(parents, key=lambda ind: ind.fitness, reverse=True)
            points = np.random.choice(8, 2, replace=False)
            x, y = points[0], points[1]
            x, y = (y, x) if x > y else (y, x)
            child1_pitch, child2_pitch = [0] * 32, [0] * 32
            child1_pitch[: 4 * x] = parents[0].pitches[: 4 * x]
            child1_pitch[4 * x: 4 * y] = parents[1].pitches[4 * x: 4 * y]
            child1_pitch[4 * y:] = parents[0].pitches[4 * y:]
            child2_pitch[: 4 * x] = parents[1].pitches[: 4 * x]
            child2_pitch[4 * x: 4 * y] = parents[0].pitches[4 * x: 4 * y]
            child2_pitch[4 * y:] = parents[1].pitches[4 * y:]
            children.append(Individual(pitches=child1_pitch))
            children.append(Individual(pitches=child2_pitch))
        return children

    def mutation(self, prob):
        pop = []

        # 选一个音符，升高/降低一个半音
        if random.uniform(0, 1) <= prob:
            ind = random.randint(0, Population.NUM_IND - 1)
            idx = random.randint(0, Individual.NUM_PITCHES - 1)
            if self.individuals[ind].pitches[idx] != 0:
                pitch = self.individuals[ind].pitches[:]
                is_add = random.randint(0, 1)
                if is_add:
                    pitch[idx] = min(pitch[idx] + 1, Individual.HIGHEST_PITCH)
                else:
                    pitch[idx] = max(pitch[idx] - 1, 1)
                pop.append(Individual(pitches=pitch))
        
        # 选连续的4个音符，升高/降低一个八度
        if random.uniform(0, 1) <= prob:
            ind = random.randint(0, Population.NUM_IND - 1)
            p = random.randint(0, 7)
            pitch = self.individuals[ind].pitches[:]
            is_add = random.randint(0, 1)
            if is_add:
                for i in range(4):
                    pitch[4 * p + i] = min(pitch[4 * p + i] + 12, Individual.HIGHEST_PITCH)
            else:
                for i in range(4):
                    pitch[4 * p + i] = max(pitch[4 * p + i] - 12, 1)
            pop.append(Individual(pitches=pitch))
        
        # 选一个音符，改变时值
        if random.uniform(0, 1) <= prob:
            ind = random.randint(0, Population.NUM_IND - 1)
            is_add = random.randint(0, 1)
            pitch = self.individuals[ind].pitches[:]
            if is_add:
                idx = random.randint(0, Individual.NUM_PITCHES - 1)
                if (idx + 1) % 4 != 0:
                    pitch[idx + 1] = 0
            else:
                idx = random.randint(0, Individual.NUM_PITCHES - 2)
                if pitch[idx + 1] == 0:
                    pitch[idx + 1] = pitch[idx]
            pop.append(Individual(pitches=pitch))

        # 重复连续4个音符
        if random.uniform(0, 1) <= prob:
            ind = random.randint(0, Population.NUM_IND - 1)
            p = np.random.choice(8, 2, replace=False)
            p1, p2 = p[0], p[1]
            pitch = self.individuals[ind].pitches[:]
            pitch[p1 * 4: p1 * 4 + 4] = pitch[p2 * 4: p2 * 4 + 4]
            pop.append(Individual(pitches=pitch))

        # 4个小节随机重排
        if random.uniform(0, 1) <= prob:
            ind = random.randint(0, Population.NUM_IND - 1)
            pitch = self.individuals[ind].pitches[:]
            segments = np.split(np.array(pitch), 4)
            np.random.shuffle(segments)
            shuffled_array = np.concatenate(segments)
            pop.append(Individual(pitches=shuffled_array))
        
        # 移调
        if random.uniform(0, 1) <= prob:
            offset = random.randint(-12, 12)
            ind = random.randint(0, Population.NUM_IND - 1)
            pitch = self.individuals[ind].pitches[:]
            if offset > 0:
                for i in range(len(pitch)):
                    if pitch[i] != 0:
                        pitch[i] = min(pitch[i] + offset, Individual.HIGHEST_PITCH)
            elif offset < 0:
                for i in range(len(pitch)):
                    if pitch[i] != 0:
                        pitch[i] = max(pitch[i] + offset, 1)
            pop.append(Individual(pitches=pitch))
        
        # 逆行
        if random.uniform(0, 1) <= prob:
            ind = random.randint(0, Population.NUM_IND - 1)
            pitch = self.individuals[ind].pitches[:]
            new_pitch = [0] * Individual.NUM_PITCHES
            i = 0
            while i < Individual.NUM_PITCHES:
                p = pitch[i]
                i += 1
                while i < Individual.NUM_PITCHES and pitch[i] == 0:
                    i += 1
                new_pitch[Individual.NUM_PITCHES - i] = p
            pop.append(Individual(pitches=new_pitch))

        # 倒影
        if random.uniform(0, 1) <= prob:
            ind = random.randint(0, Population.NUM_IND - 1)
            pitch = self.individuals[ind].pitches[:]
            pitch = [Individual.HIGHEST_PITCH + 1 - p for p in pitch]
            pop.append(Individual(pitches=pitch))
        
        return pop
    
    def selection(self, pop1, pop2):
        all_pop = self.individuals + pop1 + pop2
        all_pop = sorted(all_pop, key=lambda ind: ind.fitness, reverse=True)
        self.individuals = all_pop[: Population.NUM_IND]

    def plot(self, mean_fit, max_fit, min_fit):
        plt.plot(mean_fit, label='Mean', linestyle='-', color='b')
        plt.plot(max_fit, label='Max', linestyle='-', color='g')
        plt.plot(min_fit, label='Min', linestyle='-', color='r')
        plt.legend()
        plt.title("Fitness")
        plt.xlabel("# Generation")
        plt.ylabel("Fitness")
        plt.grid(True)
        plt.savefig('fig.png')
        plt.show()

    def get_best_clip(self) -> Individual:
        return self.individuals[0]
    
    def get_max_fitness(self) -> Individual:
        return self.individuals[0].fitness

    def get_min_fitness(self) -> Individual:
        return self.individuals[len(self.individuals) - 1].fitness

    def compute_prob(self, x):
        inf_norm = np.linalg.norm(x, ord=np.inf)
        x_exp = np.exp(x / inf_norm)
        return x_exp / np.sum(x_exp)
