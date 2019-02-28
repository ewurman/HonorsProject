import Node


class DecisionTree:

    def __init__(self, node, id = 0):
        self.root = node
        self.id = id


    def isLegal() -> bool:
        return True #TODO

    def execute(boardController):
        currNode = self.root
        #parameters = []
        permanantParams = []
        while(type(currNode) is not DecisionNode):

            if type(currNode) is IfNode:
                ifNode = currNode #IfNode(currNode)
                currNode = ifNode.follow(boardController, parameters)

            if type(currNode) is InformationNode: 
                #Information nodes not imediately under ifNodes' first children have their information stored
                # This is useful for say, selecting a unit
                paramters.append(currNode.evaluate(boardController))
                currNode = currNode.follow()

            elif type(currNode) is BooleanNode:
                #why would we end up here?
                print("ERROR: Decision Tree execute is at a BooleanNode")

            else:
                print ("ERROR: Decision Tree execute at curreNode of None, Node, or DecisionNode")
                print ("    This should only get to ifNodes and then finish at a DecisionNode, but not in this loop")
        # Now currNode is a DecisionNode.
        if type(currNode) is DecisionNode:
            result = currNode.execute(boardController, paramters)
            return result #None if this executed an action, number otherwise indicating which action tree to use
            # 1 = Harvest
            # 2 = Attack
            # 3 = Move (or garrison)
            # 4 = Build (worker or factory)
            # 5 = Research
        else:
            print("ERROR: execute DecisionTree did not terminate at a DecisionNode");
            print("\t", type(currNode))







