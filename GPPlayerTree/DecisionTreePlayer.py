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

        ba       
        return 


