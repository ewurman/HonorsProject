#from GPPlayerTree import run  #should have all the functions and classes
from GPTestBot1 import data as GP #same but for when we move this
import os
import subprocess
import shlex
import random
import runpy
#import battlecode-manager/runGPGame


def runGame(player1, player2):
    '''TODO: call battlecode and run a game'''
    pwd = os.getcwd()
    pwd1 = pwd + "/GPTestBot1/Player/"
    pwd2 = pwd + "/GPTestBot2/Player/"
    print("PWD: " + pwd)
    player1.writeToFiles(pwd1)
    player2.writeToFiles(pwd2)

    # now call the runGPGame script
    os.system("sh runGenerations.sh")


    # now read the winner in
    with open("battlecode-manager/winner.txt") as f:
        line = f.read()
    if line[0] == '0':
        return player1
    elif line[1] == '1':
        return player2
    else:
        print("ERROR: No winner found")
        return player1





if __name__ == '__main__':
    POP_SIZE = 4 #must be even
    GENERATIONS = 2

    population = []
    mutateProb = 0.05
    crossoverProb = 0.5 #50% chance each tree
    crossoverStopEarly = 0.05 #chance to stop higher in tree


    # initialize population
    for i in range(POP_SIZE):
        player = GP.createRandomDecisionTreePlayer()
        population.append(player)


    for i in range(GENERATIONS):
        print("\n\n\nGeneration {0}\n\n\n".format(i))
        random.shuffle(population)
        breedingPool = []

        #start games
        for j in range(0,POP_SIZE,2):
            player1 = population[j]
            player2 = population[j+1]

            
            print("About to run game")
            #run battlecode with these two players
            # Tournament Select
            winner = runGame(player1, player2)
            breedingPool.append(winner) 

        #now breeding pool should be half POP_SIZE

        #get ready for the new generation
        population.clear() 
        print("Starting Crossover")
        for j in range(POP_SIZE//2):
            mates = random.sample(breedingPool, 2)
            m1 = mates[0]
            m2 = mates[1]
            
            c1, c2 = GP.Crossover1Player(m1, m2, crossoverProb, crossoverStopEarly)
            population += [c1, c2]
        print("Finished Crossover")
        print("Starting Mutations")
        for j in range(POP_SIZE):
            player = population[j]
            mutatedPlayer = GP.MutatePlayer(player, mutateProb, GP.allFunctionSets)
            population[j] = mutatedPlayer
        print("Finished Mutations")

         







