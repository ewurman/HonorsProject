import DecisionTreeUtils
from enum import IntEnum


class Node:

    def __init__(self, firstChild = None, secondChild = None, thirdChild = None):
        self.firstChild = firstChild
        self.secondChild = secondChild
        self.thirdChild = thirdChild


class IfNode(Node):
    #first child is the booleanNode, then the true subtree as secondChild then an else subtree as thirdChild.

    def __init__(self, firstChild, secondChild, thirdChild):
        super().__init__(firstChild, secondChild, thirdChild)

    def follow(boardController, params = []) -> Node:
        allparams = params
        nextNode = firstChild
        while type(nextNode) is InformationNode:
            allparams.append(firstChild.evaluate())
            nextNode = nextNode.follow()

        if nextNode.evaluate(boardController, *allparams):
            return secondChild
        else:
            return thirdChild


class BooleanNode(Node):

    def __init__(self, function, params = [], operation = None, firstChild = None, secondChild = None, isGCFunction = True):
        super().__init__(firstChild, secondChild)
        self.function = function;
        self.isFunction = function != None
        self.params = params
        self.operation = operation


    def evaluate(boardController, moreParams = []) -> bool:
        if isFunction:
            try:
                totalParams = params + moreParams
                gc = boardController.GameController() #TODO, we probably want eveything passing the bc and things that need to can grab the gc
                if (isGCFunction):
                    return gc.function(*totalParams) #no params?
                else: 
                    return function(boardController, *totalParams)
            except:
                return function()
        else:
            # we have operators and boolean expressions
            # TODO: How to represent boolean expressions

            ''' The operator, is this node, and the kids are the numbers/operands '''
            if firstChild is OperandNode:
                leftOperand = firstChild.evaluate();
            elif firstChild is InformationNode:
                leftOperand = firstChild.evaluate(boardController);
            if secondChild is OperandNode:
                rightOperand = secondChild.evaluate();
            elif secondChild is InformationNode:
                rightOperand = secondChild.evaluate(boardController);

            return operation(leftOperand, rightOperand)


class OperandNode(Node):
    def __init__(self, value):
        super.__init__()
        self.value = value

    def evaluate(self):
        return self.value


class InformationNode(Node):
    def __init__(self, function, firstChild = None):
        super.__init__(firstChild)
        self.function = function

    def evaluate(self, boardController, params = None):
        if params:
            return self.function(boardController, *params)
        else:
            return self.function(boardController)

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

    def execute(boardController, params):

        # can have the helper functions to get our parameters

        if typeOfActionToMake != 0:
            return typeOfActionToMake;

        try:
            #gameController.action(unit)
            gc = boardController.GameController()
            gc.action(*params) 
            #https://stackoverflow.com/questions/817087/call-a-function-with-argument-list-in-python
            
        except:
            action(*params)

        return None










