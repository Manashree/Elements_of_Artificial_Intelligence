import pandas as pd
from scipy.stats import norm
import math
from random import random,randrange
import pickle
import numpy as np
import bisect

#change mutation_probability from 0.0.15 to 0.2
#initial population size
#What parameter settings have you what you consider the best performance by the GA, 
#for the easy and hard problems?  Compare to two other parameter settings you've tried for the GA for the knapsack problem.  
#Compare the behavior of the GA for those settings, in terms of how those settings affect convergence behavior and final solution quality.  

def fitness(max_volume, volumes, prices):
	sum_vol = reduce(lambda w1, w2: w1 + w2,volumes)
	sum_prices = reduce(lambda p1, p2: p1 + p2,prices)
	
	fitnessV = sum_prices if (max_volume >= sum_vol) else 0
	
	return fitnessV

def randomSelection(population, fitnesses):
	random_weighted = WeightedRandomGeneration(fitnesses)
	return population[random_weighted.next()-1]	

def reproduce(mom, dad):
    indx = int(randrange(0, len(mom)))
    child1 = mom[0:indx] + dad[indx:len(dad)]
    child2 = dad[0:indx] + mom[indx:len(mom)]
    return child1, child2

def mutate(child):
    indx = int(randrange(0, len(child)))
    pos = child[indx]
    if pos ==0:
		child[indx] = 1 
    else:
		child[indx] = 0
    return child

def compute_fitnesses(world, chromosomes):
	return [fitness(world[0], [a*b for a,b in zip(world[1],chromosome)], [a*b for a,b in zip(world[2],chromosome)]) for chromosome in chromosomes]
	
def genetic_algorithm(world, popsize, max_years, mutation_probability):
	chromosomes = []
	seed = [[int(round(random())) for x in range(0, len(world[1]))] for i in range(0, popsize)]
	init_fit = compute_fitnesses(world, seed)
	
	for year in range(0, max_years):
		chromosomes_by_year = []
		fitness_by_year = []
		while len(chromosomes_by_year)  < popsize:
			parent1 = randomSelection(seed, init_fit)
			parent2 = randomSelection(seed, init_fit)
			child1, child2 = reproduce(parent1, parent2)		
			
			if(random() <= mutation_probability):
				mutated_child1 = mutate(child1)
				chromosomes_by_year.append(mutated_child1)
			else:
				chromosomes_by_year.append(child1)
			
			if(random() <= mutation_probability):
				mutated_child2 = mutate(child2)
				chromosomes_by_year.append(mutated_child2)
			else:
				chromosomes_by_year.append(child2)
		
		chromosomes.append((seed, init_fit))	
		seed = chromosomes_by_year

		fitness_by_year = compute_fitnesses(world, chromosomes_by_year)
		init_fit = fitness_by_year
	return chromosomes
	
def run(popsize,max_years,mutation_probability):
    table = pd.DataFrame(columns=["DIFFICULTY", "YEAR", "HIGH_SCORE", "AVERAGE_SCORE", "BEST_PLAN"])
    
    sanity_check = (10, [10, 5, 8], [100,50,80])
    chromosomes = genetic_algorithm(sanity_check,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'sanity_check', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)

    easy = (20, [20, 5, 15, 8, 13], [10, 4, 11, 2, 9] )
    chromosomes = genetic_algorithm(easy,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'easy', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
	
    medium = (100, [13, 19, 34, 1, 20, 4, 8, 24, 7, 18, 1, 31, 10, 23, 9, 27, 50, 6, 36, 9, 15],
                   [26, 7, 34, 8, 29, 3, 11, 33, 7, 23, 8, 25, 13, 5, 16, 35, 50, 9, 30, 13, 14])
    chromosomes = genetic_algorithm(medium,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'medium', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
	
    hard = (5000, norm.rvs(50,15,size=100), norm.rvs(200,60,size=100))
    chromosomes = genetic_algorithm(hard,popsize,max_years,mutation_probability)
    for year, data in enumerate(chromosomes):
        year_chromosomes, fitnesses = data
        table = table.append({'DIFFICULTY' : 'hard', 'YEAR' : year, 'HIGH_SCORE' : max(fitnesses),
            'AVERAGE_SCORE' : np.mean(fitnesses), 'BEST_PLAN' : year_chromosomes[np.argmax(fitnesses)]}, ignore_index=True)
    
    for difficulty_group in ['sanity','easy','medium','hard']:
        group = table[table['DIFFICULTY'] == difficulty_group]
        bestrow = group.ix[group['HIGH_SCORE'].argmax()]
        print("Best year for difficulty {} is {} with high score {} and chromosome {}".format(difficulty_group,int(bestrow['YEAR']), bestrow['HIGH_SCORE'], bestrow['BEST_PLAN']))
    #table.to_pickle("results.pkl") #saves the performance data, in case you want to refer to it later. pickled python objects can be loaded back at any later point.

class WeightedRandomGeneration(object):
    def __init__(self, wt):
        self.totalWt = []
        total = 0
        for w in wt:
            total += w
            self.totalWt.append(total)
    def next(self):
        rnd = random() * self.totalWt[-1]
        return bisect.bisect_right(self.totalWt, rnd)
    def __call__(self):
        return self.next()

run(100,20,0.02)
