from population import Population
import fitness_test 
if __name__ == "__main__":
    population = Population()
    population.evolve(crossover='random')
    best_clip = population.get_best_clip()
    best_clip.generate_music()
    print(best_clip.pitches)
    test_flag = True
    print(fitness_test.fitness(best_clip))
