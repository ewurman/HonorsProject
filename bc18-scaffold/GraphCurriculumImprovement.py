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


TEST_GRAPHING = False;
PLAYING_IDEAL_PLAYER = True;
NUM_TESTS = 20;
GENS_PER_TESTS = 2;


ELITISM = False;

POP_SIZE = 32
GENERATIONS = 50


def runGame(player1, player2):
    '''TODO: call battlecode and run a game'''
    pwd = os.getcwd()
    pwd1 = pwd + "/GPTestBot1/Player/"
    pwd2 = pwd + "/GPTestBot2/Player/"
    print("PWD: " + pwd)
    player1.writeToFiles(pwd1)
    player2.writeToFiles(pwd2)

    # now call the runGPGame script
    subprocess.run(["sh", "runGenerations.sh"], timeout=30000000) #10 s + 50 each round, goes to avg 30 sec per roundx1000rounds
    # max is 30000000

    # now read the winner in
    with open("battlecode-manager/winner.txt") as f:
        line = f.read()
    if line[0] == '0':
        return player1, 0
    elif line[0] == '1':
        return player2, 1
    else:
        print("ERROR: No winner found")
        return player1, 0



def doImprovementTesting(resultDirName)->dict:
    improvementResultsByGen = dict()
    print(resultDirName)
    for i in range(1, GENERATIONS+1, GENS_PER_TESTS):
        playerDir = resultDirName

        playerDir += "/Gen" + str(i).zfill(2) + "/Winner" #TODO Gen01 is starting one... need to accomodate that


        print(playerDir)
        player = GP.DecisionTreePlayer(None, None, None, None, None, None)
        player = player.readFromFiles(playerDir, GP.allFunctionSets)
        
        opponent = GP.DecisionTreePlayer(None, None, None, None, None, None)
        if PLAYING_IDEAL_PLAYER:
            opponent = GP.createIdealPlayer()
        else:
            topTreeHeight = 5
            attackTreeHeight = 3
            opponent = GP.createRandomFixedSizeDecisionTreePlayer(topTreeHeight, attackTreeHeight)

        playerResults = []
        for j in range(NUM_TESTS):
            if TEST_GRAPHING:
                winner = random.getrandbits(1) #testing this graphing
            else:
                winningPlayer, winner = runGame(opponent, player) #1s are wins
            playerResults.append(winner)

        improvementResultsByGen[i] = playerResults
        
    return improvementResultsByGen


def convertDictToWinningPercentage(mapping):
    ''' takes in gen# -> [1,0...] map (dictionary)'''
    newDict = dict()
    for gen,wl in mapping.items():
        wins = sum(wl)
        wp = (wins * 2.0)/(len(wl)*2.0) #make sure its a double
        newDict[gen] = wp
    return newDict


#def standardDeviation()


def graphImprovement(resultDirName, treeString):
    improvementResultsByGen = doImprovementTesting(resultDirName)
    improvementWinPercentByGen = convertDictToWinningPercentage(improvementResultsByGen)

    #df = pd.DataFrame(improvementWinPercentByGen)
    print("x:", len(range(1,GENERATIONS+1, GENS_PER_TESTS)))
    print("winPercent:", len(improvementWinPercentByGen.values()))
    print("record:", len(improvementResultsByGen.values()))

    gens = range(1,GENERATIONS+1,GENS_PER_TESTS)
    df = pd.DataFrame({'x': gens, 'winPercent':[improvementWinPercentByGen[x] for x in gens], 'record':[improvementResultsByGen[x] for x in gens]})

    f = plt.figure()
    plt.plot('x', 'winPercent', data=df, color='skyblue', linewidth=2, marker='o', markersize=3)


    #print(df.groupby('x')['record'])
    #mean = df.groupby('x')['record'].mean()
    #std = df.groupby('x')['record'].std()

    #plt.errorbar(mean.index, mean, xerr=0, yerr=2*std, linestyle='')
    opponentTitle = "Random"
    if (PLAYING_IDEAL_PLAYER):
        opponentTitle = "Hand-Crafted"

    plt.legend()
    plt.xlabel("Generation")
    plt.ylabel("Win Percentage over 20 games")
    plt.title("Win Percentage of GP Player while evolving {1} vs. {0} Player".format(opponentTitle, treeString))
    plt.show()

    #plt.show()


    opponent = "Random"
    if (PLAYING_IDEAL_PLAYER):
        opponent = "Ideal"
    f.savefig(resultDirName+"/winningPercent_vs_{0}.pdf".format(opponent), bbox_inches='tight')



if __name__ == '__main__':
    mutateNodeProb = 0.01
    mutateOccurProb = 0.2  #{0.2,0.4,0.6}

    crossoverProb = 0.6 #% chance each tree  want it to be one of {0.4, 0.6, 0.8}
    crossoverStopEarly = 0.1 #chance to stop higher in tree

    treeString = "MoveTree"
    resultDirName = "CurriculumTestingResults/"+treeString+"/Pop"+str(POP_SIZE)+"_Gen"+str(GENERATIONS)+"_XOverP"
    resultDirName += str(crossoverProb)+"_XOverS"+str(crossoverStopEarly)+"_MOP"+str(mutateOccurProb)+"_MNP"+str(mutateNodeProb)
    resultDirName += "Fixed"
    if ELITISM:
        resultDirName += "/Elitist"

    graphImprovement(resultDirName, treeString)







