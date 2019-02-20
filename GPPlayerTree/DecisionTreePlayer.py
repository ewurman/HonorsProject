import DecisionTree
import DecisionTreeUtils
import GPOperators

class DecisionTreePlayer:

    def __init__(self, topTree, harvestTree, attackTree, movementTree, buildTree, researchTree):
        self.topTree = topTree
        self.harvestTree = harvestTree
        self.attackTree = attackTree
        self.movementTree = movementTree
        self.buildTree = buildTree
        self.researchTree = researchTree

    def execute(self, battleCode, gameController):
        # Runs one turn through the Tree(s)
        actionNum = self.topTree.execute(battleCode, gameController)
        print("Top Tree gave us an action of", actionNum)
        if actionNum == 1:
            # harvest
            res = self.harvestTree.execute(battleCode, gameController)
            if res:
                print("harvestTree did not execute an action and instead returned", res)
        elif actionNum == 2:
            # attack
            res = self.attackTree.execute(battleCode, gameController)
            if res:
                print("attackTree did not execute an action and instead returned", res)
        elif actionNum == 3:
            # move
            res = self.movementTree.execute(battleCode, gameController)
            if res:
                print("movementTree did not execute an action and instead returned", res)
        elif actionNum == 4:
            # build
            res = self.buildTree.execute(battleCode, gameController)
            if res:
                print("buildTree did not execute an action and instead returned", res)
        elif actionNum == 5:
            # research
            res = self.researchTree.execute(battleCode, gameController)
            if res:
                print("researchTree did not execute an action and instead returned", res)
       
        return 


    def writeToFiles(self, directoryPath):
        '''we already can print so its similar following along and writing the nodes out'''
        topTreeString = self.topTree.getWriteString()
        print(topTreeString)
        harvestTreeString = self.harvestTree.getWriteString()
        attackTreeString = self.attackTree.getWriteString()
        moveTreeString = self.movementTree.getWriteString()
        buildTreeString = self.buildTree.getWriteString()

        with open(directoryPath + "TopTree.txt", 'w') as f:
            f.write(topTreeString)
        with open(directoryPath + "HarvestTree.txt", 'w') as f:
            f.write(harvestTreeString)
        with open(directoryPath + "AttackTree.txt", 'w') as f:
            f.write(attackTreeString)
        with open(directoryPath + "MoveTree.txt", 'w') as f:
            f.write(moveTreeString)
        with open(directoryPath + "BuildTree.txt", 'w') as f:
            f.write(buildTreeString)


    def readFromFiles(self, directoryPath, allFunctionSets):
        fileNames = ["TopTree.txt", "HarvestTree.txt", "AttackTree.txt", "MoveTree.txt", "BuildTree.txt"]


        def recursiveBuildTree(lines, lineNum, numTabs) -> (Node, int):
            line = lines[lineNum]
            elements = line.split(" ")
            nodeType = elements[0]


            if nodeType == "DecisionNode":
                if elements[1].lower() == "action:":
                    func = None
                    functionName = elements[2]
                    found = False
                    for functionLists in allFunctionSets:
                        for function in functionLists:
                            if function.__name__ == functionName:
                                func = function
                                found = True
                                break
                        if found:
                            break

                    node = DecisionNode(func)
                
                else: #top tree
                    node = DecisionNode(None, int(elements[2]))
                return node, lineNum + 1


            if nodeType == "IfNode":
                firstChild, nextLineNum = recursiveBuildTree(lines, lineNum + 1, numTabs + 1)
                secondChild, nextLineNum = recursiveBuildTree(lines, nextLineNum, numTabs + 1)
                thirdChild, nextLineNum = recursiveBuildTree(lines, nextLineNum, numTabs + 1)
                #check if nextLine is infoNode with correct tabs
                if len(elements) == 2 and elements[1] == "WithInfo":
                    infoChild, nextLineNum = recursiveBuildTree(lines, nextLineNum, numTabs + 1)
                else:
                    infoChild = None
                node = IfNode(firstChild, secondChild, thirdChild, infoChild)
                return node, nextLineNum


            if nodeType == "InformationNode":
                functionName = elements[2]
                func = None
                found = False
                for functionLists in allFunctionSets:
                    for function in functionLists:
                        if function.__name__ == functionName:
                            func = function
                            found = True
                            break
                    if found:
                        break

                nextLineNum = lineNum + 1
                child = None
                #now check if nextline is one indent in
                if nextLineNum < len(lines) and lines[nextLineNum].startswith("\t"*(numTabs+1)):
                #if line[lineNum + 1][numTabs] ==  '\t': #one more mean after numTabs (but 0 indexed so good here)
                    #then its a child
                    child, nextLineNum = recursiveBuildTree(lines, nextLineNum, numTabs + 1)
                
                if func == None:
                    print("** building infoNode with no function! **")
                node = InformationNode(func, child)
                return node, nextLineNum


            if nodeType == "OperandNode":
                value = int(elements[2])
                node = OperandNode(value)
                return node, lineNum + 1


            if nodeType == "BooleanNode":

                if elements[1] == "function:":
                    functionName = elements[2]
                    func = None
                    found = False
                    for functionLists in allFunctionSets:
                        for function in functionLists:
                            if function.__name__ == functionName:
                                func = function
                                found = True
                                break
                        if found:
                            break

                    nextLineNum = lineNum + 1
                    node = BooleanNode(func)
                    return node, nextLineNum

                else:
                    #its an operation and has children
                    operation = operator.lt # TODO: rn we only do less than
                    nextLineNum = lineNum + 1
                    firstChild, nextLineNum = recursiveBuildTree(lines, nextLineNum, numTabs + 1)
                    secondChild, nextLineNum = recursiveBuildTree(lines, nextLineNum, numTabs + 1)

                    node = BooleanNode(None, operation = operation, firstChild = firstChild, secondChild = secondChild, isGCFunction = False)
                    return node, nextLineNum

            print("Returning None Node in recursiveBuildTree")
            return None, lineNum


        with open(directoryPath + "/" + fileNames[0], 'r') as f:
            lines = f.readlines()
            root, x = recursiveBuildTree(lines, 0, 0)
            topTree = DecisionTree(root)
            print("read topTree")

        with open(directoryPath + "/" + fileNames[1], 'r') as f:
            lines = f.readlines()
            root, x = recursiveBuildTree(lines, 0, 0)
            harvestTree = DecisionTree(root)
            print("read harvestTree")

        with open(directoryPath + "/" + fileNames[2], 'r') as f:
            lines = f.readlines()
            root, x = recursiveBuildTree(lines, 0, 0)
            attackTree = DecisionTree(root)
            print("read attackTree")

        with open(directoryPath + "/" + fileNames[3], 'r') as f:
            lines = f.readlines()
            root, x = recursiveBuildTree(lines, 0, 0)
            moveTree = DecisionTree(root)
            print("read movementTree")

        with open(directoryPath + "/" + fileNames[4], 'r') as f:
            lines = f.readlines()
            root, x = recursiveBuildTree(lines, 0, 0)
            buildTree = DecisionTree(root)
            print("read buildTree")

        player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
        return player
        







def createRandomDecisionTreePlayer():
    topTree = createBasicTopTree()
    harvestTree = createRandomHarvestTree()
    attackTree = createRandomAttackTree()
    moveTree = createRandomMoveTree()
    buildTree = createRandomBuildTree()

    player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
    return player



def Crossover1Player(p1, p2, probOfEachTree, probInSearch):
    '''
    p1 and p2 are players, probOfEachTree is the probability of doing crossover,
    probInSearch is the probability that helps crossover decide where to crossover.
    '''
    p1topTree, p2topTree = Crossover1(p1.topTree, p2.topTree, probOfEachTree, probInSearch)
    p1harvestTree, p2harvestTree = Crossover1(p1.harvestTree, p2.harvestTree, probOfEachTree, probInSearch)
    p1attackTree, p2attackTree = Crossover1(p1.attackTree, p2.attackTree, probOfEachTree, probInSearch)
    p1movementTree, p2movementTree = Crossover1(p1.movementTree, p2.movementTree, probOfEachTree, probInSearch)
    p1buildTree, p2buildTree = Crossover1(p1.buildTree, p2.buildTree, probOfEachTree, probInSearch)

    # No research tree rn
    newp1 = DecisionTreePlayer(p1topTree, p1harvestTree, p1attackTree, p1movementTree, p1buildTree)
    newp2 = DecisionTreePlayer(p2topTree, p2harvestTree, p2attackTree, p2movementTree, p2buildTree)

    return newp1, newp2



def MutatePlayer(player, probabilityPerNode, allFunctionSets):
    topTree = Mutate(player.topTree, probabilityPerNode, allFunctionSets)
    harvestTree = Mutate(player.harvestTree, probabilityPerNode, allFunctionSets)
    attackTree = Mutate(player.attackTree, probabilityPerNode, allFunctionSets)
    movementTree =Mutate(player.movementTree, probabilityPerNode, allFunctionSets)
    buildTree = Mutate(player.buildTree, probabilityPerNode, allFunctionSets)
    return DecisionTreePlayer(topTree, harvestTree, attackTree, movementTree, buildTree, None)






