import random
import Enum
import Node

# Helper Functions for creating a tree
def createRandomTopTreeDecisionNode():
    actionType = random.choice(list(ActionType))
    node = DecisionNode(None, actionType)
    return node


def createRandomBottomTreeDecisionNode():
    # need a dictionary of possible functions and their parameter sets
    x = "placeholder"


def createRandomValOperandNode():
    intval = random.choice(random.lognormvariate(5,2))
    node = OperandNode(intval)
    return node


#def createRandomBoardInfoOperandNode(boardController):








# Helper Functions for the game

def selectRandomWorker(boardController):
    gc = boardController.GameController()
    workers = [x for x in gc.my_units() if x.unit_type == boardController.UnitType.Worker]
    return random.choice(workers)

def selectRandomKnight(boardController):
    gc = boardController.GameController()
    knights = [x for x in gc.my_units() if x.unit_type == boardController.UnitType.Knight]
    return random.choice(knights)

def selectRandomRanger(boardController):
    gc = boardController.GameController()
    rangers = [x for x in gc.my_units() if x.unit_type == boardController.UnitType.Ranger]
    return random.choice(rangers)

def selectRandomMage(boardController):
    gc = boardController.GameController()
    mages = [x for x in gc.my_units() if x.unit_type == boardController.UnitType.Mage]
    return random.choice(mages)

def selectRandomHealer(boardController):
    gc = boardController.GameController()
    healers = [x for x in gc.my_units() if x.unit_type == boardController.UnitType.Healers]
    return random.choice(healers)


def workerMoveBehavior1(boardController, worker):
    gc = boardController.GameController()



