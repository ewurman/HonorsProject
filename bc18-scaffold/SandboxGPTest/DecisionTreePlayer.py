import DecisionTree
import DecisionTreeUtils

class DecisionTreePlayer:

    def __init__(self, topTree, harvestTree, attackTree, movementTree, buildTree, researchTree):
        self.topTree = topTree
        self.harvestTree = harvestTree
        self.attackTree = attackTree
        self.movementTree = movementTree
        self.buildTree = buildTree
        self.researchTree = researchTree

    def execute(boardController):
        # Runs one turn through the Tree(s)
        actionNum = topTree.execute(boardController)
        if actionNum == 1:
            # harvest
            res = harvestTree.execute(boardController)
            if res:
                print("harvestTree did not execute an action and instead returned", res)
        elif actionNum == 2:
            # attack
            res = attackTree.execute(boardController)
            if res:
                print("attackTree did not execute an action and instead returned", res)
        elif actionNum == 3:
            # move
            res = movementTree.execute(boardController)
            if res:
                print("movementTree did not execute an action and instead returned", res)
        elif actionNum == 4:
            # build
            res = buildTree.execute(boardController)
            if res:
                print("buildTree did not execute an action and instead returned", res)
        elif actionNum == 5:
            # research
            res = researchTree.execute(boardController)
            if res:
                print("researchTree did not execute an action and instead returned", res)