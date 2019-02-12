import DecisionTreePlayer
import DecisionTreeUtils
import battlecode as bc
import random
import sys
import traceback
import time
import os
from copy import copy, deepcopy
from collections import deque




gc = bc.GameController()

print("**********************")
print(os.path.dirname(os.path.realpath(__file__)))
print("**********************")

''' Need to generate the 5 trees '''
topTree = createBasicTopTree()
harvestTree = createBasicHarvestTree()
attackTree = createBasicAttackTree()
moveTree = createBasicMoveTree()
buildTree = createBasicBuildTree()
researchTree = createBasicResearchTree()

player = DecisionTreePlayer(topTree, harvestTree, attackTree, moveTree, buildTree, researchTree)

while True:
    
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')
    try:
        print("Money: " + str(gc.karbonite()))

        #ALL the money really happens in here 
        player.excecute(bc)

    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()



