import DecisionTreeUtils
from enum import IntEnum
import operator

class Node:

    def __init__(self, firstChild = None, secondChild = None, thirdChild = None):
        self.firstChild = firstChild
        self.secondChild = secondChild
        self.thirdChild = thirdChild

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

    def printNode(self, indent):
        if self.firstChild:
            self.firstChild.printNode(indent + "\t")
        if self.secondChild:
            self.secondChild.printNode(indent + "\t")
        if self.thirdChild:
            self.thirdChild.printNode(indent + "\t")



class IfNode(Node):
    #first child is the booleanNode, then the true subtree as secondChild then an else subtree as thirdChild.

    def __init__(self, firstChild, secondChild, thirdChild, infoChild = None):
        super().__init__(firstChild, secondChild, thirdChild)
        self.infoChild = infoChild 


    def swap(self, node):
        super().swap(node)
        temp1 = self.infoChild
        self.infoChild = node.infoChild
        node.infoChild = temp1

    def printNode(self, indent):
        print(indent + "At If Node")
        super().printNode(indent)
        if self.infoChild:
            self.infoChild.printNode(indent + '\t')


    def follow(self, boardController, gc, permparams = [], ifparams = []) -> (Node, list):
        allparams = permparams
        newparams = []
        if self.infoChild:
            print("This if node has an infoChild: collecting parameters")
            try:
                newparams = self.infoChild.evaluate(boardController, gc, permparams)
            except:
                newparams = self.infoChild.evaluate(boardController, gc, permparams)
            ifparams.append(newparams)

        nextNode = self.firstChild
        boolParams = []
        while type(nextNode) is InformationNode:
            boolParams.append(nextNode.evaluate(boardController, gc))
            nextNode = nextNode.follow()

        allparams += ifparams
        if nextNode.evaluate(boardController, gc, allparams + boolParams):
            return (self.secondChild , ifparams)
        else:
            return (self.thirdChild, ifparams)


class BooleanNode(Node):

    def __init__(self, function, params = [], operation = None, firstChild = None, secondChild = None, isGCFunction = True):
        super().__init__(firstChild, secondChild)
        self.function = function;
        self.isFunction = function != None
        self.params = params
        self.operation = operation

    def swap(self, node):
        super().swap(node)
        temp1 = self.function
        temp2 = self.params
        temp3 = self.operation
        temp4 = isGCFunction
        self.function = node.function
        node.function = temp1
        self.params = node.params
        node.params = temp2
        self.operation = node.operation
        node.operation = temp3
        self.isGCFunction = node.isGCFunction
        node.isGCFunction = temp4


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



    def evaluate(self, battleCode, gc, moreParams = []) -> bool:
        if moreParams != []:
            print("Evaluating BooleanNode with params: ", moreParams)
        if self.isFunction:
        
            totalParams = self.params + moreParams
            
            #if (self.isGCFunction):
            #    return gc.function(*totalParams) #no params?
            #else: 
            #    return self.function(boardController, gc, *totalParams)
            try:
                res = self.function(battleCode, gc, *totalParams)
            except:
                res = self.function(gc, *totalParams)
            return res
        else:
            # we have operators and boolean expressions
            # TODO: How to represent boolean expressions

            ''' The operator, is this node, and the kids are the numbers/operands '''
            if self.firstChild is OperandNode:
                leftOperand = self.firstChild.evaluate();
            elif self.firstChild is InformationNode:
                leftOperand = self.firstChild.evaluate(battleCode, gc);
            if self.secondChild is OperandNode:
                rightOperand = self.secondChild.evaluate();
            elif self.secondChild is InformationNode:
                rightOperand = self.secondChild.evaluate(battleCode, gc);

            return self.operation(leftOperand, rightOperand)


class OperandNode(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def swap(self, node):
        super().swap(node)
        temp1 = self.value
        self.value = node.value
        node.value = temp1

    def printNode(self, indent):
        print(indent + "At Operand Node with value: "+ str(self.value))
        super().printNode(indent)

    def evaluate(self):
        return self.value



class InformationNode(Node):
    def __init__(self, function, firstChild = None):
        super().__init__(firstChild)
        self.function = function

    def swap(self, node):
        super().swap(node)
        temp1 = self.function
        self.function = node.function
        node.function = temp1

    def printNode(self, indent):
        print(indent + "At Info Node with function: " + self.function.__name__ )
        super().printNode(indent)

    def evaluate(self, battleCode, gameController, params = []):
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
    Research = 5




class DecisionNode(Node):

    def __init__(self, action, typeOfActionToMake = 0):
        super().__init__()
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

    def printNode(self, indent):
        print(indent + "At Decision Node with action: "+ self.action.__name__)
        if self.typeOfActionToMake != 0:
            print(indent + "type of action is " + self.typeOfActionToMake)
        super().printNode(indent)


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










