#import DecisionTreePlayer
#import DecisionTreeUtils
import battlecode as bc
import random
import sys
import traceback
import time
import os
from copy import copy, deepcopy
from collections import deque

#import DecisionTreeUtils
from enum import IntEnum
from enum import Enum
import operator

''' Begin Node.py '''

class Node:

    def __init__(self, firstChild = None, secondChild = None, thirdChild = None, identity = -1):
        self.firstChild = firstChild
        self.secondChild = secondChild
        self.thirdChild = thirdChild
        self.identity = identity

    def swap(self, node):
        temp1 = self.firstChild
        temp2 = self.secondChild
        temp3 = self.thirdChild
        self.firstChild = node.firstChild
        self.secondChild = node.secondChild
        self.thirdChild = node.thirdChild
        node.firstChild = temp1
        node.secondChild = temp2
        node.thirdChild = temp3

    def compareTo(self, node):
        return 0

    def printNode(self, indent):
        if self.firstChild:
            self.firstChild.printNode(indent + "\t")
        if self.secondChild:
            self.secondChild.printNode(indent + "\t")
        if self.thirdChild:
            self.thirdChild.printNode(indent + "\t")

    def getWriteString(self, indent):
        s = ""
        if self.firstChild:
            s += self.firstChild.getWriteString(indent + "\t")
        if self.secondChild:
            s += self.secondChild.getWriteString(indent + "\t")
        if self.thirdChild:
            s += self.thirdChild.getWriteString(indent + "\t")
        return s

    def setIdentity(self, newID):
        self.identity = newID



class IfNode(Node):
    #first child is the booleanNode, then the true subtree as secondChild then an else subtree as thirdChild.

    def __init__(self, firstChild, secondChild, thirdChild, infoChild = None, identity = -1):
        super().__init__(firstChild = firstChild, secondChild = secondChild, thirdChild = thirdChild, identity = identity)
        self.infoChild = infoChild 
        if firstChild == None:
            print("Creating if node with None firstChild")
        if secondChild == None:
            print("Creating if node with None secondChild")
        if thirdChild == None:
            print("Creating if node with None thirdChild")


    def swap(self, node):
        super().swap(node)
        temp1 = self.infoChild
        self.infoChild = node.infoChild
        node.infoChild = temp1

    def compareTo(self, node):
        val = 0 + super().compareTo(node)
        return val

    def printNode(self, indent):
        ending = ""
        if self.infoChild:
            ending = "WithInfo"
        print(indent + "At If Node" + ending)
        super().printNode(indent)
        if self.infoChild:
            self.infoChild.printNode(indent + '\t')

    def getWriteString(self, indent) -> str:
        ending = ""
        if self.infoChild:
            ending = "WithInfo"
        s = indent + "IfNode " + ending + "\n"
        s += super().getWriteString(indent)
        if self.infoChild:
            s += self.infoChild.getWriteString(indent + '\t')
        return s


    def follow(self, boardController, gc, permparams = [], ifparams = []) -> (Node, list):
        allparams = permparams.copy()
        newparams = []
        if self.infoChild:
           #print("This if node has an infoChild: collecting parameters")
            newparams = self.infoChild.evaluate(boardController, gc, permparams)
            ifparams.append(newparams) #if newparams is not None else None)
        #print("if params: ", ifparams)

        nextNode = self.firstChild
        boolParams = []
        while type(nextNode) is InformationNode:
            res = nextNode.evaluate(boardController, gc)
            boolParams.append(res) #if res is not None else None) 
            nextNode = nextNode.follow()
        #print ("boolParams: ", boolParams)
        #print ("allParams before ifParams: ", allparams)

        allparams += ifparams
        if nextNode.evaluate(boardController, gc, allparams + boolParams):
            #print("If evaluated as True")
            return (self.secondChild , ifparams)
        else:
            #print("If evaluated as False")
            return (self.thirdChild, ifparams)


class BooleanNode(Node):

    def __init__(self, function, params = [], operation = None, firstChild = None, secondChild = None, isGCFunction = True, identity = -1):
        super().__init__(firstChild = firstChild, secondChild = secondChild, identity = identity)
        self.function = function;
        self.isFunction = function != None
        self.params = params
        self.operation = operation
        self.isGCFunction = isGCFunction

    def swap(self, node):
        super().swap(node)
        temp1 = self.function
        temp2 = self.params
        temp3 = self.operation
        temp4 = self.isGCFunction
        self.function = node.function
        node.function = temp1
        self.params = node.params
        node.params = temp2
        self.operation = node.operation
        node.operation = temp3
        self.isGCFunction = node.isGCFunction
        node.isGCFunction = temp4

    def compareTo(self, node):
        val = super().compareTo(node)
        if self.function and node.function:
            if self.function is node.function:
                val += 1
        return val

    def printNode(self, indent):
        if (self.isFunction):
            print(indent + "At Boolean Node with function: " + self.function.__name__ )
            print(indent + "\tParams are " + str(self.params))
            if self.operation:
                print(indent + "operation is " + self.operation.__name__)
            super().printNode(indent)
        else:
            print(indent + "At Boolean Node: ")
            if self.operation:
                print(indent + "operation is " + self.operation.__name__)
            super().printNode(indent)


    def getWriteString(self, indent) -> str:
        s = ""
        if (self.isFunction):
            s += indent + "BooleanNode function: " + self.function.__name__ + "\n"
        else:
            if self.operation:
                s += indent + "BooleanNode operation: " + self.operation.__name__ + "\n"
        s += super().getWriteString(indent)
        return s


    def evaluate(self, battleCode, gc, moreParams = []) -> bool:
        #if moreParams != []:
            #print("Evaluating BooleanNode with params: ", moreParams)
        if self.isFunction:
        
            totalParams = self.params + moreParams
            try:
                res = self.function(battleCode, gc, *totalParams)
                #print("Successfully evaluated BooleanNode")
            except:
                res = self.function(gc, *totalParams)
            return res
        else:
            # we have operators and boolean expressions
            # TODO: How to represent boolean expressions

            ''' The operator, is this node, and the kids are the numbers/operands '''
            leftOperand = 1
            rightOperand = 1
            if type(self.firstChild) is OperandNode:
                leftOperand = self.firstChild.evaluate();
            elif type(self.firstChild) is InformationNode:
                leftOperand = self.firstChild.evaluate(battleCode, gc);
            if type(self.secondChild) is OperandNode:
                rightOperand = self.secondChild.evaluate();
            elif type(self.secondChild) is InformationNode:
                rightOperand = self.secondChild.evaluate(battleCode, gc);

            value = self.operation(leftOperand, rightOperand)
            '''
            if value:
                print("Boolean node evaluated as true")
            else:
                print("Boolean node evaluated as false")
            '''
            return value


class OperandNode(Node):
    def __init__(self, value, identity=-1):
        super().__init__(identity = identity)
        self.value = value

    def swap(self, node):
        super().swap(node)
        temp1 = self.value
        self.value = node.value
        node.value = temp1

    def compareTo(self, node):
        val = super().compareTo(node)
        if self.value == node.value:
            val += 1
        return val

    def printNode(self, indent):
        print(indent + "At Operand Node with value: "+ str(self.value))
        super().printNode(indent)

    def getWriteString(self, indent) -> str:
        s = indent + "OperandNode Value: " + str(self.value) + "\n"
        s += super().getWriteString(indent)
        return s

    def evaluate(self):
        #print("Operand Value of ", self.value)
        return self.value



class InformationNode(Node):
    def __init__(self, function, firstChild = None, identity = -1):
        super().__init__(firstChild, identity = identity)
        self.function = function

    def swap(self, node):
        super().swap(node)
        temp1 = self.function
        self.function = node.function
        node.function = temp1

    def compareTo(self, node):
        val = super().compareTo(node)
        if self.function is node.function:
            val += 1
        return val

    def printNode(self, indent):
        print(indent + "At Info Node with function: " + self.function.__name__ )
        super().printNode(indent)

    def getWriteString(self, indent) -> str:
        if self.function:
            s = indent + "InformationNode function: " + self.function.__name__ + "\n"
            s += super().getWriteString(indent)
            return s
        else:
            print("infoNode has no function ???????????")
            return super().getWriteString(indent)

    def evaluate(self, battleCode, gameController, params = []):
        print("function name", self.function.__name__)
        if params != []:
            return self.function(battleCode, gameController, *params)
        else:
            return self.function(battleCode, gameController)

    def follow(self):
        return self.firstChild



class ActionType(IntEnum):
    Harvest = 1
    Attack = 2
    Move = 3 #(or garrison)
    Build = 4 #(worker or factory)




class DecisionNode(Node):

    def __init__(self, action, typeOfActionToMake = 0, identity = -1):
        super().__init__(identity = identity)
        #self.unit = unit
        self.action = action
        self.typeOfActionToMake = typeOfActionToMake
        # 1 = Harvest
        # 2 = Attack
        # 3 = Move (or garrison)
        # 4 = Build (worker or factory)
        # 5 = Research

    def swap(self, node):
        super().swap(node)
        temp1 = self.action
        temp2 = self.typeOfActionToMake
        self.action = node.action
        self.typeOfActionToMake = node.typeOfActionToMake
        node.action = temp1
        node.typeOfActionToMake = temp2

    def compareTo(self, node):
        val = super().compareTo(node)
        if self.action and node.action:
            if self.action is node.action:
                val += 1
        if self.typeOfActionToMake == node.typeOfActionToMake:
            val += 1
        return val

    def printNode(self, indent):
        if self.action:
            print(indent + "At Decision Node with action: "+ self.action.__name__)
        if self.typeOfActionToMake != 0:
            print(indent + "At Decision Node with type of action is " + str(self.typeOfActionToMake))
        super().printNode(indent)

    def getWriteString(self, indent) -> str:
        if self.action:
            s = indent + "DecisionNode action: " + self.action.__name__ + "\n"
        else:
            s = indent + "DecisionNode typeOfActionToMake: " + str(int(self.typeOfActionToMake)) + "\n"
        s += super().getWriteString(indent)
        return s

    def execute(self, battleCode, gameController, params):

        # can have the helper functions to get our parameters
        print("Executing DecisionNode with params", params)

        if self.typeOfActionToMake != 0:
            return self.typeOfActionToMake;

        try:
            #gameController.action(unit)
            #gameController.action(*params) 
            
            self.action(battleCode, gameController, *params)
            #https://stackoverflow.com/questions/817087/call-a-function-with-argument-list-in-python
            
        except:
            self.action(gameController, *params)
            #https://stackoverflow.com/questions/32342729/pass-object-along-with-object-method-to-function
            

        #else:
        #    print("WARNING: EXITING program")
        #    exit(1)

        return None


'''End Node.py '''



class DecisionTree:

    def __init__(self, node, treeID = 0):
        self.root = node
        self.treeID = treeID


    def isLegal(self) -> bool:
        return True #TODO

    def printTree(self):
        self.root.printNode("")

    def getWriteString(self):
        return self.root.getWriteString("")

    def getNumNodes(self):
        #print("getting number of nodes in decision Tree")
        nodes = 0
        queue = [self.root]
        while (len(queue) != 0):
            currNode = queue.pop(0)
            nodes += 1
            if currNode.firstChild:
                queue.append(currNode.firstChild)
            if currNode.secondChild:
                queue.append(currNode.secondChild)
            if currNode.thirdChild:
                queue.append(currNode.thirdChild)
            if type(currNode) is IfNode:
                if currNode.infoChild:
                    queue.append(currNode.infoChild)

        return nodes


    def compareTo(self, tree):
        return 0 #TODO

    def execute(self, battleCode, gameController):
        #print("Executing a decision Tree")
        currNode = self.root
        ifParams = []
        permanantParams = []
        while(type(currNode) is not DecisionNode):

            #print("At a node of type", type(currNode));
            if type(currNode) is IfNode:
                ifNode = currNode #IfNode(currNode)
                #print("permparams before: ", permanantParams)
                currNode, ifParams = ifNode.follow(battleCode, gameController, permanantParams, ifParams)
                #print("permparams after: ", permanantParams)

            elif type(currNode) is InformationNode: 
                #Information nodes not imediately under ifNodes' first children have their information stored
                # This is useful for say, selecting a unit
                permanantParams.append(currNode.evaluate(battleCode, gameController))
                currNode = currNode.follow()

            elif type(currNode) is BooleanNode:
                #why would we end up here?
                print("ERROR: Decision Tree execute is at a BooleanNode")

            else:
                print ("ERROR: Decision Tree execute at currNode of type", type(currNode))
                print ("    This should only get to ifNodes and then finish at a DecisionNode, but not in this loop")
                return
        # Now currNode is a DecisionNode.
        if type(currNode) is DecisionNode:
            result = currNode.execute(battleCode, gameController, permanantParams + ifParams)
            return result #None if this executed an action, number otherwise indicating which action tree to use
            # 1 = Harvest
            # 2 = Attack
            # 3 = Move (or garrison)
            # 4 = Build (worker or factory)
            # 5 = Research
        else:
            print("ERROR: execute DecisionTree did not terminate at a DecisionNode");
            print("\t", type(currNode))




class FixedSizeDecisionTree(DecisionTree):

    def __init__(self, node, idNum = 0, height = 4):
        self.root = node
        self.id = idNum
        self.height = height

    def isLegal(self) -> bool:
        depth = 1
        queue = [(self.root, depth)]
        while (len(queue) != 0):
            currNode, currDepth = queue.pop(0)
            if currDepth > self.height:
                return False
            if type(currNode) is DecisionNode and currDepth != self.height:
                return False
            if currNode.firstChild:
                queue.append((currNode.firstChild, currDepth+1))
            if currNode.secondChild:
                queue.append((currNode.secondChild, currDepth+1))
            if currNode.thirdChild:
                queue.append((currNode.thirdChild, currDepth+1))
            if type(currNode) is IfNode:
                if currNode.infoChild:
                    queue.append((currNode.infoChild, currDepth+1))


        return True # TODO, test this

    def printTree(self):
        self.root.printNode("")

    def getWriteString(self):
        return self.root.getWriteString("")

    def getNumNodes(self):
        nodes = 0
        queue = [self.root]
        while (len(queue) != 0):
            currNode = queue.pop(0)
            nodes += 1
            if currNode.firstChild:
                queue.append(currNode.firstChild)
            if currNode.secondChild:
                queue.append(currNode.secondChild)
            if currNode.thirdChild:
                queue.append(currNode.thirdChild)
            if type(currNode) is IfNode:
                if currNode.infoChild:
                    queue.append(currNode.infoChild)

        return nodes


    def compareTo(self, tree):
        ''' 
            gives a fitness evaluation based on the comparison between nodes. 
            Nodes higher in the tree are weighted more heavily. 
            This is used to test our GP operators without running the time-intesive game
        '''
        x = super().compareTo(tree)
        val = 0
        queue = [(self.root, tree.root, 1)]
        while (len(queue) != 0):
            nodeA, nodeB, currHeight  = queue.pop(0)
            multiplier = 2 **(self.height - currHeight)
            toAdd = nodeA.compareTo(nodeB) * multiplier 
            val += toAdd

            if type(nodeA) is IfNode:
                if nodeA.firstChild:
                    queue.append((nodeA.firstChild, nodeB.firstChild, currHeight))
                if nodeA.secondChild:
                    queue.append((nodeA.secondChild, nodeB.secondChild, currHeight+1))
                if nodeA.thirdChild:
                    queue.append((nodeA.thirdChild, nodeB.thirdChild, currHeight+1))

                if nodeA.infoChild:
                    queue.append((nodeA.infoChild, nodeB.infoChild, currHeight+1))
            else: 
                if nodeA.firstChild:
                    queue.append((nodeA.firstChild, nodeB.firstChild, currHeight+1))
                if nodeA.secondChild:
                    queue.append((nodeA.secondChild, nodeB.secondChild, currHeight+1))

        return val


    def execute(self, battleCode, gameController):
        print("Executing a fixed size decision tree of type", self.id)
        currNode = self.root
        ifParams = []
        permanantParams = []
        while(type(currNode) is not DecisionNode):

            #print("At a node of type", type(currNode));
            if type(currNode) is IfNode:
                ifNode = currNode #IfNode(currNode)
                currNode, ifParams = ifNode.follow(battleCode, gameController, permanantParams, ifParams)

            elif type(currNode) is InformationNode: 
                #Information nodes not imediately under ifNodes' first children have their information stored
                # This is useful for say, selecting a unit
                #print("Appending to permanantParams")
                permanantParams.append(currNode.evaluate(battleCode, gameController))
                currNode = currNode.follow()

            elif type(currNode) is BooleanNode:
                #why would we end up here?
                print("ERROR: Decision Tree execute is at a BooleanNode")

            else:
                print ("ERROR: Decision Tree execute at currNode of type", type(currNode))
                print ("    This should only get to ifNodes and then finish at a DecisionNode, but not in this loop")
                return
        # Now currNode is a DecisionNode.
        if type(currNode) is DecisionNode:
            result = currNode.execute(battleCode, gameController, permanantParams + ifParams)
            return result #None if this executed an action, number otherwise indicating which action tree to use
            # 1 = Harvest
            # 2 = Attack
            # 3 = Move (or garrison)
            # 4 = Build (worker or factory)
            # 5 = Research
        else:
            print("ERROR: execute DecisionTree did not terminate at a DecisionNode");
            print("\t", type(currNode))


    def setNodeIdNumbers(self):
        ''' BFS set Id numbers of Nodes starting at node 0 -> the root'''
        nodeID = 0
        queue = [self.root]
        while (len(queue) != 0):
            currNode = queue.pop(0)
            currNode.setIdentity(nodeID)
            nodeID += 1
            if currNode.firstChild:
                queue.append(currNode.firstChild)
            if currNode.secondChild:
                queue.append(currNode.secondChild)
            if currNode.thirdChild:
                queue.append(currNode.thirdChild)
            if type(currNode) is IfNode:
                if currNode.infoChild:
                    queue.append(currNode.infoChild)

        return None

''' End FixedSizeDecisionTree '''




''' Begin DecisionTreeUtils.py '''

# Helper Functions for creating a tree
def createRandomTopTreeDecisionNode():
    actionType = random.choice(list(ActionType))
    node = DecisionNode(None, actionType)
    return node


def createRandomValOperandNode(mean, stdev):
    intval = int(random.gauss(mean, stdev))
    node = OperandNode(intval)
    return node


#def createRandomBoardInfoOperandNode(boardController):

'''
    Harvest = 1
    Attack = 2
    Move = 3 #(or garrison)
    Build = 4 #(worker or factory)
    Research = 5
'''

def createIdealTopTree() -> FixedSizeDecisionTree:
    ''' 
        A basic Fixed Size Tree that we use as dummy test to make sure GP code works
    '''
    print("creating ideal top tree")
    harvestNode = DecisionNode(None, ActionType.Harvest)
    buildNode1 = DecisionNode(None, ActionType.Build)
    getKarboniteNode = InformationNode(getKarbonite)
    node150 = OperandNode(150)
    karbonite150BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getKarboniteNode, secondChild = node150, isGCFunction = False)
    ifKarbonite150Node = IfNode(karbonite150BoolNode, harvestNode, buildNode1)

    buildNode2 = DecisionNode(None, ActionType.Build)
    moveNode1 = DecisionNode(None, ActionType.Move)
    getFactoriesNode = InformationNode(getNumberOfFactories)
    nodeFactory1 = OperandNode(1)
    factory1BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getFactoriesNode, secondChild = nodeFactory1, isGCFunction = False)
    ifFactory1Node = IfNode(factory1BoolNode, buildNode2, moveNode1)

    getWorkersNode = InformationNode(getNumberOfWorkers)
    nodeWorkers4 = OperandNode(4)
    workers4BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getWorkersNode, secondChild = nodeWorkers4, isGCFunction = False)
    if4WorkersNode = IfNode(workers4BoolNode, ifKarbonite150Node, ifFactory1Node)

    #Now right side of the tree
    buildNode3 = DecisionNode(None, ActionType.Build)
    moveNode2 = DecisionNode(None, ActionType.Move)
    getRangersNode = InformationNode(getNumberOfRangers)
    nodeRangers3 = OperandNode(3)
    rangers3BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getRangersNode, secondChild = nodeRangers3, isGCFunction = False)
    if3RangersNode = IfNode(rangers3BoolNode, buildNode3, moveNode2)

    attackNode = DecisionNode(None, ActionType.Attack)
    moveNode3 = DecisionNode(None, ActionType.Move)
    getRoundNode1 = InformationNode(getRoundNumber)
    nodeRound500 = OperandNode(500)
    round500BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getRoundNode1, secondChild = nodeRound500, isGCFunction = False)
    ifRound500Node = IfNode(round500BoolNode, attackNode, moveNode3)

    getRocketsNode = InformationNode(getNumberOfRockets)
    nodeRockets1 = OperandNode(1)
    rockets1BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getRocketsNode, secondChild = nodeRockets1, isGCFunction = False)
    if1RocketsNode = IfNode(rockets1BoolNode, if3RangersNode, ifRound500Node)

    #now connect the two halves
    getRoundNode2 = InformationNode(getRoundNumber)
    nodeRound250 = OperandNode(250)
    round250BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getRoundNode2, secondChild = nodeRound250, isGCFunction = False)
    ifRound250Node = IfNode(round250BoolNode, if4WorkersNode, if1RocketsNode)

    return FixedSizeDecisionTree(ifRound250Node, 0, 4)


def createIdealMoveTree() -> FixedSizeDecisionTree:
    ''' My own move tree to use GP on to improve '''
    print("creating ideal move tree")
    moveFromBuildingNode1 = DecisionNode(unitMoveAwayFromBuilding)
    workerAction3Node = DecisionNode(workerActionBehavior3)
    selectRandomWorkerNode1 = DecisionNode(selectRandomWorker)
    getKarboniteNode1 = InformationNode(getKarbonite)
    nodeKarbonite100 = OperandNode(100)
    karbonite100BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getKarboniteNode1, secondChild = nodeKarbonite100, isGCFunction = False)
    if100KarboniteIfNode = IfNode(karbonite100BoolNode, moveFromBuildingNode1, workerAction3Node, selectRandomWorkerNode1)

    moveFromBuildingNode2 = DecisionNode(unitMoveAwayFromBuilding)
    moveFromBuildingNode3 = DecisionNode(unitMoveAwayFromBuilding)
    selectRandomWorkerNode2 = DecisionNode(selectRandomWorker)
    isWorkerBoolNode1 = BooleanNode(isWorker)
    isWorkerIfNode1 = IfNode(isWorkerBoolNode1, moveFromBuildingNode2, moveFromBuildingNode3, selectRandomWorkerNode2)

    getFactoriesNode = InformationNode(getNumberOfFactories)
    nodeFactories2 = OperandNode(2)
    factories2BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getFactoriesNode, secondChild = nodeFactories2, isGCFunction = False)
    if2FactoriesIfNode = IfNode(factories2BoolNode, if100KarboniteIfNode, isWorkerIfNode1)

    #second group on left side
    moveFromBuildingNode4 = DecisionNode(unitMoveAwayFromBuilding)
    moveRandomly = DecisionNode(unitMoveRandomBehavior)
    selectMoveableUnitNode = InformationNode(selectRandomUnitThatCanMove)
    isWorkerBoolNode2 = BooleanNode(isWorker)
    isWorkerIfNode2 = IfNode(isWorkerBoolNode2, moveFromBuildingNode4, moveRandomly, selectMoveableUnitNode)

    moveTowardEnemyNode1 = DecisionNode(unitMoveTowardEnemyBehavior)
    moveTowardEnemyNode2 = DecisionNode(unitMoveTowardEnemyBehavior)
    selectMovableAttackerNode1 = InformationNode(selectUnitThatCanAttackToMove)
    isAttackerBoolNode1 = BooleanNode(isAttacker)
    isAttackerIfNode1 = IfNode(isAttackerBoolNode1, moveTowardEnemyNode1, moveTowardEnemyNode2, selectMovableAttackerNode1)

    getNumAttackersNode = InformationNode(getNumberOfAttackers)
    nodeAttackers4 = OperandNode(4)
    attackers4BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getNumAttackersNode, secondChild = nodeAttackers4, isGCFunction = False)
    if4AttackersIfNode = IfNode(attackers4BoolNode, isWorkerIfNode2, isAttackerIfNode1)

    getNumWorkersNode = InformationNode(getNumberOfWorkers)
    nodeWorkers4 = OperandNode(4)
    workers4BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getNumWorkersNode, secondChild = nodeWorkers4, isGCFunction = False)
    if4WorkersIfNode = IfNode(workers4BoolNode, if2FactoriesIfNode, if4AttackersIfNode)

    #now the right side
    moveTowardEnemyNode3 = DecisionNode(unitMoveTowardEnemyBehavior)
    moveAwayFromEnemyNode1 = DecisionNode(unitMoveAwayFromEnemy)
    selectMovableAttackerNode2 = InformationNode(selectUnitThatCanAttackToMove)
    isKnightBoolNode1 = BooleanNode(isKnight)
    isKnightIfNode1 = IfNode(isKnightBoolNode1, moveTowardEnemyNode3, moveAwayFromEnemyNode1, selectMovableAttackerNode2)

    moveTowardEnemyNode4 = DecisionNode(unitMoveTowardEnemyBehavior)
    moveAwayFromEnemyNode2 = DecisionNode(unitMoveAwayFromEnemy)
    selectMovableAttackerNode3 = InformationNode(selectUnitThatCanAttackToMove)
    isKnightBoolNode2 = BooleanNode(isKnight)
    isKnightIfNode2 = IfNode(isKnightBoolNode2, moveTowardEnemyNode4, moveAwayFromEnemyNode2, selectMovableAttackerNode3)

    getNumRangersNode = InformationNode(getNumberOfRangers)
    nodeRangers3 = OperandNode(3)
    rangers3BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getNumRangersNode, secondChild = nodeRangers3, isGCFunction = False)
    if3RangersIfNode = IfNode(rangers3BoolNode, isKnightIfNode1, isKnightIfNode2)

    #second group on right side
    moveIntoRocketNode = DecisionNode(unitMoveIntoClosestRocket)
    moveFromBuildingNode5 = DecisionNode(unitMoveAwayFromBuilding)
    selectMovableAttackerNode4 = InformationNode(selectUnitThatCanAttackToMove)
    isAttackerBoolNode2 = BooleanNode(isAttacker)
    isAttackerIfNode2 = IfNode(isAttackerBoolNode1, moveIntoRocketNode, moveFromBuildingNode5, selectMovableAttackerNode4)

    launchNode1 = DecisionNode(launch_rocket_to_mars)
    launchNode2 = DecisionNode(launch_rocket_to_mars)
    selectFullestRocketNode = InformationNode(select_rocket_with_most_units_garrisoned)
    isRocketBoolNode = BooleanNode(isRocket)
    isRocketIfNode = IfNode(isRocketBoolNode, launchNode1, launchNode2, selectFullestRocketNode)

    getMaxGarrisonNode = InformationNode(getMaxNumberOfUnitsInEarthRocket)
    nodeGarrisoned3 = OperandNode(3)
    garrisoned3BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getMaxGarrisonNode, secondChild = nodeGarrisoned3, isGCFunction = False)
    if3GarrisonedIfNode = IfNode(garrisoned3BoolNode, isAttackerIfNode2, isRocketIfNode)

    #combine right side
    getNumRocketsNode = InformationNode(getNumberOfRockets)
    nodeRockets1 = OperandNode(1)
    rockets1BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getNumRocketsNode, secondChild = nodeRockets1, isGCFunction = False)
    if1RocketsIfNode = IfNode(rockets1BoolNode, if3RangersIfNode, if3GarrisonedIfNode)

    #now combine left and right
    getRoundNode = InformationNode(getRoundNumber)
    nodeRound300 = OperandNode(300)
    round300BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getRoundNode, secondChild = nodeRound300, isGCFunction = False)
    ifRound300IfNode = IfNode(round300BoolNode, if4WorkersIfNode, if1RocketsIfNode)

    return FixedSizeDecisionTree(ifRound300IfNode, 3, 5)



def createIdealBuildTree() -> FixedSizeDecisionTree:
    print("Creating ideal build tree")
    buildFactoryNode1 = DecisionNode(workerBuildFactory)
    buildWorkerNode1 = DecisionNode(factory_produce_worker)
    selectBuilderNode1 = InformationNode(selectBuilderThatCanBuild)
    isWorkerNode1 = BooleanNode(isWorker)
    ifIsWorkerNode1 = IfNode(isWorkerNode1, buildFactoryNode1, buildWorkerNode1, selectBuilderNode1)

    workerReplicateNode1 = DecisionNode(workerBuildBehavior)
    buildRangerNode1 = DecisionNode(factory_produce_ranger)
    selectBuilderNode2 = InformationNode(selectBuilderThatCanBuild)
    isWorkerNode2 = BooleanNode(isWorker)
    ifIsWorkerNode2 = IfNode(isWorkerNode2, workerReplicateNode1, buildRangerNode1, selectBuilderNode2)

    getNumFactoriesNode = InformationNode(getNumberOfFactories)
    nodeFactories2 = OperandNode(2)
    factories2BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getNumFactoriesNode, secondChild = nodeFactories2, isGCFunction = False)
    if2FactoriesIfNode = IfNode(factories2BoolNode, ifIsWorkerNode1, ifIsWorkerNode2)

    #2nd 4th of tree (middle left)
    buildAttackerNode1 = DecisionNode(factory_produce_attacker)
    buildAttackerNode2 = DecisionNode(factory_produce_attacker)
    selectFactoryNode1 = InformationNode(selectRandomFactory)
    isFactoryNode1 = BooleanNode(isFactory)
    ifIsFactoryNode1 = IfNode(isFactoryNode1, buildAttackerNode1, buildAttackerNode2, selectFactoryNode1)

    buildRocketNode1 = DecisionNode(workerBuildRocket)
    buildRocketNode2 = DecisionNode(workerBuildRocket)
    selectWorkerNode1 = InformationNode(selectWorkerThatCanBuild)
    isWorkerNode3 = BooleanNode(isWorker)
    ifIsWorkerNode3 = IfNode(isWorkerNode3, buildRocketNode1, buildRocketNode2, selectWorkerNode1)

    getRoundNode1 = InformationNode(getRoundNumber)
    nodeRound500 = OperandNode(500)
    round500BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getRoundNode1, secondChild = nodeRound500, isGCFunction = False)
    ifRound500Node = IfNode(round500BoolNode, ifIsFactoryNode1, ifIsWorkerNode3)

    # left half
    getRoundNode2 = InformationNode(getRoundNumber)
    nodeRound250 = OperandNode(250)
    round250BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getRoundNode2, secondChild = nodeRound250, isGCFunction = False)
    ifRound250Node = IfNode(round250BoolNode, if2FactoriesIfNode, ifRound500Node)

    #start right half
    buildRangerNode2 = DecisionNode(factory_produce_ranger)
    buildAttackerNode3 = DecisionNode(factory_produce_attacker)
    selectFactoryNode2 = InformationNode(selectRandomFactory)
    isFactoryNode2 = BooleanNode(isFactory)
    ifIsFactoryNode2 = IfNode(isFactoryNode2, buildRangerNode2, buildAttackerNode3, selectFactoryNode2)

    buildRocketNode3 = DecisionNode(workerBuildRocket)
    buildAttackerNode4 = DecisionNode(factory_produce_attacker)
    selectBuilderNode3 = InformationNode(selectBuilderThatCanBuild)
    isWorkerNode4 = BooleanNode(isWorker)
    ifIsWorkerNode4 = IfNode(isWorkerNode4, buildRocketNode3, buildAttackerNode4, selectBuilderNode3)

    getAttackersNode = InformationNode(getNumberOfAttackers)
    nodeAttackers8 = OperandNode(8)
    attackers8BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getAttackersNode, secondChild = nodeAttackers8, isGCFunction = False)
    if8AttackersNode = IfNode(attackers8BoolNode, ifIsFactoryNode2, ifIsWorkerNode4)

    #last 4th
    buildRangerNode3 = DecisionNode(factory_produce_ranger)
    buildRangerNode4 = DecisionNode(factory_produce_ranger)
    selectFactoryNode3 = InformationNode(selectRandomFactory)
    isFactoryNode3 = BooleanNode(isFactory)
    ifIsFactoryNode3 = IfNode(isFactoryNode3, buildRangerNode3, buildRangerNode4, selectFactoryNode3)

    buildRocketNode4 = DecisionNode(workerBuildRocket)
    buildRangerNode5 = DecisionNode(factory_produce_ranger)
    selectBuilderNode4 = InformationNode(selectBuilderThatCanBuild)
    isWorkerNode5 = BooleanNode(isWorker)
    ifIsWorkerNode5 = IfNode(isWorkerNode5, buildRocketNode4, buildRangerNode5, selectBuilderNode4)

    getMaxGarrisonNode = InformationNode(getMaxNumberOfUnitsInEarthRocket)
    nodeGarrison5 = OperandNode(5)
    garrison5BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getMaxGarrisonNode, secondChild = nodeGarrison5, isGCFunction = False)
    if5GarrisonNode = IfNode(garrison5BoolNode, ifIsFactoryNode3, ifIsWorkerNode5)

    getRoundNode3 = InformationNode(getRoundNumber)
    nodeRound600 = OperandNode(600)
    round600BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getRoundNode3, secondChild = nodeRound600, isGCFunction = False)
    ifRound600Node = IfNode(round600BoolNode, if8AttackersNode, if5GarrisonNode)

    #bridge two sides
    getRocketsNode = InformationNode(getNumberOfRockets)
    nodeRockets1 = OperandNode(1)
    rockets1BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getRocketsNode, secondChild = nodeRockets1, isGCFunction = False)

    if1RocketsNode = IfNode(rockets1BoolNode, ifRound250Node, ifRound600Node)
    return FixedSizeDecisionTree(if1RocketsNode, 4, 5)

    

def createIdealHarvestTree() -> FixedSizeDecisionTree:
    print("creating ideal harvest tree")
    harvestNode1 = DecisionNode(workerHarvestBehavior)
    cantHarvestNode = DecisionNode(workerCantHarvestBehavior)
    selectWorkerNode = InformationNode(selectWorkerToMoveTowardHarvesting)
    canHarvestBoolNode = BooleanNode(worker_unit_can_harvest)
    ifCanHarvestNode = IfNode(canHarvestBoolNode, harvestNode1, cantHarvestNode, selectWorkerNode)

    replicateNode = DecisionNode(workerReplicate)
    harvestNode2 = DecisionNode(workerHarvestBehavior)
    selectRandomWorkerNode = InformationNode(selectRandomWorker)

    getWorkersNode = InformationNode(getNumberOfWorkers)
    nodeWorkers4 = OperandNode(4)
    workers4BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getWorkersNode, secondChild = nodeWorkers4, isGCFunction = False)
    if4WorkersNode = IfNode(workers4BoolNode, replicateNode, harvestNode2, selectRandomWorkerNode)

    getKarboniteNode = InformationNode(getKarbonite)
    nodeKarbonite300 = OperandNode(300)
    karbonite300BoolNode = BooleanNode(None, operation = operator.lt, firstChild = getKarboniteNode, secondChild = nodeKarbonite300, isGCFunction = False)
    if300KarboniteNode = IfNode(karbonite300BoolNode, ifCanHarvestNode, if4WorkersNode)

    return FixedSizeDecisionTree(if300KarboniteNode, 1,3)



def createIdealAttackTree() -> FixedSizeDecisionTree:
    print("creating ideal attack tree")
    attackNode1 = DecisionNode(nonWorkerAttackBehavior)
    attackNode2 = DecisionNode(nonWorkerAttackBehavior)
    selectAttackerNode = InformationNode(selectUnitDealingMostDamageThatCanAttack)
    isAttackerBoolNode1 = BooleanNode(isAttacker)
    ifIsAttackerNode1 = IfNode(isAttackerBoolNode1, attackNode1, attackNode2, selectAttackerNode)

    moveTowardEnemyNode = DecisionNode(unitMoveTowardEnemyBehavior)
    moveAwayFromEnemyNode = DecisionNode(unitMoveAwayFromEnemy)
    selectMovableUnitNode = InformationNode(selectRandomUnitThatCanMove)
    isAttackerBoolNode2 = BooleanNode(isAttacker)
    ifIsAttackerNode2 = IfNode(isAttackerBoolNode2, moveTowardEnemyNode, moveAwayFromEnemyNode, selectMovableUnitNode)

    canAttackBoolNode = BooleanNode(canAnyUnitAttack)
    ifCanAttackNode = IfNode(canAttackBoolNode, ifIsAttackerNode1, ifIsAttackerNode2)

    return FixedSizeDecisionTree(ifCanAttackNode, 2, 3)



def createBasicTopTree() -> DecisionTree:
    attackNode = DecisionNode(None, ActionType.Attack)
    harvestNode = DecisionNode(None, ActionType.Harvest)
    moveNode = DecisionNode(None, ActionType.Move)
    buildNode = DecisionNode(None, ActionType.Build)
    randomProbNode1 = BooleanNode(randomChance)
    randomProbNode2 = BooleanNode(randomChance)
    randomProbNode3 = BooleanNode(randomChance)

    lastIf = IfNode(randomProbNode3, moveNode, attackNode)
    secondIf = IfNode(randomProbNode2, buildNode, lastIf)
    firstIf = IfNode(randomProbNode1, harvestNode, secondIf)
    topTree = DecisionTree(firstIf, 0)
    return topTree


def createBasicHarvestTree() -> DecisionTree:
    harvestNode = DecisionNode(workerHarvestBehavior)
    workerSelectNode = InformationNode(selectRandomWorker, harvestNode)
    harvestTree = DecisionTree(workerSelectNode, 1)
    return harvestTree


def createBasicBuildTree() -> DecisionTree:
    workerBuildNode = DecisionNode(workerBuildBehavior)
    workerBuildRocketNode = DecisionNode(workerBuildRocket)
    randomProbNode1 = BooleanNode(randomChance, [0.2])
    randomProbNode2 = BooleanNode(randomChance, [0.5])
    
    selectWorkerNode1 = InformationNode(selectRandomWorker, workerBuildRocketNode)
    selectWorkerNode2 = InformationNode(selectRandomWorker, workerBuildNode)
    workerIfNode = IfNode(randomProbNode1, selectWorkerNode1, selectWorkerNode2)

    buildUnitNode = DecisionNode(factory_produce_random)
    selectRandomFactoryNode = InformationNode(selectRandomFactory, buildUnitNode)
    
    factoryIfNode = IfNode(randomProbNode2, selectRandomFactoryNode, workerIfNode)

    buildTree = DecisionTree(factoryIfNode, 4)
    return buildTree


def createBasicMoveTree() -> DecisionTree:
    #need to pick where to move the unit. Bottom Up construction
    moveRandomDirectionNode = DecisionNode(unitMoveRandomBehavior)
    moveTowardEnemyNode = DecisionNode(unitMoveTowardEnemyBehavior)
    moveTowardAllyNode = DecisionNode(unitMoveTowardAllyBehavior)

    isWorkerNode = BooleanNode(isWorker)
    elseIfWorkerNode = IfNode(isWorkerNode, moveRandomDirectionNode, moveTowardEnemyNode)

    isHealerNode = BooleanNode(isHealer)
    selectUnitNode = InformationNode(selectRandomUnitThatCanMove, None)
    ifHealerNode = IfNode(isHealerNode, moveTowardAllyNode, elseIfWorkerNode, selectUnitNode)
    #need to pick a unit
    #selectUnitNode = InformationNode(selectRandomUnitThatCanMove, ifHealerNode)
    #moveTree = DecisionTree(selectUnitNode)
    moveTree = DecisionTree(ifHealerNode, 3)
    return moveTree


def createBasicAttackTree() -> DecisionTree:
    
    attackBehaviorNode = DecisionNode(nonWorkerAttackBehavior)
    #select Unit
    selectUnitNode = InformationNode(selectRandomRobotForAttack, attackBehaviorNode)
    attackTree = DecisionTree(selectUnitNode, 2)
    return attackTree;

def createBasicResearchTree() -> DecisionTree:
    node = DecisionNode(random_unit_type);
    return DecisionTree(node, 5); #TODO: total hogwash right now.



# Helper Functions for the game
def selectRandomFactory(battleCode, gc):
    factories = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Factory]
    if factories != []:
        return random.choice(factories)
    return None

def selectRandomWorker(battleCode, gc):
    workers = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Worker]
    #print(workers)
    if workers != []:
        return random.choice(workers)
    print("There are no workers to choose from")
    return None

def selectRandomKnight(battleCode, gc):
    knights = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Knight]
    if knights != []:
        return random.choice(knights)
    return None

def selectRandomRanger(battleCode, gc):
    rangers = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Ranger]
    if rangers != []:
        return random.choice(rangers)
    return None

def selectRandomMage(battleCode, gc):
    mages = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Mage]
    if mages != []:
        return random.choice(mages)
    return None

def selectRandomHealer(battleCode, gc):
    healers = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Healer]
    if healers:
        return random.choice(healers)
    return None

def selectRandomMoveableUnit(battleCode, gc):
    units = [x for x in gc.my_units() if x.unit_type != battleCode.UnitType.Factory]
    units = [x for x in units if x.unit_type != battleCode.UnitType.Rocket]
    print("selectRandomMoveableUnit has units length of ", len(units))
    if units != []:
        return random.choice(units)
    print("No units were found that can be moved in selectRandomMoveableUnit")
    return None

def selectRandomRobotForAttack(battleCode, gc):
    nonWorkers = [x for x in gc.my_units() if x.unit_type != battleCode.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != battleCode.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != battleCode.UnitType.Worker]
    if nonWorkers != []:
        return random.choice(nonWorkers)
    return None


def selectUnitTypesThatCanAttack(bc, gc):
    #TODO: Not in all_functions\
    nonWorkers = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Worker]
    attackReady = [x for x in nonWorkers if gc.is_attack_ready(x.id)]
    can_attack = []
    my_team = gc.team()
    enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
    for unit in attackReady:
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    can_attack.append(unit)
                    break
    types = set()
    for u in can_attack:
        types.add(u.UnitType)
    return list(types)



def selectRandomUnitThatCanAttack(bc, gc):
    nonWorkers = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Worker]
    attackReady = [x for x in nonWorkers if gc.is_attack_ready(x.id)]
    can_attack = []
    my_team = gc.team()
    enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
    for unit in attackReady:
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    can_attack.append(unit)
                    break

    if len(can_attack) != 0:
        return random.choice(can_attack)
    else:
        return selectRandomRobotForAttack(bc,gc)


def selectUnitDealingMostDamageThatCanAttack(bc, gc):
    nonWorkers = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Worker]
    attackReady = [x for x in nonWorkers if gc.is_attack_ready(x.id)]

    can_attack = []
    my_team = gc.team()
    enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
    for unit in attackReady:
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    can_attack.append(unit)
                    break

    random.shuffle(can_attack)
    bestUnit = None
    for u in can_attack:
        if bestUnit == None:
            bestUnit = u
        if u.damage() > bestUnit.damage():
            bestUnit = u

    return bestUnit


def selectUnitWithLeastLifeThatCanAttack(bc, gc):
    nonWorkers = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Worker]
    attackReady = [x for x in nonWorkers if gc.is_attack_ready(x.id)]

    can_attack = []
    my_team = gc.team()
    enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
    for unit in attackReady:
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    can_attack.append(unit)
                    break

    random.shuffle(can_attack)
    leastLife = None
    for u in can_attack:
        if leastLife == None:
            leastLife = u
        if u.health < leastLife.health:
            leastLife = u

    return leastLife


def canAnyUnitAttack(bc, gc) -> bool:
    nonWorkers = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Worker]
    attackReady = [x for x in nonWorkers if gc.is_attack_ready(x.id)]

    my_team = gc.team()
    enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
    for unit in attackReady:
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    return True

    return False



def selectRandomUnitThatCanMove(bc, gc):
    movables = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    movables = [x for x in movables if x.unit_type != bc.UnitType.Rocket]
    moveReady = [x for x in movables if gc.is_move_ready(x.id)]
    can_move = []
    for unit in moveReady:
        random_directions = list(bc.Direction)
        # Iterate through each direction
        for direct1 in random_directions:
            if gc.can_move(unit.id, direct1):
                can_move.append(unit)
                break
    if len(can_move) != 0:
        return random.choice(can_move)
    else:
        return selectRandomMoveableUnit(bc, gc)


def selectUnitThatCanAttackToMove(bc, gc):
    movables = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    movables = [x for x in movables if x.unit_type != bc.UnitType.Rocket]
    moveReady = [x for x in movables if gc.is_move_ready(x.id)]
    moveAttackReady = [x for x in moveReady if gc.is_attack_ready(x.id)]
    can_move = []
    for unit in moveAttackReady:
        random_directions = list(bc.Direction)
        # Iterate through each direction
        for direct1 in random_directions:
            if gc.can_move(unit.id, direct1):
                can_move.append(unit)
                break
    if len(can_move) != 0:
        return random.choice(can_move)
    else:
        return selectRandomUnitThatCanMove(bc, gc)



def selectWorkerToMoveTowardHarvesting(bc, gc):
    movables1 = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Worker]
    movables2 = [x for x in movables1 if gc.is_move_ready(x.id)]
    if len(movables2) != 0:
        return random.choice(movables2)
    else:
        return random.choice(movables1)


def selectWorkerThatCanBuild(bc, gc):
    workers = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Worker]
    earthWorkers = [x for x in workers if x.location.map_location().planet == bc.Planet.Earth]
    return random.choice(earthWorkers)

def selectBuilderThatCanBuild(bc, gc):
    workers = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Worker]
    earthWorkers = [x for x in workers if x.location.map_location().planet == bc.Planet.Earth]
    factories = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Factory]
    both = earthWorkers + factories
    x = random.choice(both)
    return x

def selectRandomRocket(battleCode, gc):
    rockets = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Rocket]
    if rockets != []:
        return random.choice(rockets)
    return None


# Boolean Functions
def isKnight(battleCode, gc, unit):
    if isinstance(unit, battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Knight
    return False

def isRanger(battleCode, gc, unit):
    if isinstance(unit, battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Ranger
    return False

def isMage(battleCode, gc, unit):
    if isinstance(unit, battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Mage
    return False

def isHealer(battleCode, gc, unit):
    if isinstance(unit, battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Healer
    return False

def isWorker(battleCode, gc, unit):
    if isinstance(unit, battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Worker
    return False

def isFactory(battleCode, gc, unit):
    if isinstance(unit, battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Factory
    return False

def isRocket(battleCode, gc, unit):
    if isinstance(unit, battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Rocket
    return False
    
def isAttacker(battleCode, gc, unit):
    if isinstance(unit, battleCode.Unit):
        return isKnight(battleCode, gc, unit) or isRanger(battleCode, gc, unit) or isMage(battleCode, gc, unit)
    return False


#Behaviors
def workerHarvestBehavior(battleCode, gc, unit):
    if unit:
        bot_can_harvest = worker_can_harvest(battleCode, gc, unit.id)

        if bot_can_harvest:
            gc.harvest(unit.id, bot_can_harvest)
    return


def workerCantHarvestBehavior(bc, gc, unit):
    ''' put worker in position to harvest '''
    if unit:
        if unit.worker_has_acted():
            return None
        #for each location around the unit 2 spaces away, check if can harvest, go towards it
        currMapLocation = unit.location.map_location()
        random_directions = list(bc.Direction)
        random.shuffle(random_directions)
        # Iterate through each direction
        directToGo = random_directions[0]
        bestKarbonite = 0
        for direct1 in random_directions:
            if not gc.can_move(unit.id, direct1):
                continue
            totalKarbonite = 0
            for direct2 in random_directions:
                totalKarbonite += gc.karbonite_at(currMapLocation.add(direct1).add(direct2))
            if totalKarbonite > bestKarbonite:
                directToGo = direct1

        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, directToGo):
            gc.move_robot(unit.id, directToGo)
    return None



def workerBuildBehavior(battleCode, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(battleCode, gc, unit)

        #replicate
        if bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
            gc.replicate(unit.id, bot_occupiable)

        #build if possible
        elif gc.karbonite() > battleCode.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, battleCode.UnitType.Factory, bot_occupiable):
            gc.blueprint(unit.id, battleCode.UnitType.Factory, bot_occupiable)

        # lastly, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == battleCode.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    #print('built a factory!')
                    continue
    return None


def workerBuildFactory(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, bot_occupiable):
            gc.blueprint(unit.id, bc.UnitType.Factory, bot_occupiable)

        # lastly, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    #print('built a factory!')
                    continue
    return None

def workerReplicate(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        if bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
            gc.replicate(unit.id, bot_occupiable)
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    #print('built a factory!')
                    continue
    return None


def workerActionBehavior1(bc, gc, unit):
    if unit:
        d = random.choice(list(bc.Direction))
        bot_can_harvest = worker_can_harvest(bc, gc, unit.id)
        bot_occupiable = find_occupiable(bc, gc, unit)

        #build if possible
        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, bot_occupiable):
            gc.blueprint(unit.id, bc.UnitType.Factory, bot_occupiable)

        #harvest
        elif bot_can_harvest:
            gc.harvest(unit.id, bot_can_harvest)

        #replicate
        elif bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
            gc.replicate(unit.id, bot_occupiable)

        # lastly, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    #print('built a factory!')
                    continue
    return

def workerActionBehavior2(bc, gc, unit):
    if unit:
        d = random.choice(list(bc.Direction))
        bot_can_harvest = worker_can_harvest(bc, gc, unit.id)
        bot_occupiable = find_occupiable(bc, gc, unit)

        #harvest
        if bot_can_harvest:
            gc.harvest(unit.id, bot_can_harvest)

        #build if possible
        elif gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, bot_occupiable):
            gc.blueprint(unit.id, bc.UnitType.Factory, bot_occupiable)

        #replicate
        elif bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
            gc.replicate(unit.id, bot_occupiable)

        # lastly, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    #print('built a factory!')
                    continue
    return

def workerActionBehavior3(bc, gc, unit):
    if unit:
        d = random.choice(list(bc.Direction))
        bot_can_harvest = worker_can_harvest(bc, gc, unit.id)
        bot_occupiable = find_occupiable(bc, gc, unit)

        #replicate
        if bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
            gc.replicate(unit.id, bot_occupiable)

        #harvest
        elif bot_can_harvest:
            gc.harvest(unit.id, bot_can_harvest)

        #build if possible
        elif gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, bot_occupiable):
            gc.blueprint(unit.id, bc.UnitType.Factory, bot_occupiable)

        # lastly, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    #print('built a factory!')
                    continue
    return

def workerBuildRocket(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and bot_occupiable and gc.can_blueprint(unit.id, bc.UnitType.Rocket, bot_occupiable):
            gc.blueprint(unit.id, bc.UnitType.Rocket, bot_occupiable)
    return

def unitMoveRandomBehavior(bc, gc, unit):
    if unit:
        d = random.choice(list(bc.Direction))
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)
    return

def unitMoveTowardEnemyBehavior(battleCode, gc, unit):
    if unit:
        d = get_direction_of_closest_enemy(battleCode, gc, unit)
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)
        else:
            unitMoveRandomBehavior(battleCode, gc, unit)
    return

def unitMoveTowardAllyBehavior(battleCode, gc, unit):
    if unit:
        d = get_direction_of_closest_ally(battleCode, gc, unit)
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)
        else:
            unitMoveRandomBehavior(battleCode,gc, unit)
    return

def unitMoveIntoClosestRocket(bc, gc, unit):
    if unit:
        rockets = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Rocket]
        for rocket in rockets:
            if gc.can_load(rocket.id, unit.id):
                gc.load(rocket.id, unit.id)
                return
        direction = get_direction_of_closest_rocket(bc, gc, unit)
        gc.move_robot(unit.id, direction)

    return None

def getOpposite3Directions(direction):
    if direction == bc.Direction.East:
        return [bc.Direction.West, bc.Direction.Northwest, bc.Direction.Southwest]
    if direction == bc.Direction.Northeast:
        return [bc.Direction.West, bc.Direction.South, bc.Direction.Southwest]
    if direction == bc.Direction.North:
        return [bc.Direction.Southeast, bc.Direction.South, bc.Direction.Southwest]
    if direction == bc.Direction.Northwest:
        return [bc.Direction.East, bc.Direction.South, bc.Direction.Southeast]
    if direction == bc.Direction.West:
        return [bc.Direction.East, bc.Direction.Southeast, bc.Direction.Northeast]
    if direction == bc.Direction.Southwest:
        return [bc.Direction.East, bc.Direction.North, bc.Direction.Northeast]
    if direction == bc.Direction.South:
        return [bc.Direction.Northwest, bc.Direction.North, bc.Direction.Northeast]
    if direction == bc.Direction.Southeast:
        return [bc.Direction.West, bc.Direction.North, bc.Direction.Northwest]
    if direction == bc.Direction.Center:
        return list(bc.Direction)


def unitMoveAwayFromBuilding(bc, gc, unit):
    if unit:
        if gc.is_move_ready(unit.id):
            rockets = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Rocket]
            factories = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Factory]
            buildings = rockets + factories
            direction = get_direction_of_closest_building(bc, gc, unit)
            possibleDirections = getOpposite3Directions(direction)
            movableDirections = [x for x in possibleDirections if gc.can_move(unit.id, x)]
            if len(movableDirections) == 0:
                #move random
                allDirections = list(bc.Direction)
                canMoveIn = [x for x in allDirections if gc.can_move(unit.id, x)]
                if len(canMoveIn) > 0:
                    moveIn = random.choice(canMoveIn)
                    gc.move_robot(unit.id, moveIn)
                    return None
                else: 
                    return None
            else:
                # we look at any direction
                movableDirections = [x for x in list(bc.Direction) if gc.can_move(unit.id, x)]
                if len(movableDirections) > 0:
                    gc.move_robot(unit.id, random.choice(movableDirections))
                else:
                    print("unit can move in no direction")
        else:
            print("unit is not move ready!")

    return None

def unitMoveAwayFromEnemy(bc, gc, unit):
    if unit:
        if gc.is_move_ready(unit.id):
            direction = get_direction_of_closest_enemy(bc, gc, unit)
            possibleDirections = getOpposite3Directions(direction)
            movableDirections = [x for x in possibleDirections if gc.can_move(unit.id, x)]
            if len(movableDirections) == 0:
                #move random
                allDirections = list(bc.Direction)
                canMoveIn = [x for x in allDirections if gc.can_move(unit.id, x)]
                if len(canMoveIn) > 0:
                    moveIn = random.choice(canMoveIn)
                    gc.move_robot(unit.id, moveIn)
                    return None
                else: 
                    return None
            else:
                moveIn = random.choice(possibleDirections)
                gc.move_robot(unit.id, moveIn)

    return None


def nonWorkerAttackBehavior(battleCode, gc, unit):
    if unit:
        if unit.unit_type == battleCode.UnitType.Knight:
            return knight_action(battleCode, gc, unit)
        if unit.unit_type == battleCode.UnitType.Ranger:
            return ranger_action(battleCode, gc, unit)
        if unit.unit_type == battleCode.UnitType.Mage:
            return mage_action(battleCode, gc, unit)
        if unit.unit_type == battleCode.UnitType.Healer:
            return healer_action(battleCode, gc, unit)


# Taken straight from the medium player
def rocketBehavior(bc, gc, unit):
    if unit:
        my_team = gc.team()
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units_by_team(location.map_location(), 9, my_team)
            for other in nearby:
                if other.team == my_team and gc.can_load(unit.id, other.id):
                    # print('Loaded a ' + other.unit_type + ' into rocket!')
                    gc.load(unit.id, other.id)
                    continue
        destination = rocket_destination(bc, gc, unit.id)
        if gc.can_launch_rocket(unit.id, destination) and (len(unit.structure_garrison()) >= 6 or gc.round() >= 400): #leave these numbers for now
            gc.launch_rocket(unit.id, destination)
        if unit.location.map_location().planet == bc.Planet.Mars:
            bot_occupiable = find_occupiable(bc, gc, unit)
            if bot_occupiable:
                gc.unload(unit.id, find_occupiable(bc, gc, unit))
    return



def factory_produce_worker(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, bc.UnitType.Worker, bot_occupiable)
    return
    
def factory_produce_knight(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, bc.UnitType.Knight, bot_occupiable)
    return

def factory_produce_mage(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, bc.UnitType.Mage, bot_occupiable)
    return

def factory_produce_ranger(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, bc.UnitType.Ranger, bot_occupiable)
    return

def factory_produce_healer(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, bc.UnitType.Healer, bot_occupiable)
    return

def factory_produce_random(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, random_unit_type(bc), bot_occupiable)
    return

def factory_produce_attacker(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        attackerTypes = [bc.UnitType.Knight, bc.UnitType.Ranger, bc.UnitType.Mage]
        unit_type = random.choice(attackerTypes)
        factory_produce(bc, gc, unit, unit_type, bot_occupiable)
    return


def knight_action(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        bot_occupiable = find_occupiable(bc, gc, unit)
        # Check whether there is something to attack
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units_by_team(location.map_location(), 50, enemy_team)
            for other in nearby:
                if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    #print('Knight attacked a thing!')
                    gc.attack(unit.id, other.id)
                    return #we only want to attack

        if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
                direction = get_direction_of_closest_enemy(bc, gc, unit)
                if direction:
                    gc.move_robot(unit.id, direction)
                else:
                    gc.move_robot(unit.id, bot_occupiable)



def ranger_action(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        bot_occupiable = find_occupiable(bc, gc, unit)
        # Check whether there is something to attack
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units_by_team(location.map_location(), 50, enemy_team)
            for other in nearby:
                if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    #print('Knight attacked a thing!')
                    gc.attack(unit.id, other.id)
                    return #we only want to attack

        if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
                direction = get_direction_of_closest_enemy(bc, gc, unit)
                if direction:
                    gc.move_robot(unit.id, direction)
                else:
                    gc.move_robot(unit.id, bot_occupiable)

def mage_action(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        bot_occupiable = find_occupiable(bc, gc, unit)
        # Check whether there is something to attack
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units_by_team(location.map_location(), 50, enemy_team)
            for other in nearby:
                if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    #print('Knight attacked a thing!')
                    gc.attack(unit.id, other.id)
                    return #we only want to attack

        if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
                direction = get_direction_of_closest_enemy(bc, gc, unit)
                if direction:
                    gc.move_robot(unit.id, direction)
                else:
                    gc.move_robot(unit.id, bot_occupiable)

def healer_action(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        # Check whether there is something to attack
        location = unit.location

        if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
                direction = get_direction_of_closest_ally(bc, gc, unit)
                if direction:
                    gc.move_robot(unit.id, direction)
                else:
                    gc.move_robot(unit.id, bot_occupiable)


''' The following were taken from the medium player's helper functions '''

#gives adjacent direction or space for a unit to move or place something
def find_occupiable(bc, gc, unit):
    if unit:
        if unit.location.is_in_garrison():
            return None
        # Create a random order of directions
        random_directions = list(bc.Direction)
        random.shuffle(random_directions)
        # Iterate through each direction
        for direct in random_directions:
            #print(str(unit.location.map_location().add(dir).clone()) + " ;P" )
            if unit.location.map_location().add(direct):
                loc = unit.location.map_location().add(direct)
            else:
                continue
            loc_map = gc.starting_map(loc.planet)

            if (loc.x < loc_map.width and loc.x >= 0 and loc.y < loc_map.height and loc.y >= 0
                and gc.is_occupiable(unit.location.map_location().add(direct))):
                #if gc.can_move(unit.id, dir) and gc.is_occupiable(unit.location.map_location().add(dir)):
                return direct
    return None

def worker_can_harvest(bc, gc, unit_id):
    for direct in list(bc.Direction):
        if gc.can_harvest(unit_id, direct):
             return direct
    return None

def worker_unit_can_harvest(bc, gc, unit) -> bool:
    if unit:
        direct = worker_can_harvest(bc, gc, unit.id)
        if direct is not None: 
            return True
        else:
            return False
    else: 
        return False

def worker_get_direct_for_harvest(bc, gc, unit):
    if unit:
        return worker_can_harvest(bc,gc, unit.id)
    return None

def factory_produce(bc, gc, unit, unit_type, bot_occupiable):
    if unit:
        garrison = unit.structure_garrison()
        if len(garrison) > 0:
            if bot_occupiable and gc.can_unload(unit.id, bot_occupiable):
                gc.unload(unit.id, bot_occupiable)
        elif gc.can_produce_robot(unit.id, unit_type):
            gc.produce_robot(unit.id, unit_type)

def random_unit_type(battleCode):
    unit_types = [battleCode.UnitType.Knight, battleCode.UnitType.Ranger, battleCode.UnitType.Mage, battleCode.UnitType.Healer]
    return random.choice(unit_types)

def rocket_destination(battleCode, gc, unit_id):
    x = random.randint(0, gc.starting_map(battleCode.Planet.Mars).width)
    y = random.randint(0, gc.starting_map(battleCode.Planet.Mars).height)
    location = battleCode.MapLocation(battleCode.Planet.Mars, x, y)
    if gc.starting_map(battleCode.Planet.Mars).is_passable_terrain_at(location):
        return battleCode.MapLocation(battleCode.Planet.Mars, x, y)
    else:
        return rocket_destination(battleCode, gc, unit_id)

def get_direction_of_closest_enemy(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        closest_enemy_dist = 99999
        closest_enemy_id = None
        direction = None
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                distance = unit.location.map_location().distance_squared_to(other.location.map_location())
                if distance < closest_enemy_dist:
                    closest_enemy_dist = distance
                    closest_enemy_id = other.id;
                    if closest_enemy_id:
                        direction = unit.location.map_location().direction_to(other.location.map_location())
        if direction:                
            return direction
        else:
            return random.choice(list(bc.Direction))
    return random.choice(list(bc.Direction))

def get_direction_of_closest_ally(bc, gc, unit):
    if unit:
        closest_ally_dist = 99999
        closest_ally_id = None
        direction = None
        my_team = gc.team();
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, my_team)
        for other in nearby:
            if other.team == my_team:
                distance = unit.location.map_location().distance_squared_to(other.location.map_location())
                if distance < closest_ally_dist:
                    closest_ally_dist = distance
                    closest_ally_id = other.id;
                    if closest_ally_id:
                        direction = unit.location.map_location().direction_to(other.location.map_location())
        return direction
    return random.choice(list(bc.Direction))


def get_direction_of_closest_rocket(bc, gc, unit):
    if unit:
        closest_rocket_dist = 99999
        closest_rocket = None
        direction = None
        rockets = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Rocket]
        if len(rockets) > 0:
            for rocket in rockets:
                distance = unit.location.map_location().distance_squared_to(rocket.location.map_location())
                if distance < closest_rocket_dist:
                    closest_rocket_dist = distance
                    closest_rocket = rocket
                    if closest_rocket:
                        direction = unit.location.map_location().direction_to(closest_rocket.location.map_location())
            return direction
    return random.choice(list(bc.Direction))

def get_direction_of_closest_building(bc, gc, unit):
    if unit:
        closest_rocket_dist = 99999
        closest_rocket = None
        direction = None
        rockets = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Rocket]
        factories = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Factory]
        buildings = factories + rockets
        if len(buildings) > 0:
            for rocket in buildings:
                distance = unit.location.map_location().distance_squared_to(rocket.location.map_location())
                if distance < closest_rocket_dist:
                    closest_rocket_dist = distance
                    closest_rocket = rocket
                    if closest_rocket:
                        direction = unit.location.map_location().direction_to(closest_rocket.location.map_location())
            return direction
    return random.choice(list(bc.Direction))


def randomChance(bc, gc, chanceTrue = 0.25) -> bool:
    roll = random.random()
    return roll <= chanceTrue



def unitAttackRandomPossibleEnemy(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        enemies_in_range = []
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    enemies_in_range.append(other)
        enemy = random.choice(enemies_in_range)
        gc.attack(unit.id, enemy.id)
    return None #we attacked


def unitAttackClosestPossibleEnemy(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        closest_enemy_dist = 99999
        closest_enemy_id = None
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                distance = unit.location.map_location().distance_squared_to(other.location.map_location())
                if distance < closest_enemy_dist:
                    closest_enemy_dist = distance
                    closest_enemy_id = other.id;
        gc.attack(unit.id, closest_enemy_id)
    return None #we attacked


def getRoundNumber(bc, gc):
    return gc.round()

def getNumberOfWorkers(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Worker ]
    return len(y)

def getNumberOfFactories(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Factory]
    return len(y)

def getNumberOfRockets(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Rocket ]
    return len(y)

def getNumberOfKnights(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Knight ]
    return len(y)

def getNumberOfRangers(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Ranger ]
    return len(y)

def getNumberOfMages(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Mage ]
    return len(y)

def getNumberOfHealers(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Healer ]
    return len(y)

def getKarbonite(bc, gc):
    return gc.karbonite()

def getNumberOfAttackers(bc, gc):
    return getNumberOfMages(bc, gc) + getNumberOfRangers(bc, gc) + getNumberOfKnights(bc, gc)

def getMaxNumberOfUnitsInEarthRocket(bc, gc):
    rockets = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Rocket]
    earthRockets = [x for x in rockets if x.location.map_location().planet == bc.Planet.Earth]
    maxUnits = 0
    for rocket in earthRockets:
        garrisonSize = len(rocket.structure_garrison())
        if garrisonSize > maxUnits:
            maxUnits = garrisonSize
    return maxUnits

def select_random_rocket(bc, gc):
    rockets = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Rocket]
    if len(rockets) > 0:
        return random.choice(rockets)
    return None


def select_rocket_with_most_units_garrisoned(bc, gc):
    rockets = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Rocket]
    if len(rockets) == 0:
        return None
    bestRocket = None
    mostUnits = -1
    for rocket in rockets:
        numUnits = len(rocket.structure_garrison())
        if numUnits > mostUnits:
            bestRocket = rocket
            mostUnits = numUnits
    return bestRocket


def select_earth_rocket_with_most_units_garrisoned(bc, gc):
    rockets = [x for x in gc.my_units() if x.unit_type is bc.UnitType.Rocket]
    if len(rockets) == 0:
        return None
    earthRockets = [x for x in rockets if x.location.map_location().planet == bc.Planet.Earth]
    bestRocket = None
    mostUnits = -1
    for rocket in earthRockets:
        numUnits = len(rocket.structure_garrison())
        if numUnits > mostUnits:
            bestRocket = rocket
            mostUnits = numUnits
    return bestRocket


def launch_rocket_to_mars(bc, gc, unit):
    if unit:
        destination = rocket_destination(bc, gc, unit.id)
        if gc.can_launch_rocket(unit.id, destination): 
            print("Launching a Rocket!")
            gc.launch_rocket(unit.id, destination)
    return




'''

I want to define some lists of similar functions in order to mutate 
Preferably, each function only is in one group.

'''


#params are bc, gc
select_factory_functions = [
    selectRandomFactory,
]

# params are bc, gc, unit of type factory
factory_produce_functions = [
    factory_produce_worker,
    factory_produce_knight,
    factory_produce_mage,
    factory_produce_ranger,
    factory_produce_healer,
    factory_produce_random,
    factory_produce_attacker
]


#params are bc, gc
select_worker_functions = [
    selectRandomWorker
]

select_worker_build_functions = [
    selectRandomWorker,
    selectWorkerThatCanBuild
]

worker_harvest_functions = [
    workerHarvestBehavior
]

worker_build_functions = [
    workerBuildBehavior,
    workerBuildFactory,
    workerReplicate,
    workerBuildRocket
]

#params are bc, gc, unit of type worker
worker_behavior_functions = [
    #workerBuildBehavior,
    workerActionBehavior1,
    workerActionBehavior2,
    workerActionBehavior3
    #workerBuildRocket
]

select_builder_functions = [
    selectBuilderThatCanBuild
] 

#params are bc, gc
select_knight_functions = [
    selectRandomKnight
]

#params are bc, gc, unit of type knight
knight_action_functions = [
    knight_action
]

#params are bc, gc
select_ranger_functions = [
    selectRandomRanger
]

#params are bc, gc, unit of type ranger
ranger_action_functions = [
    ranger_action
]

#params are bc, gc
select_mage_functions = [
    selectRandomMage
]

#params are bc, gc, unit of type ranger
mage_action_functions = [
    mage_action
]

#params are bc, gc
select_healer_functions = [
    selectRandomHealer
]

#params are bc, gc, unit of type ranger
healer_action_functions = [
    healer_action
]

select_attacker_functions = [
    selectRandomUnitThatCanAttack,
    selectUnitDealingMostDamageThatCanAttack,
    selectUnitWithLeastLifeThatCanAttack
]

select_moveable_unit_functions = [
    selectRandomUnitThatCanMove,
    selectUnitThatCanAttackToMove,
    selectWorkerToMoveTowardHarvesting
]

unit_attack_functions = [
    unitAttackClosestPossibleEnemy,
    unitAttackRandomPossibleEnemy
]

unit_heal_functions = [
    healer_action #todo, this isn't a correct function for this
]

unit_move_functions = [
    unitMoveRandomBehavior,
    unitMoveTowardAllyBehavior,
    unitMoveTowardEnemyBehavior,
    unitMoveIntoClosestRocket,
    unitMoveAwayFromEnemy,
    unitMoveAwayFromBuilding
]

worker_can_harvest_functions = [
    worker_unit_can_harvest
]

worker_cant_harvest_functions = [
    workerCantHarvestBehavior
]

game_number_info_functions = [
    getRoundNumber,
    getNumberOfWorkers,
    getNumberOfFactories,
    getNumberOfKnights,
    getNumberOfRangers,
    getNumberOfMages,
    getNumberOfHealers,
    getNumberOfRockets,
    getKarbonite,
    getNumberOfAttackers,
    getMaxNumberOfUnitsInEarthRocket
]

boolean_game_info_functions = [
    canAnyUnitAttack
]

random_chance_function = [
    randomChance
]

is_unit_type_functions = [
    isHealer,
    isKnight,
    isWorker,
    isRanger,
    isMage,
    isFactory,
    isRocket,
    isAttacker
]

select_rocket_functions = [
    select_random_rocket,
    select_rocket_with_most_units_garrisoned,
    select_earth_rocket_with_most_units_garrisoned
]

rocket_action_functions = [
    launch_rocket_to_mars
]


allFunctionSets = [
    select_factory_functions,
    factory_produce_functions,
    select_worker_functions,
    select_worker_build_functions,
    worker_harvest_functions,
    worker_build_functions,
    worker_behavior_functions,
    select_knight_functions,
    knight_action_functions,
    select_ranger_functions,
    ranger_action_functions,
    select_mage_functions,
    mage_action_functions,
    select_healer_functions,
    healer_action_functions,
    select_rocket_functions,
    rocket_action_functions,
    select_attacker_functions,
    select_moveable_unit_functions,
    unit_attack_functions,
    unit_heal_functions,
    unit_move_functions,
    worker_can_harvest_functions,
    worker_cant_harvest_functions,
    game_number_info_functions,
    random_chance_function,
    is_unit_type_functions,
    select_builder_functions,
    boolean_game_info_functions
]

game_number_info_functions_number_mappings = {
    getRoundNumber : [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 750],
    getNumberOfWorkers : [1,2,4,7,11],
    getNumberOfFactories : [1,2,3],
    getNumberOfKnights : [1,2,3,5],
    getNumberOfRangers : [1,3,5,8],
    getNumberOfMages : [1,3,5,8],
    getNumberOfHealers : [1,2,3],
    getNumberOfRockets : [1,2],
    getKarbonite : [50,100,150,200,250,300,350,400,450,500],
    getNumberOfAttackers: [1,4,8,12],
    getMaxNumberOfUnitsInEarthRocket: [1,3,5]
}


def createRandomAttackTree():
    selectUnitFunction = random.choice(select_attacker_functions)
    selectUnitInfoNode = InformationNode(selectUnitFunction)
    
    isHealerNode = BooleanNode(isHealer)

    healFunction = random.choice(unit_heal_functions)
    healDecisionNode = DecisionNode(healFunction)

    if random.random() <= .75:
        # we do a separate function for Knight and ranged
        isKnightNode = BooleanNode(isKnight)
        knightAttackFunction = random.choice(unit_attack_functions)
        knightAttackDecisionNode = DecisionNode(knightAttackFunction)

        if random.random() <= .66:
            #separate for mage and ranger
            isRangerNode = BooleanNode(isRanger)
            rangerAttackFunction = random.choice(unit_attack_functions)
            rangerAttackNode = DecisionNode(rangerAttackFunction)
            mageAttackFunction = random.choice(unit_attack_functions)
            mageAttackNode = DecisionNode(mageAttackFunction)

            ifRangerNode = IfNode(isRangerNode, rangerAttackNode, mageAttackNode)
            ifKnightNode = IfNode(isKnightNode, knightAttackDecisionNode, ifRangerNode)

        else:
            rangedAttackFunction = random.choice(unit_attack_functions)
            rangedAttackDecisionNode = DecisionNode(rangedAttackFunction)
            ifKnightNode = IfNode(isKnightNode, knightAttackDecisionNode, rangedAttackDecisionNode)

        root = IfNode(isHealerNode, healDecisionNode, ifKnightNode, selectUnitInfoNode)
        return DecisionTree(root, 2)


    else:
        attackFunction = random.choice(unit_attack_functions)
        attackDecisionNode = DecisionNode(attackFunction)

        root = IfNode(isHealerNode, healDecisionNode, attackDecisionNode, selectUnitInfoNode)
        return DecisionTree(root, 2)



def recursiveRandomAttackSubtree(maxRecursion, currentRecursion, percentRecurse) -> Node: #TODO, remove build specifics
    isHealerNode = BooleanNode(isHealer)
    healFunction = random.choice(unit_heal_functions)
    healDecisionNode = DecisionNode(healFunction)
        

    firstCheckFunction = random.choice(game_number_info_functions)
    firstChildLeftNode = InformationNode(firstCheckFunction)
    if firstCheckFunction is getRoundNumber:
        firstChildRightNode = OperandNode(random.randint(0,999))
        # TODO money caps at 400 if not gathering it
    elif firstCheckFunction is getKarbonite:
        firstChildRightNode = OperandNode(random.randint(0,400))
    else:
        firstChildRightNode = createRandomValOperandNode(5,2)
    firstCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = firstChildLeftNode, secondChild = firstChildRightNode, isGCFunction = False)

    if currentRecursion == maxRecursion:
        #force Decision Node both
        attackFunction1 = random.choice(unit_attack_functions)
        attackDecisionNode1 = DecisionNode(attackFunction1)
        attackFunction2 = random.choice(unit_attack_functions)
        attackDecisionNode2 = DecisionNode(attackFunction2)
        junctionNode = IfNode(firstCheckBoolNode, attackDecisionNode1, attackDecisionNode2)
        ifHealerNode = IfNode(isHealerNode, healDecisionNode, junctionNode)
        return ifHealerNode


    if percentRecurse < random.random():
        #force Decision node left:
        if percentRecurse < random.random():
            #Also force Decision node right:
            attackFunction1 = random.choice(unit_attack_functions)
            attackDecisionNode1 = DecisionNode(attackFunction1)
            attackFunction2 = random.choice(unit_attack_functions)
            attackDecisionNode2 = DecisionNode(attackFunction2)
            junctionNode = IfNode(firstCheckBoolNode, attackDecisionNode1, attackDecisionNode2)
            ifHealerNode = IfNode(isHealerNode, healDecisionNode, junctionNode)
            return ifHealerNode

        else:
            #only the left is Decision
            attackFunction1 = random.choice(unit_attack_functions)
            attackDecisionNode1 = DecisionNode(attackFunction1)
            rChildNode = recursiveRandomAttackSubtree(maxRecursion, currentRecursion+1, percentRecurse)
            junctionNode = IfNode(firstCheckBoolNode, attackDecisionNode1, rChildNode)
            ifHealerNode = IfNode(isHealerNode, healDecisionNode, junctionNode)
            return ifHealerNode


    elif percentRecurse < random.random():
        #force ONLY Decision node right:
        attackFunction2 = random.choice(unit_attack_functions)
        attackDecisionNode2 = DecisionNode(attackFunction2)
        lChildNode = recursiveRandomAttackSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        junctionNode = IfNode(firstCheckBoolNode, lChildNode, attackDecisionNode2)
        ifHealerNode = IfNode(isHealerNode, healDecisionNode, junctionNode)
        return ifHealerNode

    else:
        #recurse
        lChildNode = recursiveRandomAttackSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        rChildNode = recursiveRandomAttackSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
        ifHealerNode = IfNode(isHealerNode, healDecisionNode, junctionNode)
        return ifHealerNode


def createRandomFixedSizeAttackTree(height):
    '''
        height includes the Decision nodes so should have height - 1 layes of IfNodes
    '''
    lowestIfs = []
    layer = height - 1
    for i in range(2**(layer)):
        selectUnitFunction = random.choice(select_attacker_functions)
        selectUnitInfoNode = InformationNode(selectUnitFunction)

        attackFunc = random.choice(unit_attack_functions)
        healFunc = random.choice(unit_heal_functions)
        attackNode = DecisionNode(attackFunc)
        healNode = DecisionNode(healFunc)

        isHealerNode = BooleanNode(isHealer)

        ifNode = IfNode(isHealerNode, healNode, attackNode, selectUnitInfoNode)

        lowestIfs.append(ifNode)
    layer -= 1
    nextLayerIfs = lowestIfs

    while (layer >= 1):
        newLayer = []
        for i in range(2**(layer-1)):
            lowerNode1 = nextLayerIfs.pop()
            lowerNode2 = nextLayerIfs.pop()
            usedFuncs = getFixedSizeTreeBoolCheckFunctionsUsed(lowerNode1)
            usedFuncs = usedFuncs | getFixedSizeTreeBoolCheckFunctionsUsed(lowerNode2)
            possibleFuncs = set(game_number_info_functions) - usedFuncs
            if len(possibleFuncs) == 0:
                infoFunc = random.choice(game_number_info_functions)
            else: 
                infoFunc = random.choice(list(possibleFuncs))
            infoNode = InformationNode(infoFunc)
            opVal = random.choice(game_number_info_functions_number_mappings[infoFunc])
            opNode = OperandNode(opVal)

            boolNode = BooleanNode(None, operation = operator.lt, firstChild = infoNode, secondChild = opNode, isGCFunction = False) 
            ifNode = IfNode(boolNode, lowerNode1, lowerNode2)
            newLayer.append(ifNode)

        layer -= 1
        nextLayerIfs = newLayer
    # done now on the top layer
    root = nextLayerIfs[0]
    return FixedSizeDecisionTree(root, 2, height)




def createRandomHarvestTree():
    selectUnitFunction = random.choice(select_worker_functions)
    selectUnitInfoNode = InformationNode(selectUnitFunction)

    workerCanHarvestFunction = random.choice(worker_can_harvest_functions)
    canHarvestNode = BooleanNode(workerCanHarvestFunction)

    cantHarvestFunction = random.choice(worker_cant_harvest_functions)
    cantHarvestNode = DecisionNode(cantHarvestFunction)


    harvestFunction = random.choice(worker_harvest_functions)
    harvestNode = DecisionNode(harvestFunction)

    root = IfNode(canHarvestNode, harvestNode, cantHarvestNode, selectUnitInfoNode)
    return DecisionTree(root, 1)


def createRandomFixedSizeHarvestTree():
    '''
        height includes the Decision nodes so should have height - 1 layes of IfNodes
    '''
    selectUnitFunction = random.choice(select_worker_functions)
    selectUnitInfoNode = InformationNode(selectUnitFunction)

    workerCanHarvestFunction = random.choice(worker_can_harvest_functions)
    canHarvestNode = BooleanNode(workerCanHarvestFunction)

    cantHarvestFunction = random.choice(worker_cant_harvest_functions)
    cantHarvestNode = DecisionNode(cantHarvestFunction)

    harvestFunction = random.choice(worker_harvest_functions)
    harvestNode = DecisionNode(harvestFunction)

    root = IfNode(canHarvestNode, harvestNode, cantHarvestNode, selectUnitInfoNode)
    return FixedSizeDecisionTree(root, 1, 2)





def createRandomBuildTree():
    #TODO, look at phases and how many things we have
    firstCheckFunction = random.choice(game_number_info_functions)
    firstChildLeftNode = InformationNode(firstCheckFunction)
    if firstCheckFunction is getRoundNumber or firstCheckFunction is getKarbonite:
        firstChildRightNode = OperandNode(random.randint(0,999))
    else:
        firstChildRightNode = createRandomValOperandNode(5,2)
    firstCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = firstChildLeftNode, secondChild = firstChildRightNode, isGCFunction = False)

    # Now we recurse
    leftSubtree = recursiveRandomBuildSubtree(3, 0, 0.9)
    rightSubtree = recursiveRandomBuildSubtree(3, 0, 0.9)

    root = IfNode(firstCheckBoolNode, leftSubtree, rightSubtree)
    return DecisionTree(root, 4)



def recursiveRandomBuildSubtree(maxRecursion, currentRecursion, percentRecurse):
    #TODO, look at phases and how many things we have
    firstCheckFunction = random.choice(game_number_info_functions)
    firstChildLeftNode = InformationNode(firstCheckFunction)
    if firstCheckFunction is getRoundNumber or firstCheckFunction is getKarbonite:
        firstChildRightNode = OperandNode(random.randint(0,999))
    else:
        firstChildRightNode = createRandomValOperandNode(5,2)
    firstCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = firstChildLeftNode, secondChild = firstChildRightNode, isGCFunction = False)

    if currentRecursion == maxRecursion:
        #force Decision Node both
        if random.random() < 0.5:
            # choose worker to build
            select_builder_function = random.choice(select_worker_build_functions)
            lChildFunction = random.choice(worker_build_functions)
            lChildNode = DecisionNode(lChildFunction)
            rChildFunction = random.choice(worker_build_functions)
            rChildNode = DecisionNode(rChildFunction)
        else:
            select_builder_function = random.choice(select_factory_functions)
            lChildFunction = random.choice(factory_produce_functions)
            lChildNode = DecisionNode(lChildFunction)
            rChildFunction = random.choice(factory_produce_functions)
            rChildNode = DecisionNode(rChildFunction)

        selectBuilderNode = InformationNode(select_builder_function)

        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode, selectBuilderNode)
        return junctionNode


    if percentRecurse < random.random():
        #force Decision node left:
        if percentRecurse < random.random():
            #Also force Decision node right:

            if random.random() < 0.5:
                # choose worker to build
                select_builder_function = random.choice(select_worker_build_functions)
                lChildFunction = random.choice(worker_build_functions)
                rChildFunction = random.choice(worker_build_functions)
                lChildNode = DecisionNode(lChildFunction)
                rChildNode = DecisionNode(rChildFunction)
            else:
                select_builder_function = random.choice(select_factory_functions)
                lChildFunction = random.choice(factory_produce_functions)
                lChildNode = DecisionNode(lChildFunction)
                rChildFunction = random.choice(factory_produce_functions)
                rChildNode = DecisionNode(lChildFunction)

            selectBuilderNode = InformationNode(select_builder_function)
            junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode, selectBuilderNode)
            return junctionNode


        else:
            #only the left is Decision
            if random.random() < 0.5:
                # choose worker to build
                select_builder_function = random.choice(select_worker_build_functions)
                lChildFunction = random.choice(worker_build_functions)
                lChildNode = DecisionNode(lChildFunction)
            else:
                select_builder_function = random.choice(select_factory_functions)
                lChildFunction = random.choice(factory_produce_functions)
                lChildNode = DecisionNode(lChildFunction)

            selectBuilderNode = InformationNode(select_builder_function, lChildNode)

            rChildNode = recursiveRandomBuildSubtree(maxRecursion, currentRecursion+1, percentRecurse)

            junctionNode = IfNode(firstCheckBoolNode, selectBuilderNode, rChildNode )
            return junctionNode


    elif percentRecurse < random.random():
        #force ONLY Decision node right:
        if random.random() < 0.5:
            # choose worker to build
            select_builder_function = random.choice(select_worker_build_functions)
            rChildFunction = random.choice(worker_build_functions)
            rChildNode = DecisionNode(rChildFunction)
        else:
            select_builder_function = random.choice(select_factory_functions)
            rChildFunction = random.choice(factory_produce_functions)
            rChildNode = DecisionNode(rChildFunction)

        selectBuilderNode = InformationNode(select_builder_function, rChildNode)

        lChildNode = recursiveRandomBuildSubtree(maxRecursion, currentRecursion+1, percentRecurse)

        junctionNode = IfNode(firstCheckBoolNode, lChildNode, selectBuilderNode)
        return junctionNode

    else:
        #recurse
        lChildNode = recursiveRandomBuildSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        rChildNode = recursiveRandomBuildSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
        return junctionNode



def createRandomFixedSizeBuildTree(height):
    '''
        height includes the Decision nodes so should have height - 1 layes of IfNodes
    '''
    lowestIfs = []
    layer = height - 1
    for i in range(2**(layer)):
                
        infoFunc = random.choice(game_number_info_functions) #TODO: maybe not game info
        infoNode = InformationNode(infoFunc)
        opVal = random.choice(game_number_info_functions_number_mappings[infoFunc])
        boolNode = BooleanNode(None, operation = operator.lt, firstChild = infoNode, secondChild = opNode, isGCFunction = False) 

        select_builder_function, lChildNode, rChildNode = None
        if random.random() < 0.5:
            # choose worker to build
            select_builder_function = random.choice(select_worker_build_functions)
            lChildFunction = random.choice(worker_build_functions)
            lChildNode = DecisionNode(lChildFunction)
            rChildFunction = random.choice(worker_build_functions)
            rChildNode = DecisionNode(rChildFunction)
        else:
            select_builder_function = random.choice(select_factory_functions)
            lChildFunction = random.choice(factory_produce_functions)
            lChildNode = DecisionNode(lChildFunction)
            rChildFunction = random.choice(factory_produce_functions)
            rChildNode = DecisionNode(rChildFunction)

        selectBuilderNode = InformationNode(select_builder_function)

        ifNode = IfNode(boolNode, lChildNode, rChildNode, selectBuilderNode)
        lowestIfs.append(ifNode)
    layer -= 1
    nextLayerIfs = lowestIfs

    while (layer >= 1):
        newLayer = []
        for i in range(2**(layer-1)):
            lowerNode1 = nextLayerIfs.pop()
            lowerNode2 = nextLayerIfs.pop()
            usedFuncs = getFixedSizeTreeBoolCheckFunctionsUsed(lowerNode1)
            usedFuncs = usedFuncs | getFixedSizeTreeBoolCheckFunctionsUsed(lowerNode2)
            possibleFuncs = set(game_number_info_functions) - usedFuncs
            if len(possibleFuncs) == 0:
                infoFunc = random.choice(game_number_info_functions)
            else: 
                infoFunc = random.choice(list(possibleFuncs))
            infoNode = InformationNode(infoFunc)
            opVal = random.choice(game_number_info_functions_number_mappings[infoFunc])
            opNode = OperandNode(opVal)

            boolNode = BooleanNode(None, operation = operator.lt, firstChild = infoNode, secondChild = opNode, isGCFunction = False) 
            ifNode = IfNode(boolNode, lowerNode1, lowerNode2)
            newLayer.append(ifNode)

        layer -= 1
        nextLayerIfs = newLayer
    # done now on the top layer
    root = nextLayerIfs[0]
    return FixedSizeDecisionTree(root, 4, height)



def createRandomMoveTree():
    #TODO
    gameCheckFunction = random.choice(game_number_info_functions)
    gameCheckNode = InformationNode(gameCheckFunction)
    if gameCheckFunction is getRoundNumber or gameCheckFunction is getKarbonite:
        gameCheckValueNode = OperandNode(random.randint(0,999))
    else:
        gameCheckValueNode = createRandomValOperandNode(5,2)
    gameCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = gameCheckNode, secondChild = gameCheckValueNode, isGCFunction = False)

    # now recurse
    leftSubtree = recursiveRandomMoveSubtree(3, 0, 0.8)
    rightSubtree = recursiveRandomMoveSubtree(3, 0, 0.8)
    root = IfNode(gameCheckBoolNode, leftSubtree, rightSubtree)
    return DecisionTree(root, 3)



def recursiveRandomMoveSubtree(maxRecursion, currentRecursion, percentRecurse):
    #TODO, look at phases and how many things we have
    gameCheckFunction = random.choice(game_number_info_functions)
    gameCheckNode = InformationNode(gameCheckFunction)
    if gameCheckFunction is getRoundNumber or gameCheckFunction is getKarbonite:
        gameCheckValueNode = OperandNode(random.randint(0,999))
    else:
        gameCheckValueNode = createRandomValOperandNode(5,2)
    gameCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = gameCheckNode, secondChild = gameCheckValueNode, isGCFunction = False)

    if currentRecursion == maxRecursion:
        #force Decision Node both
        lChildNode, rChildNode, selectUnitNode = None,None,None
        if random.random() < 0.33:
            selectUnitNode = InformationNode(random.choice(select_rocket_functions))
            lChildFunction = random.choice(rocket_action_functions)
            lChildNode = DecisionNode(lChildFunction)
            rChildFunction = random.choice(rocket_action_functions)
            rChildNode = DecisionNode(rChildFunction)
        else:
            selectUnitNode = InformationNode(random.choice(select_moveable_unit_functions))
            lChildFunction = random.choice(unit_move_functions)
            lChildNode = DecisionNode(lChildFunction)
            rChildFunction = random.choice(unit_move_functions)
            rChildNode = DecisionNode(rChildFunction)

        junctionNode = IfNode(gameCheckBoolNode, lChildNode, rChildNode, selectUnitNode)
        return junctionNode

    if percentRecurse < random.random(): 
        #force Decision node left:
        select_unit_function = None
        lChildNode = None
        isRocketFunc = False
        if random.random() < 0.33:
            select_unit_function = random.choice(select_rocket_functions)
            lChildFunction = random.choice(rocket_action_functions)
            lChildNode = DecisionNode(lChildFunction)
            isRocketFunc = True
        else: 
            select_unit_function = random.choice(select_moveable_unit_functions)
            lChildFunction = random.choice(unit_move_functions)
            lChildNode = DecisionNode(lChildFunction)

        if percentRecurse < random.random(): 
            #Also force right
            if isRocketFunc:
                rChildFunction = random.choice(rocket_action_functions)
                rChildNode = DecisionNode(rChildFunction)
            else:
                rChildFunction = random.choice(unit_move_functions)
                rChildNode = DecisionNode(rChildFunction)

            selectUnitNode = InformationNode(select_unit_function)
            junctionNode = IfNode(gameCheckBoolNode, lChildNode, rChildNode, selectUnitNode)

        else:
            rChildNode = recursiveRandomMoveSubtree(maxRecursion, currentRecursion+1, percentRecurse)
            selectUnitNode = InformationNode(select_unit_function, lChildNode)

            junctionNode = IfNode(gameCheckBoolNode, selectUnitNode, rChildNode)

        return junctionNode
    

    elif percentRecurse < random.random():
        #just right side stops
        lChildNode = recursiveRandomMoveSubtree(maxRecursion, currentRecursion+1, percentRecurse)

        selectUnitNode = None
        if random.random() < 0.33:
            rChildFunction = random.choice(rocket_action_functions)
            rChildNode = DecisionNode(rChildFunction)
            select_unit_function = random.choice(select_rocket_functions)
            selectUnitNode = InformationNode(select_unit_function, rChildNode)
        else:
            rChildFunction = random.choice(unit_move_functions)
            rChildNode = DecisionNode(rChildFunction)
            select_unit_function = random.choice(select_moveable_unit_functions)
            selectUnitNode = InformationNode(select_unit_function, rChildNode)

        junctionNode = IfNode(gameCheckBoolNode, lChildNode, selectUnitNode)
        return junctionNode


    else:
        lChildNode = recursiveRandomMoveSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        rChildNode = recursiveRandomMoveSubtree(maxRecursion, currentRecursion+1, percentRecurse)

        junctionNode = IfNode(gameCheckBoolNode, lChildNode, rChildNode)
        return junctionNode



def createRandomFixedSizeMoveTree(height):
    '''
        height includes the Decision nodes so should have height - 1 layes of IfNodes
    '''
    lowestIfs = []
    layer = height - 1
    for i in range(2**(layer)):
                
        infoFunc = random.choice(game_number_info_functions)  #TODO: not game info functions, use isUnit() functions
        infoNode = InformationNode(infoFunc)
        opVal = random.choice(game_number_info_functions_number_mappings[infoFunc])
        boolNode = BooleanNode(None, operation = operator.lt, firstChild = infoNode, secondChild = opNode, isGCFunction = False) 

        lChildNode, rChildNode, selectUnitNode = None,None,None
        if random.random() < 0.33: #Sometimes make rocket movements
            selectUnitNode = InformationNode(random.choice(select_rocket_functions))
            lChildFunction = random.choice(rocket_action_functions)
            lChildNode = DecisionNode(lChildFunction)
            rChildFunction = random.choice(rocket_action_functions)
            rChildNode = DecisionNode(rChildFunction)
        else:
            selectUnitNode = InformationNode(random.choice(select_moveable_unit_functions))
            lChildFunction = random.choice(unit_move_functions)
            lChildNode = DecisionNode(lChildFunction)
            rChildFunction = random.choice(unit_move_functions)
            rChildNode = DecisionNode(rChildFunction)

        ifNode = IfNode(boolNode, lChildNode, rChildNode, selectUnitNode)
        lowestIfs.append(ifNode)
    layer -= 1
    nextLayerIfs = lowestIfs

    while (layer >= 1):
        newLayer = []
        for i in range(2**(layer-1)):
            lowerNode1 = nextLayerIfs.pop()
            lowerNode2 = nextLayerIfs.pop()
            usedFuncs = getFixedSizeTreeBoolCheckFunctionsUsed(lowerNode1)
            usedFuncs = usedFuncs | getFixedSizeTreeBoolCheckFunctionsUsed(lowerNode2)
            possibleFuncs = set(game_number_info_functions) - usedFuncs
            if len(possibleFuncs) == 0:
                infoFunc = random.choice(game_number_info_functions)
            else: 
                infoFunc = random.choice(list(possibleFuncs))
            infoNode = InformationNode(infoFunc)
            opVal = random.choice(game_number_info_functions_number_mappings[infoFunc])
            opNode = OperandNode(opVal)

            boolNode = BooleanNode(None, operation = operator.lt, firstChild = infoNode, secondChild = opNode, isGCFunction = False) 
            ifNode = IfNode(boolNode, lowerNode1, lowerNode2)
            newLayer.append(ifNode)

        layer -= 1
        nextLayerIfs = newLayer
    # done now on the top layer
    root = nextLayerIfs[0]
    return FixedSizeDecisionTree(root, 3, height)





def createRandomTopTree():
    #TODO, look at phases and how many things we have
    firstCheckFunction = random.choice(game_number_info_functions)
    firstChildLeftNode = InformationNode(firstCheckFunction)
    if firstCheckFunction is getRoundNumber or firstCheckFunction is getKarbonite:
        firstChildRightNode = OperandNode(random.randint(0,999))
    else:
        firstChildRightNode = createRandomValOperandNode(5,2)
    firstCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = firstChildLeftNode, secondChild = firstChildRightNode, isGCFunction = False)

    # Now we recurse
    leftSubtree = recursiveRandomTopSubtree(4, 0, 0.9)
    rightSubtree = recursiveRandomTopSubtree(4, 0, 0.9)

    root = IfNode(firstCheckBoolNode, leftSubtree, rightSubtree)
    return DecisionTree(root, 0)



def recursiveRandomTopSubtree(maxRecursion, currentRecursion, percentRecurse) -> Node: #TODO, remove build specifics
    #TODO, look at phases and how many things we have
    firstCheckFunction = random.choice(game_number_info_functions)
    firstChildLeftNode = InformationNode(firstCheckFunction)
    if firstCheckFunction is getRoundNumber:
        firstChildRightNode = OperandNode(random.randint(0,999))
        # TODO money caps at 400 if not gathering it
    elif firstCheckFunction is getKarbonite:
        firstChildRightNode = OperandNode(random.randint(0,400))
    else:
        firstChildRightNode = createRandomValOperandNode(5,2)
    firstCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = firstChildLeftNode, secondChild = firstChildRightNode, isGCFunction = False)

    if currentRecursion == maxRecursion:
        #force Decision Node both
        lChildNode = createRandomTopTreeDecisionNode()
        rChildNode = createRandomTopTreeDecisionNode()
        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
        return junctionNode


    if percentRecurse < random.random():
        #force Decision node left:
        if percentRecurse < random.random():
            #Also force Decision node right:
            lChildNode = createRandomTopTreeDecisionNode()
            rChildNode = createRandomTopTreeDecisionNode()
            junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
            return junctionNode

        else:
            #only the left is Decision
            lChildNode = createRandomTopTreeDecisionNode()
            rChildNode = recursiveRandomTopSubtree(maxRecursion, currentRecursion+1, percentRecurse)
            junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
            return junctionNode


    elif percentRecurse < random.random():
        #force ONLY Decision node right:
        rChildNode = createRandomTopTreeDecisionNode()
        lChildNode = recursiveRandomTopSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
        return junctionNode

    else:
        #recurse
        lChildNode = recursiveRandomTopSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        rChildNode = recursiveRandomTopSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
        return junctionNode



def createRandomFixedSizeTopTree(height):
    '''
        height includes the Decision nodes so should have height - 1 layes of IfNodes
    '''
    bottomDecisionNodes = []
    for i in range(2**(height-1)):
        node = createRandomTopTreeDecisionNode()
        bottomDecisionNodes.append(node)
    nextLayerIfs = []
    layer = height - 1
    for i in range(2**(layer-1)):
        infoFunc = random.choice(game_number_info_functions)
        infoNode = InformationNode(infoFunc)
        opVal = random.choice(game_number_info_functions_number_mappings[infoFunc])
        opNode = OperandNode(opVal)
        boolNode = BooleanNode(None, operation = operator.lt, firstChild = infoNode, secondChild = opNode, isGCFunction = False)
        d1 = bottomDecisionNodes.pop()
        d2 = bottomDecisionNodes.pop()
        ifNode = IfNode(boolNode, d1, d2)
        nextLayerIfs.append(ifNode)
    layer -= 1

    while (layer >= 1):
        newLayer = []
        for i in range(2**(layer-1)):
            lowerNode1 = nextLayerIfs.pop()
            lowerNode2 = nextLayerIfs.pop()
            usedFuncs = getFixedSizeTreeBoolCheckFunctionsUsed(lowerNode1)
            usedFuncs = usedFuncs | getFixedSizeTreeBoolCheckFunctionsUsed(lowerNode2)
            possibleFuncs = set(game_number_info_functions) - usedFuncs
            if len(possibleFuncs) == 0:
                infoFunc = random.choice(game_number_info_functions)
            else: 
                infoFunc = random.choice(list(possibleFuncs))
            infoNode = InformationNode(infoFunc)
            opVal = random.choice(game_number_info_functions_number_mappings[infoFunc])
            opNode = OperandNode(opVal)

            boolNode = BooleanNode(None, operation = operator.lt, firstChild = infoNode, secondChild = opNode, isGCFunction = False) 
            ifNode = IfNode(boolNode, lowerNode1, lowerNode2)
            newLayer.append(ifNode)

        layer -= 1
        nextLayerIfs = newLayer
    # done now on the top layer
    root = nextLayerIfs[0]
    return FixedSizeDecisionTree(root, 0, height)



def getFixedSizeTreeBoolCheckFunctionsUsed(ifNode):
    functions = set()
    queue = [ifNode]
    while (len(queue) != 0):
        currNode = queue.pop(0)
        if currNode.firstChild: #booleanNode
            if type(currNode.firstChild) is BooleanNode:
                queue.append(currNode.firstChild)
        if currNode.secondChild: #ifNode
            if type(currNode.secondChild) is IfNode:
                queue.append(currNode.secondChild)
        if currNode.thirdChild: #ifNode
            if type(currNode.thirdChild) is IfNode:
                queue.append(currNode.thirdChild)
        if type(currNode) is BooleanNode:
            #we want the first child's function
            if currNode.firstChild:
                if type(currNode.firstChild) is InformationNode:
                    functions.add(currNode.firstChild.function)
    return functions



'''End DecisionTreeUtils.py'''


class DecisionTreePlayer:

    def __init__(self, topTree, harvestTree, attackTree, movementTree, buildTree, researchTree):
        self.topTree = topTree
        self.harvestTree = harvestTree
        self.attackTree = attackTree
        self.movementTree = movementTree
        self.buildTree = buildTree
        self.researchTree = researchTree

    def compareTo(self, p2, treeTesting):
        if treeTesting == 0:
            return self.topTree.compareTo(p2.topTree)
        if treeTesting == 1:
            return self.harvestTree.compareTo(p2.harvestTree)
        if treeTesting == 2:
            return self.attackTree.compareTo(p2.attackTree)
        if treeTesting == 3:
            return self.movementTree.compareTo(p2.movementTree)
        if treeTesting == 4:
            return self.buildTree.compareTo(p2.buildTree)

    def getNumNodesByTree(self):
        n0 = self.topTree.getNumNodes()
        n1 = self.harvestTree.getNumNodes()
        n2 = self.attackTree.getNumNodes()
        n3 = self.movementTree.getNumNodes()
        n4 = self.buildTree.getNumNodes()
        return [n0, n1, n2, n3, n4]

    def execute(self, battleCode, gameController):
        # Runs one turn through the Tree(s)
        actionNum = self.topTree.execute(battleCode, gameController)
        print("Top Tree gave us an action of", actionNum)
        if actionNum == 1:
            # harvest
            #self.harvestTree.printTree()
            res = self.harvestTree.execute(battleCode, gameController)
            if res:
                print("harvestTree did not execute an action and instead returned", res)
        elif actionNum == 2:
            # attack
            #self.attackTree.printTree()
            res = self.attackTree.execute(battleCode, gameController)
            if res:
                print("attackTree did not execute an action and instead returned", res)
        elif actionNum == 3:
            # move
            #self.movementTree.printTree()
            res = self.movementTree.execute(battleCode, gameController)
            if res:
                print("movementTree did not execute an action and instead returned", res)
        elif actionNum == 4:
            # build
            #self.buildTree.printTree()
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
        harvestTreeString = self.harvestTree.getWriteString()
        attackTreeString = self.attackTree.getWriteString()
        moveTreeString = self.movementTree.getWriteString()
        buildTreeString = self.buildTree.getWriteString()

        if not os.path.exists(os.path.dirname(directoryPath + "TopTree.txt")):
            os.makedirs(os.path.dirname(directoryPath + "TopTree.txt"), exist_ok=True)
        if not os.path.exists(os.path.dirname(directoryPath + "HarvestTree.txt")):
            os.makedirs(os.path.dirname(directoryPath + "HarvestTree.txt"), exist_ok=True)
        if not os.path.exists(os.path.dirname(directoryPath + "AttackTree.txt")):
            os.makedirs(os.path.dirname(directoryPath + "AttackTree.txt"), exist_ok=True)
        if not os.path.exists(os.path.dirname(directoryPath + "MoveTree.txt")):
            os.makedirs(os.path.dirname(directoryPath + "MoveTree.txt"), exist_ok=True)
        if not os.path.exists(os.path.dirname(directoryPath + "BuildTree.txt")):
            os.makedirs(os.path.dirname(directoryPath + "BuildTree.txt"), exist_ok=True)
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
            elements = line.split()
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
                    print(elements[1])
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
                    print("** building infoNode with no function! **", functionName)
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
            topTree = FixedSizeDecisionTree(root, 0)
            print("read topTree")

        with open(directoryPath + "/" + fileNames[1], 'r') as f:
            lines = f.readlines()
            root, x = recursiveBuildTree(lines, 0, 0)
            harvestTree = FixedSizeDecisionTree(root, 1)
            print("read harvestTree")

        with open(directoryPath + "/" + fileNames[2], 'r') as f:
            lines = f.readlines()
            root, x = recursiveBuildTree(lines, 0, 0)
            attackTree = FixedSizeDecisionTree(root, 2)
            print("read attackTree")

        with open(directoryPath + "/" + fileNames[3], 'r') as f:
            lines = f.readlines()
            root, x = recursiveBuildTree(lines, 0, 0)
            moveTree = FixedSizeDecisionTree(root, 3)
            print("read movementTree")

        with open(directoryPath + "/" + fileNames[4], 'r') as f:
            lines = f.readlines()
            root, x = recursiveBuildTree(lines, 0, 0)
            buildTree = FixedSizeDecisionTree(root, 4)
            print("read buildTree")

        player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
        return player
        




def createRandomFixedSizeDecisionTreePlayer(topHeight, attackHeight):
    topTree = createRandomFixedSizeTopTree(topHeight)
    harvestTree = createRandomFixedSizeHarvestTree()
    attackTree = createRandomFixedSizeAttackTree(attackHeight)
    moveTree = createRandomMoveTree()
    buildTree = createRandomBuildTree()

    player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
    return player


def createCurriculumTrainingPlayerTop(topHeight) -> DecisionTreePlayer:
    topTree = createRandomFixedSizeTopTree(topHeight)
    harvestTree = createIdealHarvestTree()
    attackTree = createIdealAttackTree()
    moveTree = createIdealMoveTree()
    buildTree = createIdealBuildTree()

    player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
    return player

def createCurriculumTrainingPlayerHarvest(harvestHeight) -> DecisionTreePlayer:
    topTree = createIdealTopTree()
    harvestTree = createRandomFixedSizeHarvestTree() #TODO add harvest height
    attackTree = createIdealAttackTree()
    moveTree = createIdealMoveTree()
    buildTree = createIdealBuildTree()

    player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
    return player


def createCurriculumTrainingPlayerAttack(attackHeight) -> DecisionTreePlayer:
    ''' Gives us the 'ideal' player we are testing all our GP operations against besides Attack
    '''
    topTree = createIdealTopTree()
    harvestTree = createIdealHarvestTree()
    attackTree = createRandomFixedSizeAttackTree(attackHeight)
    moveTree = createIdealMoveTree()
    buildTree = createIdealBuildTree()

    player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
    return player


def createCurriculumTrainingPlayerMove(moveHeight) -> DecisionTreePlayer:
    ''' Gives us the 'ideal' player we are testing all our GP operations against besides Move
    '''
    topTree = createIdealTopTree()
    harvestTree = createIdealHarvestTree()
    attackTree = createIdealAttackTree()
    moveTree = createRandomFixedSizeMoveTree(moveHeight)
    buildTree = createIdealBuildTree()

    player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
    return player


def createCurriculumTrainingPlayerBuild(buildHeight) -> DecisionTreePlayer:
    ''' Gives us the 'ideal' player we are testing all our GP operations against besides Build
    '''
    topTree = createIdealTopTree()
    harvestTree = createIdealHarvestTree()
    attackTree = createIdealAttackTree()
    moveTree = createIdealMoveTree()
    buildTree = createRandomFixedSizeBuildTree(buildHeight)

    player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
    return player



def createRandomDecisionTreePlayer():
    ''' Antiquated '''
    topTree = createRandomTopTree()
    harvestTree = createRandomHarvestTree()
    attackTree = createRandomAttackTree()
    moveTree = createRandomMoveTree()
    buildTree = createRandomBuildTree()

    player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
    return player


def Crossover1Player(p1, p2, probOfEachTree, probInSearch) -> (DecisionTreePlayer, DecisionTreePlayer, int, list):
    '''
    p1 and p2 are players, probOfEachTree is the probability of doing crossover,
    probInSearch is the probability that helps crossover decide where to crossover.
    '''
    p1topTree, p2topTree, x1, h1 = Crossover1(p1.topTree, p2.topTree, probOfEachTree, probInSearch)
    p1harvestTree, p2harvestTree, x2, h2 = Crossover1(p1.harvestTree, p2.harvestTree, probOfEachTree, probInSearch)
    p1attackTree, p2attackTree, x3, h3 = Crossover1(p1.attackTree, p2.attackTree, probOfEachTree, probInSearch)
    p1movementTree, p2movementTree, x4, h4 = Crossover1(p1.movementTree, p2.movementTree, probOfEachTree, probInSearch)
    p1buildTree, p2buildTree, x5, h5 = Crossover1(p1.buildTree, p2.buildTree, probOfEachTree, probInSearch)
    numCrossover = x1 + x2 + x3 + x4 + x5
    heights = [h1, h2, h3, h4, h5]
    # No research tree rn
    newp1 = DecisionTreePlayer(p1topTree, p1harvestTree, p1attackTree, p1movementTree, p1buildTree, None)
    newp2 = DecisionTreePlayer(p2topTree, p2harvestTree, p2attackTree, p2movementTree, p2buildTree, None)

    return newp1, newp2, numCrossover, heights




def MutatePlayer(player, probabilityPerNode, probOfMutate, allFunctionSets) -> (DecisionTreePlayer, int):
    topTree, m0 = Mutate(player.topTree, probabilityPerNode, probOfMutate, allFunctionSets)
    harvestTree, m1 = Mutate(player.harvestTree, probabilityPerNode, probOfMutate, allFunctionSets)
    attackTree, m2 = Mutate(player.attackTree, probabilityPerNode, probOfMutate, allFunctionSets)
    movementTree, m3 =Mutate(player.movementTree, probabilityPerNode, probOfMutate, allFunctionSets)
    buildTree, m4 = Mutate(player.buildTree, probabilityPerNode, probOfMutate, allFunctionSets)
    numMutations = m0 + m1 + m2 + m3 + m4
    return (DecisionTreePlayer(topTree, harvestTree, attackTree, movementTree, buildTree, None), numMutations)


''' GP operators '''
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


def Mutate(decisionTree, probabilityPerNode, probOfMutate, allFunctionSets, decisionToSubtreeProb = 0) -> (DecisionTree, int):
    ''' NEW IMPLEMENTATION
        mutates the trees just a bit by changing functions to like functions in Information and Decision Nodes
        Also can change the value of a operand node. ALl these changes done with some given probability.
    '''
    if random.random() > probOfMutate:
        # don't mutate this tree
        return (decisionTree, 0)


    nodeQueue = []
    nodeQueue.append(decisionTree.root)
    numMutations = 0

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

                #possibly add subtree
                if random.random() < decisionToSubtreeProb:
                    if decisionTree.id == 0:
                        # Top tree
                        subtree = recursiveRandomTopSubtree(2, 0, 0.9)
                        currNode.swap(subtree)

                    # Harvest Tree, do nothing
                    # TODO: can't swap if and decision nodes

                    elif decisionTree.id == 2:
                        # Attack Tree
                        subtree = recursiveRandomAttackSubtree(2,0,0.8)
                        currNode.swap(subtree)
                    elif decisionTree.id == 3:
                        # Move Tree
                        subtree = recursiveRandomMoveSubtree(2, 0, 0.8)
                        currNode.swap(subtree)
                    elif decisionTree.id == 4:
                        # Build Tree
                        subtree = recursiveRandomBuildSubtree(2, 0, 0.9)
                        currNode.swap(subtree)

                else:
                    function = currNode.action
                    for functionSet in allFunctionSets:
                        if function in functionSet:
                            newFunction = random.choice(functionSet)
                            #print("Changing Decision Node function from " + currNode.action.__name__ + " to " + newFunction.__name__)
                            currNode.action = newFunction
                            numMutations += 1
                            break

        if type(currNode) is InformationNode:
            if random.random() < probabilityPerNode:
                function = currNode.function
                for functionSet in allFunctionSets:
                    if function in functionSet:
                        newFunction = random.choice(functionSet)
                        #print("Changing Information Node function from " + currNode.function.__name__ + " to " + newFunction.__name__)
                        currNode.function = newFunction
                        numMutations += 1
                        break

        #if operandNode
        if type(currNode) is OperandNode:
            if random.random() < probabilityPerNode:
                newVal = newValInNormalizedRange(currNode.value, min(len(nodeQueue), 3)) #this is sorta random I guess
                #print("Changing Operand Node value from " + str(currNode.value) + " to " + str(newVal))
                currNode.value = newVal
                numMutations += 1

    return (decisionTree, numMutations)





def Crossover1(treeA, treeB, probOfDoing, probInSearching) -> (DecisionTree, DecisionTree, int, int):
    ''' returns two trees that are crossed over. then the number of crossover and the height of the crossover
        we can only do crossover on same type nodes
    '''
    if random.random() > probOfDoing:
        return (treeA, treeB, 0, -1)

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
            return (treeA, treeB, 0 , -1)


    #now we search treeB for a node of the same type, weighting toward lower in the tree
    currNodeB = treeB.root
    heightB = 1
    nodes = recursiveDFSNodes(currNodeB, heightB);
    trimmedNodes = [node for node in nodes if type(node) is type(currNodeA)]
    if len(trimmedNodes) != 0:
        nodeB = random.choice(trimmedNodes)
        currNodeA.swap(nodeB) #TODO: check these are working
        return (treeA, treeB, 1, heightA)
    else:
        return (treeA, treeB, 0, -1)
        




def recursiveDFSNodesDepthPair(currNode, depth) -> list:
    '''returns a list of nodes under and including currNode'''
    nodes = []
    if currNode.firstChild:
        nodes += recursiveDFSNodesDepthPair(currNode.firstChild, depth+1)
    if currNode.secondChild:
        nodes += recursiveDFSNodesDepthPair(currNode.secondChild, depth+1)
    if currNode.thirdChild:
        nodes += recursiveDFSNodesDepthPair(currNode.thirdChild, depth+1)
    #TODO: ignoring possible info node for if nodes
    nodes += [(currNode, depth)]
    return nodes



def Crossover2(treeA, treeB, probOfDoing, probInSearching) -> (DecisionTree, DecisionTree, int, int):
    ''' returns two trees that are crossed over. then the number of crossover and the height of the crossover
        we can only do crossover on same type nodes. This version uses a desired crossover height to bias toward averaging 
        the tree heights after crossover
    '''
    if random.random() > probOfDoing:
        return (treeA, treeB, 0, -1)

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
            return (treeA, treeB, 0 , -1)


    #now we search treeB for a node of the same type, weighting toward lower in the tree
    currNodeB = treeB.root
    heightB = 1
    nodes = recursiveDFSNodesDepthPair(currNodeB, heightB);
    nodeDepthPairs = [nodePair for nodePair in nodes if type(nodePair[0]) is type(currNodeA)]
    if len(nodeDepthPairs) != 0:
        
        nodeB = crossover2NodeSelection(nodeDepthPairs, heightA)

        currNodeA.swap(nodeB) #TODO: check these are working
        return (treeA, treeB, 1, heightA)
    else:
        return (treeA, treeB, 0, -1)


def crossover2NodeSelection(nodeDepthPairs, heightA):
    depthDifference = [] #hold the difference from desiredCHeight
    for pair in nodeDepthPairs:
        depthDifference.append(abs(heightA-pair[1]))
    # now we want the sum and make buckets of probabilities based on those differences
    depthDifference = [x+1 for x in depthDifference] #zeroes are bad for ranks
    totalDifs = sum(depthDifference)
    rankedProbs = [totalDifs - x for x in depthDifference]
    divideRankProbBy = sum(rankedProbs)
    buckets = [] #holds the endpoint of the bucket
    nextBucket = 0
    for prob in rankedProbs:
        nextBucket += (prob / divideRankProbBy)
        buckets.append(nextBucket)

    print("Buckets: ", buckets)
    target = random.random()
    index = len(nodeDepthPairs);
    for i in range(len(nodeDepthPairs)):
        if target < buckets[i]:
            #we have passed the bucket
            index = i-1
            break;
    if index == len(nodeDepthPairs):
        #it didn't work, pick randomly
        print("crossover2NodeSelection did not get a target {0} into a bucket".format(target))
        return random.choice(nodeDepthPairs)[0]
    else:
        return nodeDepthPairs[index][0]



def Crossover2Player(p1, p2, probOfEachTree, probInSearch) -> (DecisionTreePlayer, DecisionTreePlayer, int, list):
    '''
    p1 and p2 are players, probOfEachTree is the probability of doing crossover,
    probInSearch is the probability that helps crossover decide where to crossover.
    '''
    p1topTree, p2topTree, x1, h1 = Crossover2(p1.topTree, p2.topTree, probOfEachTree, probInSearch)
    p1harvestTree, p2harvestTree, x2, h2 = Crossover2(p1.harvestTree, p2.harvestTree, probOfEachTree, probInSearch)
    p1attackTree, p2attackTree, x3, h3 = Crossover2(p1.attackTree, p2.attackTree, probOfEachTree, probInSearch)
    p1movementTree, p2movementTree, x4, h4 = Crossover2(p1.movementTree, p2.movementTree, probOfEachTree, probInSearch)
    p1buildTree, p2buildTree, x5, h5 = Crossover2(p1.buildTree, p2.buildTree, probOfEachTree, probInSearch)
    numCrossover = x1 + x2 + x3 + x4 + x5
    heights = [h1, h2, h3, h4, h5]
    # No research tree rn
    newp1 = DecisionTreePlayer(p1topTree, p1harvestTree, p1attackTree, p1movementTree, p1buildTree, None)
    newp2 = DecisionTreePlayer(p2topTree, p2harvestTree, p2attackTree, p2movementTree, p2buildTree, None)

    return newp1, newp2, numCrossover, heights



def FixedSizeTreeCrossover(fst1, fst2, probOfDoing, probInSearch) -> (FixedSizeDecisionTree, FixedSizeDecisionTree, int, int):
    ''' 
        Crossover of fixed trees. We only want to do it at if, bool, or decision nodes
    '''
    if random.random() > probOfDoing:
        return (fst1, fst2, 0, -1)

    #fst1.setNodeIdNumbers()
    #fst2.setNodeIdNumbers()

    currNodeA = fst1.root
    currNodeB = fst2.root
    heightA = 1 #the number of if nodes
    # We prefer smaller mutations, so we are going to mutate as a function of depth
    while(type(currNodeA) is IfNode):
        
        if type(currNodeB) is IfNode:
            #3 children
            randVal = random.random()
            if randVal < probInSearch*heightA:
                break;

            randVal = random.random()
            heightA += 1
            if randVal < 0.33:
                currNodeA = currNodeA.firstChild
                currNodeB = currNodeB.firstChild
            elif randVal < 0.67:
                currNodeA = currNodeA.secondChild
                currNodeB = currNodeB.secondChild
            else:
                currNodeA = currNodeA.thirdChild
                currNodeB = currNodeB.thirdChild
            #ignore optional info node until we have the dictionary

        else:
            print("currNodeA and currNodeB are not both ifNodes")
            break;

    currNodeA.swap(currNodeB)
    return (fst1, fst2, 1, heightA)


def FixedSizeTopTreeMutateOnce(tree, probOfMutate, game_number_info_functions_number_mappings):
    ''' NEW IMPLEMENTATION
        Mutates the fixed size top tree to adjust the numbers/functions of boolean nodes or the Decision Node output.
        We only do mutate at Boolean Nodes or Decision Nodes, but Boolean node mutations are actually the infoNode functions
        and the Operand Node values of the Boolean Node children
        Unlike the other Mutates, this only mutates once in the tree
    '''
    if random.random() > probOfMutate:
        # don't mutate this tree
        return (tree, 0)

    nodeQueue = [tree.root]
    potentialNodes = []

    while(len(nodeQueue) != 0):
        #add children to Queue
        currNode = nodeQueue.pop(0)

        if type(currNode) is IfNode:
            if currNode.firstChild:
                nodeQueue.append(currNode.firstChild)
            if currNode.secondChild:
                nodeQueue.append(currNode.secondChild)
            if currNode.thirdChild:
                nodeQueue.append(currNode.thirdChild)
            
            if currNode.infoChild:
                nodeQueue.append(currNode.infoChild)
            
        #if decision node, possibly mutate
        elif type(currNode) is DecisionNode:
            potentialNodes.append(currNode)

        #if boolean node, may want to mutate
        elif type(currNode) is BooleanNode:
           potentialNodes.append(currNode)

    nodeToMutate = random.choice(potentialNodes)

    if type(nodeToMutate) is DecisionNode:
        newNode = createRandomTopTreeDecisionNode()
        nodeToMutate.swap(newNode)
    elif type(nodeToMutate) is BooleanNode:
        if nodeToMutate.firstChild and type(nodeToMutate.firstChild) is InformationNode:
            if nodeToMutate.secondChild and type(nodeToMutate.secondChild) is OperandNode:
                newFunc = random.choice(list(game_number_info_functions_number_mappings.keys()))
                newVal = random.choice(game_number_info_functions_number_mappings[newFunc])
                nodeToMutate.firstChild.function = newFunc
                nodeToMutate.secondChild.value = newVal
            else:
                print("In FixedSizeDecisionTree top tree, boolean node's second child is not OperandNode") 
                return (tree, 0)
        else:
            print("In FixedSizeDecisionTree top tree, boolean node's first child is not InfoNode") 
            return (tree, 0)

    return (tree, 1)


def FixedSizeLowerTreeMutateOnce(tree, probOfMutate, allFunctionSets, game_number_info_functions_number_mappings):
    ''' NEW IMPLEMENTATION
        Mutates the fixed size top tree to adjust the numbers/functions of boolean nodes or the Decision Node output.
        We only do mutate at Boolean Nodes or Decision Nodes, but Boolean node mutations are actually the infoNode functions
        and the Operand Node values of the Boolean Node children
        Unlike the other Mutates, this only mutates once in the tree
    '''
    if random.random() > probOfMutate:
        # don't mutate this tree
        return (tree, 0)

    nodeQueue = [tree.root]
    potentialNodes = []

    while(len(nodeQueue) != 0):
        #add children to Queue
        currNode = nodeQueue.pop(0)

        if type(currNode) is IfNode:
            if currNode.firstChild:
                nodeQueue.append(currNode.firstChild)
            if currNode.secondChild:
                nodeQueue.append(currNode.secondChild)
            if currNode.thirdChild:
                nodeQueue.append(currNode.thirdChild)
            
            if currNode.infoChild:
                nodeQueue.append(currNode.infoChild)
            
        #if decision node, possibly mutate
        elif type(currNode) is DecisionNode:
            potentialNodes.append(currNode)

        #if boolean node, may want to mutate
        elif type(currNode) is BooleanNode:
           potentialNodes.append(currNode)

    nodeToMutate = random.choice(potentialNodes)

    if type(nodeToMutate) is DecisionNode:
        function = nodeToMutate.action
        for functionSet in allFunctionSets:
            if function in functionSet:
                newFunction = random.choice(functionSet)
                newNode = DecisionNode(newFunction)
                nodeToMutate.swap(newNode)
                break

    elif type(nodeToMutate) is BooleanNode:
        if nodeToMutate.firstChild and type(nodeToMutate.firstChild) is InformationNode:
            if nodeToMutate.secondChild and type(nodeToMutate.secondChild) is OperandNode:
                newFunc = random.choice(list(game_number_info_functions_number_mappings.keys()))
                newVal = random.choice(game_number_info_functions_number_mappings[newFunc])
                nodeToMutate.firstChild.function = newFunc
                nodeToMutate.secondChild.value = newVal
            else:
                print("In FixedSizeDecisionTree top tree, boolean node's second child is not OperandNode") 
                return (tree, 0)
        else:
            print("In FixedSizeDecisionTree top tree, boolean node's first child is not InfoNode") 
            return (tree, 0)

    return (tree, 1)



def Crossover3PlayerFixed(p1, p2, probOfEachTree, probInSearch, treeTesting) -> (DecisionTreePlayer, DecisionTreePlayer, int, list):
    '''
    p1 and p2 are players, probOfEachTree is the probability of doing crossover,
    probInSearch is the probability that helps crossover decide where to crossover.
    '''
    p1topTree, p1harvestTree, p1attackTree, p1movementTree, p1buildTree = p1.topTree, p1.harvestTree, p1.attackTree, p1.movementTree, p1.buildTree
    p2topTree, p2harvestTree, p2attackTree, p2movementTree, p2buildTree = p2.topTree, p2.harvestTree, p2.attackTree, p2.movementTree, p2.buildTree
    x1, x2, x3, x4, x5 = 0,0,0,0,0
    h1,h2,h3,h4,h5 = 0,0,0,0,0
    if treeTesting == 0:
        p1topTree, p2topTree, x1, h1 = FixedSizeTreeCrossover(p1.topTree, p2.topTree, probOfEachTree, probInSearch)
    elif treeTesting == 1:    
        p1harvestTree, p2harvestTree, x2, h2 = FixedSizeTreeCrossover(p1.harvestTree, p2.harvestTree, probOfEachTree, probInSearch)
    elif treeTesting == 2:
        p1attackTree, p2attackTree, x3, h3 = FixedSizeTreeCrossover(p1.attackTree, p2.attackTree, probOfEachTree, probInSearch)
    elif treeTesting == 3:
        p1movementTree, p2movementTree, x4, h4 = FixedSizeTreeCrossover(p1.movementTree, p2.movementTree, probOfEachTree, probInSearch)
    elif treeTesting == 4:  
        p1buildTree, p2buildTree, x5, h5 = FixedSizeTreeCrossover(p1.buildTree, p2.buildTree, probOfEachTree, probInSearch)

    numCrossover = x1 + x2 + x3 + x4 + x5
    heights = [h1, h2, h3, h4, h5]
    # No research tree rn
    newp1 = DecisionTreePlayer(p1topTree, p1harvestTree, p1attackTree, p1movementTree, p1buildTree, None)
    newp2 = DecisionTreePlayer(p2topTree, p2harvestTree, p2attackTree, p2movementTree, p2buildTree, None)

    return newp1, newp2, numCrossover, heights


def MutatePlayerFixed(player, probOfMutate, allFunctionSets, game_number_info_functions_number_mappings, treeTraining) -> (DecisionTreePlayer, int):
    topTree, harvestTree, attackTree, movementTree, buildTree = player.topTree, player.harvestTree, player.attackTree, player.movementTree, player.buildTree
    m0, m1, m2, m3, m4 = 0,0,0,0,0

    if treeTraining == 0:
        topTree, m0 = FixedSizeTopTreeMutateOnce(player.topTree, probOfMutate, game_number_info_functions_number_mappings)
    elif treeTraining == 1:
        harvestTree, m1 = FixedSizeLowerTreeMutateOnce(player.harvestTree, probOfMutate, allFunctionSets, game_number_info_functions_number_mappings)
    elif treeTraining == 2:
        attackTree, m2 = FixedSizeLowerTreeMutateOnce(player.attackTree, probOfMutate, allFunctionSets, game_number_info_functions_number_mappings)
    elif treeTraining == 3:
        movementTree, m3 = FixedSizeLowerTreeMutateOnce(player.movementTree, probOfMutate, allFunctionSets, game_number_info_functions_number_mappings)
    elif treeTraining == 4:
        buildTree, m4 = FixedSizeLowerTreeMutateOnce(player.buildTree, probOfMutate, allFunctionSets, game_number_info_functions_number_mappings)
    numMutations = m0 + m1 + m2 + m3 + m4
    return (DecisionTreePlayer(topTree, harvestTree, attackTree, movementTree, buildTree, None), numMutations)


def createIdealPlayer() -> DecisionTreePlayer:
    ''' Gives us the 'ideal' player we are testing all our GP operations against
    '''
    topTree = createIdealTopTree()
    harvestTree = createIdealHarvestTree()
    attackTree = createIdealAttackTree()
    moveTree = createIdealMoveTree()
    buildTree = createIdealBuildTree()

    player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, None)
    return player


def createIdealPlayerForTesting(treeTraining, treeHeight) -> DecisionTreePlayer:
    ''' Gives us the 'ideal' player we are testing all our GP operations against
    '''
    player = createIdealPlayer() # not correct dimensions of Harvest tree rn, or even topTree
    if treeTraining == 0:
        player = createCurriculumTrainingPlayerTop(treeHeight)
    elif treeTraining == 1:
        player = createCurriculumTrainingPlayerHarvest(treeHeight)
    elif treeTraining == 2:
        player = createCurriculumTrainingPlayerAttack(treeHeight)
    elif treeTraining == 3:
        player = createCurriculumTrainingPlayerMove(treeHeight)
    elif treeTraining == 4:
        player = createCurriculumTrainingPlayerBuild(treeHeight)
    
    return player