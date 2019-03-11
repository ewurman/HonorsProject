from GPTestBot1 import data as GP #same but for when we move this
import os
import subprocess
import shlex
import random
import runpy
import sys
#import battlecode-manager/runGPGame
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

NUM_CROSSOVER_HEADER = "# Number of Avg Crossover Per Generation\n"
CHEIGHTS_HEADER = "# Average height of tree A of Crossovers Across Generations\n"
MUTATIONS_HEADER = "# Number of Avg Mutations Per Generation\n"
TNODES_HEADER = "# Average Number of Nodes per Tree each Generation\n"
WINNER_DIST_HEADER = "# Winner Distribution\n"

POP_SIZE = 32 #must be even -> 32 easy for final tournament
GENERATIONS = 50 # want 50


def readDataFromFile(filepath):
    '''
        This should only be called on Intermediate written Data files
    '''
    with open(filepath+"/CrossoverMutationData.txt", 'r+') as f:
        lines = f.readlines()

        crossoversPerRound = []
        cHeightsPerRound = []
        mutationsPerRound = []
        tNodesPerRound = []
        winnerDist = [0,0]

        for i in range(1, len(lines)):
            if lines[i-1] == NUM_CROSSOVER_HEADER:
                print("Found NUM_CROSSOVER_HEADER, parsing for crossoversPerRound")
                line = lines[i].strip()
                crossoversPerRound = line.split(',')
                print("crossoversPerRound: ", crossoversPerRound)

            elif lines[i-1] == CHEIGHTS_HEADER:
                print("Found CHEIGHTS_HEADER, parsing for cHeightsPerRound")
                line = lines[i].strip()
                allCHeights = line.split(";") #ASSUMING INTERMEDIATE FILE
                cHeightsPerRound = [x.split(',') for x in allCHeights]
                print("cHeightsPerRound: ", cHeightsPerRound)

            elif lines[i-1] == MUTATIONS_HEADER:
                print("Found MUTATIONS_HEADER, parsing for mutationsPerRound")
                line = lines[i].strip()
                mutationsPerRound = line.split(',')
                print("mutationsPerRound: ", mutationsPerRound)

            elif lines[i-1] == TNODES_HEADER:
                print("Found TNODES_HEADER, parsing for tNodesPerRound")
                line = lines[i].strip()
                allTNodes = line.split(";") #ASSUMING INTERMEDIATE FILE
                tNodesPerRound = [x.split(',') for x in allTNodes[:-1]]
                print("tNodesPerRound: ", tNodesPerRound)

            elif lines[i-1] == WINNER_DIST_HEADER:
                print("Found WINNER_DIST_HEADER, parsing for winnerDist")
                line = lines[i].strip()
                winnerDist = line.split(',')
                print("winnerDist: ", winnerDist)

    print("************* Done Reading Data from file *************")
    return crossoversPerRound, cHeightsPerRound, mutationsPerRound, tNodesPerRound, winnerDist


def graphResult(resultDirName):
    fig = plt.figure()
    fig.suptitle(resultDirName)


def graphNodesOverGenerations(resultDirName, tNodesPerRound):
    topTreeNodesPerRound = [float(x[0]) for x in tNodesPerRound]
    harvestTreeNodesPerRound = [float(x[1]) for x in tNodesPerRound]
    attackTreeNodesPerRound = [float(x[2]) for x in tNodesPerRound]
    moveTreeNodesPerRound = [float(x[3]) for x in tNodesPerRound]
    buildTreeNodesPerRound = [float(x[4]) for x in tNodesPerRound]

    print(tNodesPerRound)
    print("tNodesPerRound len is", len(topTreeNodesPerRound))
    print("topTreeNodesPerRound len is", len(topTreeNodesPerRound))
    print("harvestTreeNodesPerRound len is", len(harvestTreeNodesPerRound))
    print("attackTreeNodesPerRound len is", len(attackTreeNodesPerRound))
    print("moveTreeNodesPerRound len is", len(moveTreeNodesPerRound))
    print("buildTreeNodesPerRound len is", len(buildTreeNodesPerRound))

    df = pd.DataFrame({'x': range(1,GENERATIONS+1), 'topTree': np.array(topTreeNodesPerRound), 'harvestTree': np.array(harvestTreeNodesPerRound), 'attackTree': np.array(attackTreeNodesPerRound), 'moveTree': np.array(moveTreeNodesPerRound), 'buildTree': np.array(buildTreeNodesPerRound)})

    f = plt.figure()
    plt.plot('x', 'topTree', data=df, color='skyblue', linewidth=2, marker='o', markersize=3)
    plt.plot('x', 'harvestTree', data=df, color='olive', linewidth=2, marker='o', markersize=3)
    plt.plot('x', 'attackTree', data=df, color='red', linewidth=2, marker='o', markersize=3)
    plt.plot('x', 'moveTree', data=df, color='violet', linewidth=2, marker='o', markersize=3)
    plt.plot('x', 'buildTree', data=df, color='yellow', linewidth=2, marker='o', markersize=3)
    plt.legend()
    plt.xlabel("Generation")
    plt.ylabel("Avg Number of Nodes")
    plt.title("Avg Nodes per Tree over Generations for " + resultDirName[24:])
    plt.show()

    f.savefig(resultDirName+"/NodesPerGeneration.pdf", bbox_inches='tight')



if __name__ == '__main__':


    population = []
    mutateNodeProb = 0.01
    mutateOccurProb = 0.2  #{0.2,0.4,0.6}

    crossoverProb = 0.8 #50% chance each tree  want it to be one of {0.4, 0.6, 0.8}

    crossoverStopEarly = 0.1 #chance to stop higher in tree
    resultDirName = "TestResults/Pop"+str(POP_SIZE)+"_Gen"+str(GENERATIONS)+"_XOverP"+str(crossoverProb)+"_XOverS"+str(crossoverStopEarly)+"_MOP"+str(mutateOccurProb)+"_MNP"+str(mutateNodeProb)

    crossoversPerRound, cHeightsPerRound, mutationsPerRound, tNodesPerRound, winnerDist = readDataFromFile(resultDirName)
    '''
    crossoversPerRound, mutationsPerRound, winnerDist, are lists
    cHeightsPerRound, tNodesPerRound are lists of lists (inner lenght 5 for number of trees)

    ''' 
    graphNodesOverGenerations(resultDirName, tNodesPerRound)


    
    print("Completed Graphing for: "+ resultDirName)

