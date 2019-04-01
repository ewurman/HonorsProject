#from GPPlayerTree import run  #should have all the functions and classes
from GPTestBot1 import data as GP #same but for when we move this
import os
import subprocess
import shlex
import random
import runpy
import sys
import shutil
#import battlecode-manager/runGPGame

NUM_CROSSOVER_HEADER = "# Number of Avg Crossover Per Generation\n"
CHEIGHTS_HEADER = "# Average height of tree A of Crossovers Across Generations\n"
MUTATIONS_HEADER = "# Number of Avg Mutations Per Generation\n"
TNODES_HEADER = "# Average Number of Nodes per Tree each Generation\n"
WINNER_DIST_HEADER = "# Winner Distribution\n"


POP_SIZE = 64 #must be even -> 32 easy for final tournament
GENERATIONS = 100 # want 50
RECORD_PER_GEN = 5

IDEAL_PLAYER = GP.createIdealPlayer()
gbest = None

def log(filepath, message):
    #print("Logging:", message)
    with open(filepath+"/Log.txt", 'a+') as f:
        f.write(message);


def runGame(player1, player2):
    ''' Fake running a game'''
    p1Score = player1.compareTo(IDEAL_PLAYER)
    p2Score = player2.compareTo(IDEAL_PLAYER)
    global gbest

    if gbest == None:
        gbest = (player1, p1Score)

    if p1Score > gbest[1]:
        gbest = (player1, p1Score)

    if p2Score > gbest[1]:
        gbest = (player1, p2Score)


    if p1Score > p2Score:
        return (player1, 0)
    elif p2Score > p1Score:
        return (player2, 1)
    else:
        return random.choice([(player1, 0), (player2, 1)])


def battleRoyale(population):
    #TODO: Assumes population is a power of 2
    print("################## Battle Royale Commenced ##################")
    while len(population) != 1:
        #start games
        new_pop = []
        for j in range(0,len(population),2):
            player1 = population[j]
            player2 = population[j+1]
            winner, x = runGame(player1, player2)
            new_pop.append(winner)
        population = new_pop.copy()

    finalWinner = population[0]
    return finalWinner




def writeDataToFile(filepath, crossoversPerRound, cHeightsPerRound, mutationsPerRound, tNodesPerRound, winnerDist, isIntermediate = True):
    log(filepath, "Writing Data to a file at " + filepath + '\n')
    fullPath = filepath+"/CrossoverMutationData.txt"
    with open(fullPath, 'a+') as f:
        f.seek(0)
        f.truncate()
        f.write(NUM_CROSSOVER_HEADER)
        last = crossoversPerRound.pop()
        total = last
        for x in crossoversPerRound:
            total += x
            f.write(str(x)+',')
        f.write(str(last)+ '\n# Average Number of Avg Crossovers Across Generations\n')
        f.write(str( total / GENERATIONS) + '\n\n')

        f.write(CHEIGHTS_HEADER)
        avgHeights = [0,0,0,0,0]
        for h in cHeightsPerRound:
            h0 = str(h[0])
            h1 = str(h[1])
            h2 = str(h[2])
            h3 = str(h[3])
            h4 = str(h[4])
            if isIntermediate:
                f.write(h0 + ',' + h1 + ',' + h2 + ',' + h3 + ',' + h4 + ';') #easier to read in as one line
            else: 
                f.write(h0 + ',' + h1 + ',' + h2 + ',' + h3 + ',' + h4 + '\n')
            avgHeights = [sum(x) for x in zip(avgHeights, h)] #add component wise

        avgHeights = [str(x / len(cHeightsPerRound)) for x in avgHeights]
        f.write("\n# Average height of tree A of Crossovers Across Generations\n")
        f.write(avgHeights[0] + ',' + avgHeights[1] + ',' + avgHeights[2] + ',' + avgHeights[3] + ',' + avgHeights[4] + '\n\n')

        f.write(MUTATIONS_HEADER)
        lastM = mutationsPerRound.pop()
        totalM = lastM
        for x in mutationsPerRound:
            totalM += x
            f.write(str(x)+',')
        f.write(str(lastM)+ '\n# Average Number of Avg Mutations Across Generations\n')
        f.write(str( totalM / GENERATIONS) + '\n')

        #node numbers
        f.write("\n"+ TNODES_HEADER)
        avgNodes = [0,0,0,0,0]
        for nodeDist in tNodesPerRound:
            n0 = str(nodeDist[0])
            n1 = str(nodeDist[1])
            n2 = str(nodeDist[2])
            n3 = str(nodeDist[3])
            n4 = str(nodeDist[4])
            if isIntermediate:
                f.write(n0 + ',' + n1 + ',' + n2 + ',' + n3 + ',' + n4 + ';')
            else:
                f.write(n0 + ',' + n1 + ',' + n2 + ',' + n3 + ',' + n4 + '\n')
            avgNodes = [sum(x) for x in zip(avgNodes, nodeDist)]
        f.write("\n# Mean number of nodes \n")
        avgNodes = [str(x/GENERATIONS) for x in avgNodes]
        f.write(avgNodes[0] + ',' + avgNodes[1] + ',' + avgNodes[2] + ',' + avgNodes[3] + ',' + avgNodes[4] + '\n\n')

        f.write(WINNER_DIST_HEADER)
        f.write(str(winnerDist[0]) + ", " + str(winnerDist[1]) + "\n")

    log(filepath, "Wrote Data to File!\n")



def readDataFromFile(filepath):
    '''
        This should only be called on Intermediate written Data files
    '''
    with open(filepath+"/CrossoverMutationData.txt", 'a+') as f:
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

    print("Done Reading Data from file")
    return crossoversPerRound, cHeightsPerRound, mutationsPerRound, tNodesPerRound, winnerDist



def doTesting(mutateNodeProb, mutateOccurProb, crossoverProb, crossoverStopEarly, elitismNum):
    resultDirName = "GPOperatorTestResults/Pop"+str(POP_SIZE)+"_Gen"+str(GENERATIONS)+"_XOverP"+str(crossoverProb)+"_XOverS"+str(crossoverStopEarly)+"_MOP"+str(mutateOccurProb)+"_MNP"+str(mutateNodeProb)+"Fixed"
    print(os.listdir("GPOperatorTestResults"))
    if not os.path.exists(resultDirName):
        print("Creating new folder for test ", resultDirName)
        os.makedirs(resultDirName, exist_ok=True)
    else:
        print("This directory already exists!")
        x = input("Do you want to delete the last tests and start over? (y/n) ")
        if x == 'y':
            shutil.rmtree(resultDirName)
            os.makedirs(resultDirName, exist_ok=True)


    directories = os.listdir(resultDirName)
    print("Directories found: ", directories)
    savedDirs = [x for x in directories if x.startswith("Gen")]
    print("Ordered: ", sorted(savedDirs))

    if len(savedDirs) == 0:
        print("No saved directories found, starting a new test")

        return newTest(mutateNodeProb, mutateOccurProb, crossoverProb, crossoverStopEarly, resultDirName, elitismNum)
        


    lastSaved = sorted(savedDirs).pop()
    genNum = int(lastSaved[3:])
    lastSavedDir = resultDirName + '/' + lastSaved
    print("lastSavedDir is: ", lastSavedDir)
    print("At generation number", genNum) #should always be a multiple of RECORD_PER_GEN

    #Load last population
    population = []

    lastSavedSubDirs = os.listdir(lastSavedDir)
    print("lastSavedSubDirs:", lastSavedSubDirs)
    individualDirs = [x for x in lastSavedSubDirs if x.startswith("Individual")]
    print("individualDirs:", individualDirs)
    for individualDir in individualDirs:
        path = lastSavedDir + '/' + individualDir
        print("individualDir path:", path)
        player = GP.DecisionTreePlayer(None, None, None, None, None, None)
        player = player.readFromFiles(path, GP.allFunctionSets)
        population.append(player)

    #Load last Data from file
    crossoversPerRound, cHeightsPerRound, mutationsPerRound, tNodesPerRound, winnerDist = readDataFromFile(lastSavedDir)

    # Now start playing again
    log(resultDirName, "############ Resuming test for Pop"+str(POP_SIZE)+"_Gen"+str(GENERATIONS)+"_XOverP"+str(crossoverProb)+"_XOverS"+str(crossoverStopEarly)+"_MOP"+str(mutateOccurProb)+"_MNP"+str(mutateNodeProb)+" ############\n")
    log(resultDirName, "Resuming test at generation: {0}\n".format(genNum))
    for i in range(genNum, GENERATIONS):
        log(resultDirName, "\n\nGeneration {0}\n\n".format(i))
        random.shuffle(population)
        breedingPool = []

        # RECORD WINNERS AND POPULATION AT THIS GENERATION 
        if (i + 1) % RECORD_PER_GEN == 0:
            genDir = resultDirName +'/Gen'+ str(i+1).zfill(2)

            #Now record the population
            for j in range(POP_SIZE):
                individualDir = genDir + "/Individual" + str(j) + "/"
                if not os.path.exists(os.path.dirname(individualDir)):
                    os.makedirs(os.path.dirname(individualDir), exist_ok=True)

                individual = population[j]
                individual.writeToFiles(individualDir)

            # Now write data to file
            writeDataToFile(genDir, crossoversPerRound, cHeightsPerRound, mutationsPerRound, tNodesPerRound, winnerDist, isIntermediate=True)
            log(resultDirName, "Finished recording individuals and data\n")

            log(resultDirName, "################## Begin Battle Royale ##################\n")
            genWinner = battleRoyale(population)
            log(resultDirName, "################## End Battle Royale ##################\n")
            
            if not os.path.exists(os.path.dirname(genDir)):
                os.makedirs(os.path.dirname(genDir), exist_ok=True)
            genWinner.writeToFiles(genDir+"/Winner/")



        # DATA COLLECTION Declaration
        crossoversThisRound = 0
        cHeightsThisRound = [0,0,0,0,0]
        tNodesThisRound = [0,0,0,0,0]
        numcHeights = [0,0,0,0,0]
        mutationsThisRound = 0

        #start games
        for j in range(0,POP_SIZE,2):
            player1 = population[j]
            player2 = population[j+1]

            # SAVE the number of nodes from this generation
            p1nodes = player1.getNumNodesByTree()
            p2nodes = player2.getNumNodesByTree()
            #nodes = [sum(x) for x in zip(p1nodes, p2nodes)]
            tNodesThisRound = [sum(x) for x in zip(p1nodes, p2nodes, tNodesThisRound)]

            log(resultDirName, "About to run game for Gen {0} match {1}\n".format(i, j))
            #run battlecode with these two players
            # Tournament Select
            winner, playerNum = runGame(player1, player2)
            breedingPool.append(winner) 

            winnerDist[playerNum] += 1
        #now breeding pool should be half POP_SIZE

        #Now we do our elitism
        elitistPlayers = getElitistPlayers(population, elitismNum)
        #get ready for the new generation
        population.clear() 
        population += elitistPlayers

        print("Starting Crossover")
        for j in range((POP_SIZE - elitistPlayers)//2):
            mates = random.sample(breedingPool, 2)
            m1 = mates[0]
            m2 = mates[1]
            
            c1, c2, numCrossover, heightAs = GP.Crossover3PlayerFixed(m1, m2, crossoverProb, crossoverStopEarly)
            population += [c1, c2]
            crossoversThisRound += numCrossover

            for k in range(0, len(heightAs)):
                if heightAs[k] != -1:
                    numcHeights[k] += 1
                    cHeightsThisRound[k] += heightAs[k]


            #cHeightsThisRound = [sum(x) for x in zip(heightAs, cHeightsThisRound)] #add component wise

        log(resultDirName, "Gen {0}: Finished Crossover\n".format(i))
        log(resultDirName, "Gen {0}: Starting Mutations\n".format(i))
        for j in range(POP_SIZE):
            player = population[j]
            mutatedPlayer, numMutations = GP.MutatePlayerFixed(player, mutateNodeProb, mutateOccurProb, GP.allFunctionSets, GP.game_number_info_functions_number_mappings)
            population[j] = mutatedPlayer
            mutationsThisRound += numMutations
        log(resultDirName, "Gen {0}: Finished Mutations\n".format(i))


        # DATA COLLECTION 
        for j in range(0, len(cHeightsThisRound)):
            if numcHeights[j] == 0:
                cHeightsThisRound[j] = -1
            else:
                cHeightsThisRound[j] = cHeightsThisRound[j] / numcHeights[j] #divide by num crossovers for avg
        
        cHeightsPerRound.append(cHeightsThisRound)
        crossoversPerRound.append(crossoversThisRound)
        mutationsPerRound.append(mutationsThisRound)
        tNodesPerRound.append(tNodesThisRound)

    #end Generations

    #now we want a final tournament
    #TODO: This assumes a power of 2 population
    finalWinner = battleRoyale(population)
    finalWinnerDir = resultDirName + '/Winner/'

    if not os.path.exists(os.path.dirname(finalWinnerDir)):
        os.makedirs(os.path.dirname(finalWinnerDir), exist_ok=True)
        
    finalWinner.writeToFiles(finalWinnerDir)

    writeDataToFile(resultDirName, crossoversPerRound, cHeightsPerRound, mutationsPerRound, tNodesPerRound, winnerDist)
    print("Completed All generations and Data recording!")
    log(resultDirName, "Completed All generations and Data recording!\n")

    return finalWinner







def newTest(mutateNodeProb, mutateOccurProb, crossoverProb, crossoverStopEarly, resultDirName, elitismNum):
    #DATA COLLECTION VARIABLES
    crossoversPerRound = []
    cHeightsPerRound = []  #list of list of heights at which crossover occurs
    tNodesPerRound = []  #list of list of avg number of nodes of trees per generation
    mutationsPerRound = []
    winnerDist = [0,0]
    population = []
    topTreeHeight = 4

    log(resultDirName, "############ Starting new test ############\n")
    # initialize population
    for i in range(POP_SIZE):
        player = GP.createRandomFixedSizeDecisionTreePlayer(topTreeHeight)
        population.append(player)

    for i in range(GENERATIONS):
        log(resultDirName, "\n\nGeneration {0}\n\n".format(i))
        random.shuffle(population)
        breedingPool = []

        # RECORD WINNERS AND POPULATION AT THIS GENERATION 
        if (i + 1) % RECORD_PER_GEN == 0:
            genDir = resultDirName +'/Gen'+ str(i+1).zfill(2)

            #Now record the population
            for j in range(POP_SIZE):
                individualDir = genDir + "/Individual" + str(j) + "/"
                if not os.path.exists(os.path.dirname(individualDir)):
                    os.makedirs(os.path.dirname(individualDir), exist_ok=True)

                individual = population[j]
                individual.writeToFiles(individualDir)

            # Now write data to file
            writeDataToFile(genDir, crossoversPerRound, cHeightsPerRound, mutationsPerRound, tNodesPerRound, winnerDist, isIntermediate=True)
            log(resultDirName, "Finished recording individuals and data\n")

            log(resultDirName, "################## Begin Battle Royale ##################\n")
            genWinner = battleRoyale(population)
            log(resultDirName, "################## End Battle Royale ##################\n")
            
            if not os.path.exists(os.path.dirname(genDir)):
                os.makedirs(os.path.dirname(genDir), exist_ok=True)
            genWinner.writeToFiles(genDir+"/Winner/")


        # DATA COLLECTION Declaration
        crossoversThisRound = 0
        cHeightsThisRound = [0,0,0,0,0]
        tNodesThisRound = [0,0,0,0,0]
        numcHeights = [0,0,0,0,0]
        mutationsThisRound = 0

        #start games
        for j in range(0,POP_SIZE,2):
            player1 = population[j]
            player2 = population[j+1]

            # SAVE the number of nodes from this generation
            p1nodes = player1.getNumNodesByTree()
            p2nodes = player2.getNumNodesByTree()
            #nodes = [sum(x) for x in zip(p1nodes, p2nodes)]
            tNodesThisRound = [sum(x) for x in zip(p1nodes, p2nodes, tNodesThisRound)]

            log(resultDirName, "About to run game for Gen {0} match {1}\n".format(i, j))
            #run battlecode with these two players
            # Tournament Select
            winner, playerNum = runGame(player1, player2)
            breedingPool.append(winner) 

            winnerDist[playerNum] += 1
        #now breeding pool should be half POP_SIZE

        #Now we do our elitism
        elitistPlayers = getElitistPlayers(population, elitismNum)
        #get ready for the new generation
        population.clear() 
       #population += elitistPlayers
        print("population has {0} players".format(len(population)))

        print("Starting Crossover")
        for j in range((POP_SIZE - elitismNum)//2):
            mates = random.sample(breedingPool, 2)
            m1 = mates[0]
            m2 = mates[1]
            
            c1, c2, numCrossover, heightAs = GP.Crossover3PlayerFixed(m1, m2, crossoverProb, crossoverStopEarly)
            population += [c1, c2]
            crossoversThisRound += numCrossover

            for k in range(0, len(heightAs)):
                if heightAs[k] != -1:
                    numcHeights[k] += 1
                    cHeightsThisRound[k] += heightAs[k]


            #cHeightsThisRound = [sum(x) for x in zip(heightAs, cHeightsThisRound)] #add component wise

        log(resultDirName, "Gen {0}: Finished Crossover\n".format(i))
        log(resultDirName, "Gen {0}: Starting Mutations\n".format(i))
        for j in range(len(population)):
            player = population[j]
            mutatedPlayer, numMutations = GP.MutatePlayerFixed(player, mutateNodeProb, mutateOccurProb, GP.allFunctionSets, GP.game_number_info_functions_number_mappings)
            population[j] = mutatedPlayer
            mutationsThisRound += numMutations
        log(resultDirName, "Gen {0}: Finished Mutations\n".format(i))

        population += elitistPlayers

        # DATA COLLECTION 
        for j in range(0, len(cHeightsThisRound)):
            if numcHeights[j] == 0:
                cHeightsThisRound[j] = -1
            else:
                cHeightsThisRound[j] = cHeightsThisRound[j] / numcHeights[j] #divide by num crossovers for avg

        tNodesThisRound = [x / POP_SIZE for x in tNodesThisRound] #divide to get average

        
        cHeightsPerRound.append(cHeightsThisRound)
        crossoversPerRound.append(crossoversThisRound)
        mutationsPerRound.append(mutationsThisRound)
        tNodesPerRound.append(tNodesThisRound)

    #end Generations

    #now we want a final tournament
    #TODO: This assumes a power of 2 population
    finalWinner = battleRoyale(population)
    finalWinnerDir = resultDirName + '/Winner/'

    if not os.path.exists(os.path.dirname(finalWinnerDir)):
        os.makedirs(os.path.dirname(finalWinnerDir), exist_ok=True)
        
    finalWinner.writeToFiles(finalWinnerDir)

    writeDataToFile(resultDirName, crossoversPerRound, cHeightsPerRound, mutationsPerRound, tNodesPerRound, winnerDist)
    print("Completed All generations and Data recording!")
    log(resultDirName, "Completed All generations and Data recording!\n")

    return finalWinner




def getElitistPlayers(population, elitismNum):
    popScores = [(x,x.compareTo(IDEAL_PLAYER)) for x in population]
    top4 = popScores[:4]

    def myKey(playerScoreA):
        return playerScoreA[1]

    top4 = sorted(top4, key=myKey) #Ascending order
    for playerScore in popScores[4:]:
        if playerScore[1] > top4[0][1]:
            top4[0] = playerScore
            top4 = sorted(top4, key=myKey) #Ascending order

    bestPlayers = [x[0] for x in top4]

    print("Elitist Players have scores of {0}, {1}, {2}, {3}".format(top4[0][1],top4[1][1],top4[2][1],top4[3][1]))
    return bestPlayers







if __name__ == '__main__':

    gpOperatorTestsDir = "GPOperatorTestResults"
    if not os.path.exists(gpOperatorTestsDir):
        os.makedirs(gpOperatorTestsDir, exist_ok=True)

    population = []
    mutateNodeProb = 0.01
    mutateOccurProb = 0.2  #{0.2,0.4,0.6}

    crossoverProb = 0.6 #% chance each tree  want it to be one of {0.4, 0.6, 0.8}

    crossoverStopEarly = 0.1 #chance to stop higher in tree
    elitismNum = 4
    winner = doTesting(mutateNodeProb, mutateOccurProb, crossoverProb, crossoverStopEarly, elitismNum)
    
    print("Completed All generations and recording!")

    finalScore = winner.compareTo(IDEAL_PLAYER)
    bestScore = IDEAL_PLAYER.compareTo(IDEAL_PLAYER)

    print("Final Score: {0}, Ideal Score: {1}, Accuracy: {2}".format(finalScore, bestScore, finalScore/bestScore))
    print("Generation Best:")
    print("gBest Score: {0}, Ideal Score: {1}, Accuracy: {2}".format(gbest[1], bestScore, gbest[1]/bestScore))











