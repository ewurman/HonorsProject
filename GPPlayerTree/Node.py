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

    def getWriteString(self, indent):
        s = ""
        if self.firstChild:
            s += self.firstChild.getWriteString(indent + "\t")
        if self.secondChild:
            s += self.secondChild.getWriteString(indent + "\t")
        if self.thirdChild:
            s += self.thirdChild.getWriteString(indent + "\t")
        return s



class IfNode(Node):
    #first child is the booleanNode, then the true subtree as secondChild then an else subtree as thirdChild.

    def __init__(self, firstChild, secondChild, thirdChild, infoChild = None):
        super().__init__(firstChild, secondChild, thirdChild)
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
        allparams = permparams
        newparams = []
        if self.infoChild:
            print("This if node has an infoChild: collecting parameters")
            try:
                newparams = self.infoChild.evaluate(boardController, gc, permparams)
            except:
                newparams = self.infoChild.evaluate(boardController, gc, permparams)
            ifparams.append(newparams) #if newparams is not None else None)
            

        nextNode = self.firstChild
        boolParams = []
        while type(nextNode) is InformationNode:
            res = nextNode.evaluate(boardController, gc)
            boolParams.append(res) #if res is not None else None) 
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
        temp4 = self.isGCFunction
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
            leftOperand = 0
            rightOperand = 0
            if self.firstChild is OperandNode:
                leftOperand = self.firstChild.evaluate();
            elif self.firstChild is InformationNode:
                leftOperand = self.firstChild.evaluate(battleCode, gc);
            elif self.firstChild is BooleanNode:
                leftOperand = self.firstChild.evaluate(battleCode, gc, moreParams)
            else:
                print("leftOperand defaulted to 0")
            if self.secondChild is OperandNode:
                rightOperand = self.secondChild.evaluate();
            elif self.secondChild is InformationNode:
                rightOperand = self.secondChild.evaluate(battleCode, gc);
            elif self.firstChild is BooleanNode:
                rightOperand = self.secondChild.evaluate(battleCode, gc, moreParams)
            else:
                print("rightOperand defaulted to 0")

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

    def getWriteString(self, indent) -> str:
        s = indent + "OperandNode Value: " + str(self.value) + "\n"
        s += super().getWriteString(indent)
        return s

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

    def getWriteString(self, indent) -> str:
        s = indent + "InformationNode function: " + self.function.__name__ + "\n"
        s += super().getWriteString(indent)
        return s

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
        if self.action:
            print(indent + "At Decision Node with action: "+ self.action.__name__)
        if self.typeOfActionToMake != 0:
            print(indent + "At Decision Node with type of action is " + self.typeOfActionToMake)
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










