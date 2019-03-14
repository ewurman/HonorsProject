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

    def getNumNodes(self):
        print("getting number of nodes in decision Tree")
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




class FixedSizeDecisionTree(DecisionTree):

    def __init__(self, node, treeID = 0, height = 4):
        self.root = node
        self.treeID = treeID
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






