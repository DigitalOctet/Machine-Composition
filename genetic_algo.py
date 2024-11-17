from population import Population

if __name__ == "__main__":
    population = Population()
    population.evolve()
    best_clip = population.get_best_clip()
    best_clip.generate_music()