'''
Selection
Crossover -> do it on nodes of the same type.
Mutation
'''

import DecisionTree
import Node
import random

def newValInRange(lower, upper):
    return random.randint(lower, upper + 1)

def newValInNormalizedRange(center, sigma):
    return int(random.gauss(center, sigma))


def Mutation(decisionTree, prob) -> DecisionTree:
    ''' Mutates the tree a little bit 
        OLD IMPLEMENTATION
    '''

    currNode = decisionTree.root
    height = 1 #the number of if nodes
    # We prefer smaller mutations, so we are going to mutate as a function of depth
    while(type(currNode) is not DecisionNode):

        if type(currNode) is IfNode:
            randVal = random.random()
            if randVal < prob * height:
                currNode = currNode.firstChild # we're mutating the boolean node
            elif randVal < 0.5 + (0.5 * prob):
                currNode = currNode.secondChild
            else:
                currNode = currNode.thirdChild
            height += 1


        elif type(currNode) is InformationNode: #We don't want to mess with necessary info yet until we have our dictionary of functions
            currNode = currNode.follow()

        elif type(currNode) is BooleanNode:
            randVal = random.random()
            if randVal < prob * height:
                #we mutate if it has operands
                if randVal < 0.5:
                    currNode = currNode.firstChild
                else:
                    currNode = currNode.secondChild
            #if its a function, We don't want to mess with necessary info yet until we have our dictionary of functions

        elif type(currNode) is OperandNode:
            currNode.value = newValInNormalizedRange(currNode.value, min(height, 3))
            return decisionTree
            

def recursiveDFSNodes(currNode, depth) -> list:
    '''returns a list of nodes under and including currNode'''
    nodes = []
    if currNode.firstChild:
        nodes += recursiveDFSNodes(currNode.firstChild, depth+1)
    if currNode.secondChild:
        nodes += recursiveDFSNodes(currNode.secondChild, depth+1)
    if currNode.thirdChild:
        nodes += recursiveDFSNodes(currNode.thirdChild, depth+1)
    #TODO: ignoring possible info node for if nodes
    nodes += [currNode]*depth
    return nodes


def Mutate(decisionTree, probabilityPerNode, allFunctionSets):
    ''' NEW IMPLEMENTATION
        mutates the trees just a bit by changing functions to like functions in Information and Decision Nodes
        Also can change the value of a operand node. ALl these changes done with some given probability.
    '''
    nodeQueue = []
    nodeQueue.append(decisionTree.root)

    while(len(nodeQueue) != 0):
        #add children to Queue
        currNode = nodeQueue.pop(0)
        if currNode.firstChild:
            nodeQueue.append(currNode.firstChild)
        if currNode.secondChild:
            nodeQueue.append(currNode.secondChild)
        if currNode.thirdChild:
            nodeQueue.append(currNode.thirdChild)

        if type(currNode) is IfNode:
            if currNode.infoChild:
                nodeQueue.append(currNode.infoChild)

        #if decision node, possibly mutate
        if type(currNode) is DecisionNode:

            if random.random() < probabilityPerNode:
                function = currNode.action
                for functionSet in allFunctionSets:
                    if function in functionSet:
                        newFunction = random.choice(functionSet)
                        print("Changing Decision Node function from " + currNode.action.__name__ + " to " + newFunction.__name__)
                        currNode.action = newFunction
                        break

        if type(currNode) is InformationNode:
            if random.random() < probabilityPerNode:
                function = currNode.function
                for functionSet in allFunctionSets:
                    if function in functionSet:
                        newFunction = random.choice(functionSet)
                        print("Changing Information Node function from " + currNode.function.__name__ + " to " + newFunction.__name__)
                        currNode.function = newFunction
                        break

        #if operandNode
        if type(currNode) is OperandNode:
            if random.random() < probabilityPerNode:
                newVal = newValInNormalizedRange(currNode.value, min(len(nodeQueue), 3)) #this is sorta random I guess
                print("Changing Operand Node value from " + str(currNode.value) + " to " + str(newVal))
                currNode.value = newVal

    return decisionTree





def Crossover1(treeA, treeB, probOfDoing, probInSearching) -> (DecisionTree, DecisionTree):
    ''' returns two trees that are crossed over.
        we can only do crossover on same type nodes
    '''
    if random.random() > probOfDoing:
        return (treeA, treeB)

    currNodeA = treeA.root
    heightA = 1 #the number of if nodes
    # We prefer smaller mutations, so we are going to mutate as a function of depth
    while(type(currNodeA) is not DecisionNode):
        randVal = random.random()
        if randVal < probInSearching*heightA:
            break;

        if type(currNodeA) is IfNode:
            #3 children
            heightA += 1
            if randVal < 0.33:
                currNodeA = currNodeA.firstChild
            elif randVal < 0.67:
                currNodeA = currNodeA.secondChild
            else:
                currNodeA = currNodeA.thirdChild
            #ignore optional info node until we have the dictionary

        elif type(currNodeA) is BooleanNode:
            # 0 or two children
            if currNodeA.firstChild == None:
                #Do a final test for staying
                if random.random() < probInSearching*heightA:
                    break;
            else:
                if randVal < 0.5:
                    currNodeA = currNodeA.firstChild
                else:
                    currNodeA = currNodeA.secondChild

        elif type(currNodeA) is InformationNode:
            currNodeA = currNodeA.follow()

        elif currNodeA == None:
            return (treeA, treeB)


    #now we search treeB for a node of the same type, weighting toward lower in the tree
    currNodeB = treeB.root
    heightB = 1
    nodes = recursiveDFSNodes(currNodeB, heightB);
    trimmedNodes = [node for node in nodes if type(node) is type(currNodeA)]
    nodeB = random.choice(trimmedNodes)

    currNodeA.swap(nodeB) #TODO: check these are working
    return (treeA, treeB)
        



def Selection():
    ''' TODO: to do this, we need to be able to run the trees from scripting '''
    return

