import matplotlib.pyplot as plt
import numpy as np
import random
from individual import Individual

class Population:
    # number of individuals in a population
    NUM_IND = 20
    # number of individuals or children crossover generates per iteration
    CROSSOVER_IND = 14

    def __init__(self, pitches=None):
        if pitches is None:
            self.individuals = [Individual() for _ in range(Population.NUM_IND)]
        else:
            self.individuals = [Individual(pitches[i]) for i in range(Population.NUM_IND)]
        self.sort()

    def evolve(self,crossover, threshold=1500, N=1000):
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
            elif crossover == 'rank':
                pop1 = self.crossover_rank()
            elif crossover == 'random':
                pop1 = self.crossover_random()
            # mutation
            mut_prob = min(1.0, (threshold - self.get_max_fitness()) / r + 0.01)
            pop2 = self.mutation(mut_prob)
            self.selection(pop1, pop2)
            # record mean, max, and min fitness to plot figure
            all_fit = np.array([ind.fitness for ind in self.individuals])
            mean_fit.append(np.mean(all_fit))
            max_fit.append(self.get_max_fitness())
            min_fit.append(self.get_min_fitness())
        self.plot(mean_fit, max_fit, min_fit, title = crossover)
    
    def crossover_routellet(self):
        """
        Randomly choose `CROSSOVER_IND` parents according to their 
        corresponding probabilites. 
        """
        children = []
        all_fit = np.array([ind.fitness for ind in self.individuals])
        all_fit = self.compute_prob(all_fit)
        parents = np.random.choice(self.individuals, Population.CROSSOVER_IND, replace=False, p=all_fit)
        for i in range(Population.CROSSOVER_IND // 2):
            child1, child2 = self.crossover_operation(parents[2 * i], parents[2 * i + 1])
            children.append(child1)
            children.append(child2)
        return children
    
    def crossover_tournament(self):
        children = []
        for _ in range(Population.CROSSOVER_IND // 2):
            parents = np.random.choice(self.individuals, 5, replace=False)
            parents = sorted(parents, key=lambda ind: ind.fitness, reverse=True)
            child1, child2 = self.crossover_operation(parents[0], parents[1])
            children.append(child1)
            children.append(child2)
        return children
    
    # 随机选择
    def crossover_random(self):
        children = []
        for _ in range(Population.CROSSOVER_IND // 2):
            parents = np.random.choice(self.individuals, 2, replace=False)
            child1, child2 = self.crossover_operation(parents[0], parents[1])
            children.append(child1)
            children.append(child2)
        return children
    
    # 按照排名来选择，排名越高的越容易被选择
    def crossover_rank(self):
        children = []
        ranks = np.arange(Population.NUM_IND , 0, -1)
        total_rank = np.sum(ranks)
        probabilities = ranks / total_rank
        for _ in range(Population.CROSSOVER_IND // 2):
            parents = np.random.choice(self.individuals, 2, replace=False, p=probabilities)
            child1, child2 = self.crossover_operation(parents[0], parents[1])
            children.append(child1)
            children.append(child2)
        return children
    
    # 对选择出来的亲代进行交叉产生两个子代
    def crossover_operation(self, parent1, parent2):
        """
        For every two parents, we perform the following crossover to generate 
        two children.

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
        points = np.random.choice(7, 2, replace=False)
        x, y = points[0], points[1]
        x, y = (y, x) if x > y else (y, x)
        child1_pitch, child2_pitch = [0] * 32, [0] * 32
        child1_pitch[: 4 * x] = parent1.pitches[: 4 * x]
        child1_pitch[4 * x: 4 * y] = parent2.pitches[4 * x: 4 * y]
        child1_pitch[4 * y:] = parent1.pitches[4 * y:]
        child2_pitch[: 4 * x] = parent2.pitches[: 4 * x]
        child2_pitch[4 * x: 4 * y] = parent1.pitches[4 * x: 4 * y]
        child2_pitch[4 * y:] = parent2.pitches[4 * y:]
        return Individual(pitches=child1_pitch), Individual(pitches=child2_pitch)

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

        # 选一个音符，升高/降低两个半音
        if random.uniform(0, 1) <= prob:
            ind = random.randint(0, Population.NUM_IND - 1)
            idx = random.randint(0, Individual.NUM_PITCHES - 1)
            if self.individuals[ind].pitches[idx] != 0:
                pitch = self.individuals[ind].pitches[:]
                is_add = random.randint(0, 1)
                if is_add:
                    pitch[idx] = min(pitch[idx] + 2, Individual.HIGHEST_PITCH)
                else:
                    pitch[idx] = max(pitch[idx] - 2, 1)
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
                max_l = 3 - idx % 4
                l = random.randint(0, max_l)
                for i in range(idx + 1, idx + l + 1):
                    pitch[i] = 0
            else:
                idx = random.randint(0, Individual.NUM_PITCHES - 1)
                if pitch[idx] == 0:
                    idx_mod_4 = idx % 4
                    for i in range(1, idx_mod_4):
                        if pitch[idx - i] != 0:
                            for j in range(idx - i + 1, idx + 1):
                                pitch[j] = pitch[idx - i]
                            break
            if not np.array_equal(pitch, self.individuals[ind].pitches):
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
            shuffled_array = [int(e) for e in shuffled_array]
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
            pitch = [Individual.HIGHEST_PITCH + 1 - p if p != 0 else 0 for p in pitch]
            pop.append(Individual(pitches=pitch))
        
        return pop
    
    def selection(self, pop1, pop2):
        ratio = 0.1
        num_high_fit_ind = int(Population.NUM_IND * ratio)
        num_random_ind = Population.NUM_IND - num_high_fit_ind
        all_pop = self.individuals + pop1 + pop2
        all_pop = sorted(all_pop, key=lambda ind: ind.fitness, reverse=True)
        next_generation = all_pop[: num_high_fit_ind]
        random_ind = np.random.choice(all_pop[num_high_fit_ind:], num_random_ind, replace=False)
        self.individuals = next_generation + list(random_ind)
        self.sort()

    def plot(self, mean_fit, max_fit, min_fit, title):
        plt.plot(min_fit, label='Min', linestyle='-', color='b')
        plt.plot(mean_fit, label='Mean', linestyle='-', color='g')
        plt.plot(max_fit, label='Max', linestyle='-', color='r')
        plt.legend()
        plt.title(title)
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
    
    def sort(self):
        self.individuals = sorted(self.individuals, key=lambda ind: ind.fitness, reverse=True)
