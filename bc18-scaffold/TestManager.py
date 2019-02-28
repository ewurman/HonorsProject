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


def battleRoyale(population):
    #TODO: Assumes population is a power of 2
    while len(population) != 1:
        #start games
        new_pop = []
        for j in range(0,len(population),2):
            player1 = population[j]
            player2 = population[j+1]
            winner = runGame(player1, player2)
            new_pop.append(winner)
        population = new_pop.copy()

    finalWinner = population[0]
    return finalWinner



if __name__ == '__main__':
    POP_SIZE = 32 #must be even -> 32 easy for final tournament
    GENERATIONS = 50 # want 50
    RECORD_PER_GEN = 5

    population = []
    mutateNodeProb = 0.01
    mutateOccurProb = 0.2  #{0.2,0.4,0.6}
    crossoverProb = 0.5 #50% chance each tree  want it to be one of {0.4, 0.6, 0.8}
    crossoverStopEarly = 0.1 #chance to stop higher in tree
    resultDirName = "TestResults/Pop"+str(POP_SIZE)+"_Gen"+str(GENERATIONS)+"_XOverP"+str(crossoverProb)+"_XOverS"+str(crossoverStopEarly)+"_MOP"+str(mutateOccurProb)+"_MNP"+str(mutateNodeProb)

    #DATA COLLECTION VARIABLES
    crossoversPerRound = []
    cHeightsPerRound = []
    mutationsPerRound = []

    # initialize population
    for i in range(POP_SIZE):
        player = GP.createRandomDecisionTreePlayer()
        population.append(player)


    for i in range(GENERATIONS):
        print("\n\n\nGeneration {0}\n\n\n".format(i))
        random.shuffle(population)
        breedingPool = []


        if i % RECORD_PER_GEN == 0:
            genWinner = battleRoyale(population)
            genDir = resultDirName +'/Gen'+ str(i) + '/'
            
            if not os.path.exists(os.path.dirname(genDir)):
                os.makedirs(os.path.dirname(genDir), exist_ok=True)

            genWinner.writeToFiles(genDir)


        # DATA COLLECTION Declaration
        crossoversThisRound = 0
        cHeightsThisRound = [0,0,0,0,0]
        mutationsThisRound = 0

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
            
            c1, c2, numCrossover, heightAs = GP.Crossover1Player(m1, m2, crossoverProb, crossoverStopEarly)
            population += [c1, c2]
            crossoversThisRound += numCrossover
            cHeightsThisRound = [sum(x) for x in zip(heightAs, cHeightsThisRound)] #add component wise

        print("Finished Crossover")
        print("Starting Mutations")
        for j in range(POP_SIZE):
            player = population[j]
            mutatedPlayer, numMutations = GP.MutatePlayer(player, mutateNodeProb, mutateOccurProb, GP.allFunctionSets)
            population[j] = mutatedPlayer
            mutationsThisRound += numMutations
        print("Finished Mutations")


        # DATA COLLECTION 
        cHeightsThisRound = [x / (POP_SIZE//2) for x in cHeightsThisRound] #divide by num crossovers for avg
        cHeightsPerRound.append(cHeightsThisRound)
        crossoversPerRound.append(crossoversThisRound)
        mutationsPerRound.append(mutationsThisRound)

    #end Generations


    #now we want a final tournament
    #TODO: This assumes a power of 2 population
    finalWinner = battleRoyale(population)
    finalWinnerDir = resultDirName + '/Winner/'

    if not os.path.exists(os.path.dirname(finalWinnerDir)):
        os.makedirs(os.path.dirname(finalWinnerDir), exist_ok=True)
        
    finalWinner.writeToFiles(finalWinnerDir)


    with open(resultDirName+"/CrossoverMutationData.txt", 'a+') as f:
        f.write("# Number of Avg Crossover Per Generation\n")
        last = crossoversPerRound.pop()
        total = last
        for x in crossoversPerRound:
            total += x
            f.write(str(x)+',')
        f.write(str(last)+ '\n# Average Number of Avg Crossovers Across Generations\n')
        f.write(str( total / GENERATIONS) + '\n\n')

        f.write("# Average height of tree A of Crossovers Per Generation\n")
        avgHeights = [0,0,0,0,0]
        for h in cHeightsPerRound:
            h0 = str(h[0])
            h1 = str(h[1])
            h2 = str(h[2])
            h3 = str(h[3])
            h4 = str(h[4])
            f.write(h0 + ',' + h1 + ',' + h2 + ',' + h3 + ',' + h4 + '\n')
            avgHeights = [sum(x) for x in zip(avgHeights, h)] #add component wise

        avgHeights = [str(x / len(cHeightsPerRound)) for x in avgHeights]
        f.write("# Average height of tree A of Crossovers Across Generations\n")
        f.write(avgHeights[0] + ',' + avgHeights[1] + ',' + avgHeights[2] + ',' + avgHeights[3] + ',' + avgHeights[4] + '\n\n')

        f.write("# Number of Avg Mutations Per Generation\n")
        lastM = mutationsPerRound.pop()
        totalM = lastM
        for x in mutationsPerRound:
            totalM += x
            f.write(str(x)+',')
        f.write(str(lastM)+ '\n# Average Number of Avg Mutations Across Generations\n')
        f.write(str( totalM / GENERATIONS) + '\n')











