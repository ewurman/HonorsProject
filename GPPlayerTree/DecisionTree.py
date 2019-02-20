import Node


class DecisionTree:

    def __init__(self, node, id = 0):
        self.root = node
        self.id = id


    def isLegal(self) -> bool:
        return True #TODO

    def printTree(self):
        self.root.printNode("")


    def getWriteString(self):
        return self.root.getWriteString("")


    def execute(self, battleCode, gameController):
        print("Executing a decision Tree")
        currNode = self.root
        ifParams = []
        permanantParams = []
        while(type(currNode) is not DecisionNode):

            print("At a node of type", type(currNode));
            if type(currNode) is IfNode:
                ifNode = currNode #IfNode(currNode)
                currNode, ifParams = ifNode.follow(battleCode, gameController, permanantParams, ifParams)

            elif type(currNode) is InformationNode: 
                #Information nodes not imediately under ifNodes' first children have their information stored
                # This is useful for say, selecting a unit
                print("Appending to permanantParams")
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







