import random
from enum import Enum
import Node
import DecisionTree
import operator





# Helper Functions for creating a tree
def createRandomTopTreeDecisionNode():
    actionType = random.choice(list(ActionType))
    node = DecisionNode(None, actionType)
    return node


def createRandomValOperandNode(mean, stdev):
    intval = int(random.gauss(mean, stdev))
    node = OperandNode(intval)
    return node


#def createRandomBoardInfoOperandNode(boardController):

'''
    Harvest = 1
    Attack = 2
    Move = 3 #(or garrison)
    Build = 4 #(worker or factory)
    Research = 5
'''
def createBasicTopTree() -> DecisionTree:
    attackNode = DecisionNode(None, ActionType.Attack)
    harvestNode = DecisionNode(None, ActionType.Harvest)
    moveNode = DecisionNode(None, ActionType.Move)
    buildNode = DecisionNode(None, ActionType.Build)
    randomProbNode1 = BooleanNode(randomChance, [0.25])
    randomProbNode2 = BooleanNode(randomChance, [0.25])
    randomProbNode3 = BooleanNode(randomChance, [0.25])

    lastIf = IfNode(randomProbNode3, moveNode, attackNode)
    secondIf = IfNode(randomProbNode2, buildNode, lastIf)
    firstIf = IfNode(randomProbNode1, harvestNode, secondIf)
    topTree = DecisionTree(firstIf)
    return topTree

def createBasicHarvestTree() -> DecisionTree:
    harvestNode = DecisionNode(workerHarvestBehavior)
    workerSelectNode = InformationNode(selectRandomWorker, harvestNode)
    harvestTree = DecisionTree(workerSelectNode)
    return harvestTree


def createBasicBuildTree() -> DecisionTree:
    workerBuildNode = DecisionNode(workerBuildBehavior)
    workerBuildRocketNode = DecisionNode(workerBuildRocket)
    randomProbNode1 = BooleanNode(randomChance, [0.2])
    randomProbNode2 = BooleanNode(randomChance, [0.5])
    
    selectWorkerNode1 = InformationNode(selectRandomWorker, workerBuildRocketNode)
    selectWorkerNode2 = InformationNode(selectRandomWorker, workerBuildNode)
    workerIfNode = IfNode(randomProbNode1, selectWorkerNode1, selectWorkerNode2)

    buildUnitNode = DecisionNode(factory_produce_random)
    selectRandomFactoryNode = InformationNode(selectRandomFactory, buildUnitNode)
    
    factoryIfNode = IfNode(randomProbNode2, selectRandomFactoryNode, workerIfNode)

    buildTree = DecisionTree(factoryIfNode)
    return buildTree


def createBasicMoveTree() -> DecisionTree:
    #need to pick where to move the unit. Bottom Up construction
    moveRandomDirectionNode = DecisionNode(unitMoveRandomBehavior)
    moveTowardEnemyNode = DecisionNode(unitMoveTowardEnemyBehavior)
    moveTowardAllyNode = DecisionNode(unitMoveTowardAllyBehavior)

    isWorkerNode = BooleanNode(isWorker)
    elseIfWorkerNode = IfNode(isWorkerNode, moveRandomDirectionNode, moveTowardEnemyNode)

    isHealerNode = BooleanNode(isHealer)
    selectUnitNode = InformationNode(selectRandomMoveableUnit, None)
    ifHealerNode = IfNode(isHealerNode, moveTowardAllyNode, elseIfWorkerNode, selectUnitNode)
    #need to pick a unit
    #selectUnitNode = InformationNode(selectRandomMoveableUnit, ifHealerNode)
    #moveTree = DecisionTree(selectUnitNode)
    moveTree = DecisionTree(ifHealerNode)
    return moveTree


def createBasicAttackTree() -> DecisionTree:
    
    attackBehaviorNode = DecisionNode(nonWorkerAttackBehavior)
    #select Unit
    selectUnitNode = InformationNode(selectRandomRobotForAttack, attackBehaviorNode)
    attackTree = DecisionTree(selectUnitNode)
    return attackTree;

def createBasicResearchTree() -> DecisionTree:
    node = DecisionNode(random_unit_type);
    return DecisionTree(node); #TODO: total hogwash right now.



# Helper Functions for the game
def selectRandomFactory(battleCode, gc):
    factories = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Factory]
    if factories != []:
        return random.choice(factories)
    return None

def selectRandomWorker(battleCode, gc):
    workers = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Worker]
    print(workers)
    if workers != []:
        return random.choice(workers)
    return None

def selectRandomKnight(battleCode, gc):
    knights = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Knight]
    if knights != []:
        return random.choice(knights)
    return None

def selectRandomRanger(battleCode, gc):
    rangers = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Ranger]
    if rangers != []:
        return random.choice(rangers)
    return None

def selectRandomMage(battleCode, gc):
    mages = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Mage]
    if mages != []:
        return random.choice(mages)
    return None

def selectRandomHealer(battleCode, gc):
    healers = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Healer]
    if healers:
        return random.choice(healers)
    return None

def selectRandomMoveableUnit(battleCode, gc):
    units = [x for x in gc.my_units() if x.unit_type != battleCode.UnitType.Factory]
    units = [x for x in units if x.unit_type != battleCode.UnitType.Rocket]
    if units != []:
        return random.choice(units)
    print("No units were found that can be moved in selectRandomMoveableUnit")
    return None

def selectRandomRobotForAttack(battleCode, gc):
    nonWorkers = [x for x in gc.my_units() if x.unit_type != battleCode.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != battleCode.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != battleCode.UnitType.Worker]
    if nonWorkers != []:
        return random.choice(nonWorkers)
    return None


def selectUnitTypesThatCanAttack(bc, gc):
    
    #TODO: Not in all_functions\
    nonWorkers = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Worker]
    attackReady = [x for x in nonWorkers if gc.is_attack_ready(unit.id)]
    can_attack = []
    my_team = gc.team()
    enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
    for unit in attackReady:
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    can_attack.append(unit)
                    break
    types = set()
    for u in can_attack:
        types.add(u.UnitType)
    return list(types)



def selectRandomUnitThatCanAttack(bc, gc):
    nonWorkers = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Worker]
    attackReady = [x for x in nonWorkers if gc.is_attack_ready(unit.id)]
    can_attack = []
    my_team = gc.team()
    enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
    for unit in attackReady:
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    can_attack.append(unit)
                    break

    if len(can_attack) != 0:
        return random.choice(can_attack)
    else:
        return selectRandomRobotForAttack(bc,gc)


def selectUnitDealingMostDamageThatCanAttack(bc, gc):
    nonWorkers = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Worker]
    attackReady = [x for x in nonWorkers if gc.is_attack_ready(unit.id)]

    can_attack = []
    my_team = gc.team()
    enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
    for unit in attackReady:
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    can_attack.append(unit)
                    break

    random.shuffle(can_attack)
    bestUnit = None
    for u in can_attack:
        if bestUnit == None:
            bestUnit = u
        if u.damage() > bestUnit.damage():
            bestUnit = u

    return bestUnit


def selectUnitWithLeastLifeThatCanAttack(bc, gc):
    nonWorkers = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != bc.UnitType.Worker]
    attackReady = [x for x in nonWorkers if gc.is_attack_ready(unit.id)]

    can_attack = []
    my_team = gc.team()
    enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
    for unit in attackReady:
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    can_attack.append(unit)
                    break

    random.shuffle(can_attack)
    leastLife = None
    for u in can_attack:
        if leastLife == None:
            leastLife = u
        if u.health < leastLife.health:
            leastLife = u

    return leastLife





def selectRandomUnitThatCanMove(bc, gc):
    movables = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    movables = [x for x in movables if x.unit_type != bc.UnitType.Rocket]
    moveReady = [x for x in movables if gc.is_move_ready(unit.id)]
    can_move = []
    for unit in moveReady:
        random_directions = list(bc.Direction)
        # Iterate through each direction
        for direct1 in random_directions:
            if gc.can_move(unit.id, direct1):
                can_move.append(unit)
                break
    if len(can_move) != 0:
        return random.choice(can_move)
    else:
        return selectRandomMoveableUnit(bc, gc)


def selectUnitThatCanAttackToMove(bc, gc):
    movables = [x for x in gc.my_units() if x.unit_type != bc.UnitType.Factory]
    movables = [x for x in movables if x.unit_type != bc.UnitType.Rocket]
    moveReady = [x for x in movables if gc.is_move_ready(unit.id)]
    moveAttackReady = [x for x in moveReady if gc.is_attack_ready(unit.id)]
    can_move = []
    for unit in moveAttackReady:
        random_directions = list(bc.Direction)
        # Iterate through each direction
        for direct1 in random_directions:
            if gc.can_move(unit.id, direct1):
                can_move.append(unit)
                break
    if len(can_move) != 0:
        return random.choice(can_move)
    else:
        return selectRandomUnitThatCanMove(bc, gc)


def selectWorkerToMoveTowardHarvesting(bc, gc):
    movables = [x for x in gc.my_units() if x.unit_type == bc.UnitType.Worker]
    return random.choice(movables)




def selectRandomRocket(battleCode, gc):
    rockets = [x for x in gc.my_units() if x.unit_type == battleCode.UnitType.Rocket]
    if rockets != []:
        return random.choice(rockets)
    return None


# Boolean Functions
def isKnight(battleCode, gc, unit):
    if type(unit) is type(battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Knight
    return False

def isRanger(battleCode, gc, unit):
    if type(unit) is type(battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Ranger
    return False

def isMage(battleCode, gc, unit):
    if type(unit) is type(battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Mage
    return False

def isHealer(battleCode, gc, unit):
    if type(unit) is type(battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Healer
    return False

def isWorker(battleCode, gc, unit):
    if type(unit) is type(battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Worker
    return False

def isFactory(battleCode, gc, unit):
    if type(unit) is type(battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Factory
    return False

def isRocket(battleCode, gc, unit):
    if type(unit) is type(battleCode.Unit):
        return unit.unit_type == battleCode.UnitType.Rocket
    return False
    

#Behaviors
def workerHarvestBehavior(battleCode, gc, unit):
    if unit:
        bot_can_harvest = worker_can_harvest(battleCode, gc, unit.id)

        if bot_can_harvest:
            gc.harvest(unit.id, bot_can_harvest)
    return

def workerCantHarvestBehavior(bc, gc, unit):
    ''' put worker in position to harvest '''
    if unit:
        if unit.worker_has_acted():
            return None
        #for each location around the unit 2 spaces away, check if can harvest, go towards it
        currMapLocation = unit.location.map_location()
        random_directions = list(bc.Direction)
        random.shuffle(random_directions)
        # Iterate through each direction
        directToGo = random_directions[0]
        bestKarbonite = 0
        for direct1 in random_directions:
            if not gc.can_move(unit.id, direct1):
                continue
            totalKarbonite = 0
            for direct2 in random_directions:
                totalKarbonite += gc.karbonite_at(currMapLocation.add(direct1).add(direct2))
            if totalKarbonite > bestKarbonite:
                directToGo = direct1

        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, directToGo):
            gc.move_robot(unit.id, directToGo)
    return None




def workerBuildBehavior(battleCode, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(battleCode, gc, unit)

        #replicate
        if bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
            gc.replicate(unit.id, bot_occupiable)

        #build if possible
        elif gc.karbonite() > battleCode.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, battleCode.UnitType.Factory, bot_occupiable):
            gc.blueprint(unit.id, battleCode.UnitType.Factory, bot_occupiable)

        # lastly, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == battleCode.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    #print('built a factory!')
                    continue
    return

def workerActionBehavior1(bc, gc, unit):
    if unit:
        d = random.choice(list(bc.Direction))
        bot_can_harvest = worker_can_harvest(bc, gc, unit.id)
        bot_occupiable = find_occupiable(bc, gc, unit)

        #build if possible
        if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, bot_occupiable):
            gc.blueprint(unit.id, bc.UnitType.Factory, bot_occupiable)

        #harvest
        elif bot_can_harvest:
            gc.harvest(unit.id, bot_can_harvest)

        #replicate
        elif bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
            gc.replicate(unit.id, bot_occupiable)

        # lastly, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    #print('built a factory!')
                    continue
    return

def workerActionBehavior2(bc, gc, unit):
    if unit:
        d = random.choice(list(bc.Direction))
        bot_can_harvest = worker_can_harvest(bc, gc, unit.id)
        bot_occupiable = find_occupiable(bc, gc, unit)

        #harvest
        if bot_can_harvest:
            gc.harvest(unit.id, bot_can_harvest)

        #build if possible
        elif gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, bot_occupiable):
            gc.blueprint(unit.id, bc.UnitType.Factory, bot_occupiable)

        #replicate
        elif bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
            gc.replicate(unit.id, bot_occupiable)

        # lastly, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    #print('built a factory!')
                    continue
    return

def workerActionBehavior3(bc, gc, unit):
    if unit:
        d = random.choice(list(bc.Direction))
        bot_can_harvest = worker_can_harvest(bc, gc, unit.id)
        bot_occupiable = find_occupiable(bc, gc, unit)

        #replicate
        if bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
            gc.replicate(unit.id, bot_occupiable)

        #harvest
        elif bot_can_harvest:
            gc.harvest(unit.id, bot_can_harvest)

        #build if possible
        elif gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, bot_occupiable):
            gc.blueprint(unit.id, bc.UnitType.Factory, bot_occupiable)

        # lastly, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    #print('built a factory!')
                    continue
    return

def workerBuildRocket(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and bot_occupiable and gc.can_blueprint(unit.id, bc.UnitType.Rocket, bot_occupiable):
            gc.blueprint(unit.id, bc.UnitType.Rocket, bot_occupiable)
    return

def unitMoveRandomBehavior(bc, gc, unit):
    if unit:
        d = random.choice(list(bc.Direction))
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)
    return

def unitMoveTowardEnemyBehavior(battleCode, gc, unit):
    if unit:
        d = get_direction_of_closest_enemy(battleCode, gc, unit)
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)
        else:
            unitMoveRandomBehavior(battleCode, gc, unit)
    return

def unitMoveTowardAllyBehavior(battleCode, gc, unit):
    if unit:
        d = get_direction_of_closest_ally(battleCode, gc, unit)
        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)
        else:
            unitMoveRandomBehavior(battleCode,gc, unit)
    return

def nonWorkerAttackBehavior(battleCode, gc, unit):
    if unit:
        if unit.unit_type == battleCode.UnitType.Knight:
            return knight_action(battleCode, gc, unit)
        if unit.unit_type == battleCode.UnitType.Ranger:
            return ranger_action(battleCode, gc, unit)
        if unit.unit_type == battleCode.UnitType.Mage:
            return mage_action(battleCode, gc, unit)
        if unit.unit_type == battleCode.UnitType.Healer:
            return healer_action(battleCode, gc, unit)


# Taken straight from the medium player
def rocketBehavior(bc, gc, unit):
    if unit:
        my_team = gc.team()
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units_by_team(location.map_location(), 9, my_team)
            for other in nearby:
                if other.team == my_team and gc.can_load(unit.id, other.id):
                    # print('Loaded a ' + other.unit_type + ' into rocket!')
                    gc.load(unit.id, other.id)
                    continue
        destination = rocket_destination(bc, gc, unit.id)
        if gc.can_launch_rocket(unit.id, destination) and (len(unit.structure_garrison()) >= 6 or gc.round() >= 400): #leave these numbers for now
            gc.launch_rocket(unit.id, destination)
        if unit.location.map_location().planet == bc.Planet.Mars:
            bot_occupiable = find_occupiable(bc, gc, unit)
            if bot_occupiable:
                gc.unload(unit.id, find_occupiable(bc, gc, unit))
    return



def factory_produce_worker(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, bc.UnitType.Worker, bot_occupiable)
    return
    
def factory_produce_knight(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, bc.UnitType.Knight, bot_occupiable)
    return

def factory_produce_mage(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, bc.UnitType.Mage, bot_occupiable)
    return

def factory_produce_ranger(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, bc.UnitType.Ranger, bot_occupiable)
    return

def factory_produce_healer(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, bc.UnitType.Healer, bot_occupiable)
    return

def factory_produce_random(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        factory_produce(bc, gc, unit, random_unit_type(bc), bot_occupiable)
    return

def knight_action(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        bot_occupiable = find_occupiable(bc, gc, unit)
        # Check whether there is something to attack
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units_by_team(location.map_location(), 50, enemy_team)
            for other in nearby:
                if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    #print('Knight attacked a thing!')
                    gc.attack(unit.id, other.id)
                    return #we only want to attack

        if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
                direction = get_direction_of_closest_enemy(bc, gc, unit)
                if direction:
                    gc.move_robot(unit.id, direction)
                else:
                    gc.move_robot(unit.id, bot_occupiable)



def ranger_action(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        bot_occupiable = find_occupiable(bc, gc, unit)
        # Check whether there is something to attack
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units_by_team(location.map_location(), 50, enemy_team)
            for other in nearby:
                if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    #print('Knight attacked a thing!')
                    gc.attack(unit.id, other.id)
                    return #we only want to attack

        if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
                direction = get_direction_of_closest_enemy(bc, gc, unit)
                if direction:
                    gc.move_robot(unit.id, direction)
                else:
                    gc.move_robot(unit.id, bot_occupiable)

def mage_action(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        bot_occupiable = find_occupiable(bc, gc, unit)
        # Check whether there is something to attack
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units_by_team(location.map_location(), 50, enemy_team)
            for other in nearby:
                if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    #print('Knight attacked a thing!')
                    gc.attack(unit.id, other.id)
                    return #we only want to attack
        
        if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
                direction = get_direction_of_closest_enemy(bc, gc, unit)
                if direction:
                    gc.move_robot(unit.id, direction)
                else:
                    gc.move_robot(unit.id, bot_occupiable)

def healer_action(bc, gc, unit):
    if unit:
        bot_occupiable = find_occupiable(bc, gc, unit)
        # Check whether there is something to attack
        location = unit.location

        if bot_occupiable and gc.is_move_ready(unit.id) and gc.can_move(unit.id, bot_occupiable):
                direction = get_direction_of_closest_ally(bc, gc, unit)
                if direction:
                    gc.move_robot(unit.id, direction)
                else:
                    gc.move_robot(unit.id, bot_occupiable)

''' The following were taken from the medium player's helper functions '''

#gives adjacent direction or space for a unit to move or place something
def find_occupiable(bc, gc, unit):
    if unit:
        if unit.location.is_in_garrison():
            return None
        # Create a random order of directions
        random_directions = list(bc.Direction)
        random.shuffle(random_directions)
        # Iterate through each direction
        for direct in random_directions:
            #print(str(unit.location.map_location().add(dir).clone()) + " ;P" )
            if unit.location.map_location().add(direct):
                loc = unit.location.map_location().add(direct)
            else:
                continue
            loc_map = gc.starting_map(loc.planet)

            if (loc.x < loc_map.width and loc.x >= 0 and loc.y < loc_map.height and loc.y >= 0
                and gc.is_occupiable(unit.location.map_location().add(direct))):
                #if gc.can_move(unit.id, dir) and gc.is_occupiable(unit.location.map_location().add(dir)):
                return direct
    return None

def worker_can_harvest(bc, gc, unit_id):
    for direct in list(bc.Direction):
        if gc.can_harvest(unit_id, direct):
             return direct
    return None

def worker_unit_can_harvest(bc, gc, unit):
    return worker_can_harvest(bc, gc, unit.id)


def factory_produce(bc, gc, unit, unit_type, bot_occupiable):
    if unit:
        garrison = unit.structure_garrison()
        if len(garrison) > 0:
            if bot_occupiable and gc.can_unload(unit.id, bot_occupiable):
                gc.unload(unit.id, bot_occupiable)
        elif gc.can_produce_robot(unit.id, unit_type):
            gc.produce_robot(unit.id, unit_type)

def random_unit_type(battleCode):
    unit_types = [battleCode.UnitType.Knight, battleCode.UnitType.Ranger, battleCode.UnitType.Mage, battleCode.UnitType.Healer]
    return random.choice(unit_types)

def rocket_destination(battleCode, gc, unit_id):
    x = random.randint(0, gc.starting_map(battleCode.Planet.Mars).width)
    y = random.randint(0, gc.starting_map(battleCode.Planet.Mars).height)
    location = battleCode.MapLocation(battleCode.Planet.Mars, x, y)
    if gc.starting_map(battleCode.Planet.Mars).is_passable_terrain_at(location):
        return battleCode.MapLocation(battleCode.Planet.Mars, x, y)
    else:
        return rocket_destination(battleCode, gc, unit_id)

def get_direction_of_closest_enemy(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        closest_enemy_dist = 99999
        closest_enemy_id = None
        direction = None
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                distance = unit.location.map_location().distance_squared_to(other.location.map_location())
                if distance < closest_enemy_dist:
                    closest_enemy_dist = distance
                    closest_enemy_id = other.id;
                    if closest_enemy_id:
                        direction = unit.location.map_location().direction_to(other.location.map_location())
        if direction:                
            return direction
        else:
            return random.choice(list(bc.Direction))
    return random.choice(list(bc.Direction))

def get_direction_of_closest_ally(bc, gc, unit):
    if unit:
        closest_ally_dist = 99999
        closest_ally_id = None
        direction = None
        my_team = gc.team();
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, my_team)
        for other in nearby:
            if other.team == my_team:
                distance = unit.location.map_location().distance_squared_to(other.location.map_location())
                if distance < closest_ally_dist:
                    closest_ally_dist = distance
                    closest_ally_id = other.id;
                    if closest_ally_id:
                        direction = unit.location.map_location().direction_to(other.location.map_location())
        return direction
    return random.choice(list(bc.Direction))


def randomChance(bc, gc, chanceTrue = 0.25) -> bool:
    roll = random.random()
    return roll <= chanceTrue


def unitAttackRandomPossibleEnemy(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        enemies_in_range = []
        for other in nearby:
            if other.team != my_team:
                if gc.can_attack(unit.id, other.id):
                    enemies_in_range.append(other)
        enemy = random.choice(enemies_in_range)
        gc.attack(unit.id, enemy.id)
    return None #we attacked


def unitAttackClosestPossibleEnemy(bc, gc, unit):
    if unit:
        my_team = gc.team()
        enemy_team = bc.Team.Red if my_team == bc.Team.Blue else bc.Team.Blue
        closest_enemy_dist = 99999
        closest_enemy_id = None
        nearby = gc.sense_nearby_units_by_team(unit.location.map_location(), unit.vision_range, enemy_team)
        for other in nearby:
            if other.team != my_team:
                distance = unit.location.map_location().distance_squared_to(other.location.map_location())
                if distance < closest_enemy_dist:
                    closest_enemy_dist = distance
                    closest_enemy_id = other.id;
        gc.attack(unit.id, closest_enemy_id)
    return None #we attacked


def getRoundNumber(bc, gc):
    return gc.round()

def getNumberOfWorkers(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type() is bc.UnitType.Worker ]
    return len(y)

def getNumberOfFactories(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type() is bc.UnitType.Factory]
    return len(y)

def getNumberOfRockets(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type() is bc.UnitType.Rocket ]
    return len(y)

def getNumberOfKnights(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type() is bc.UnitType.Knight ]
    return len(y)

def getNumberOfRangers(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type() is bc.UnitType.Ranger ]
    return len(y)

def getNumberOfMages(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type() is bc.UnitType.Mages ]
    return len(y)

def getNumberOfHealers(bc, gc):
    y = [x for x in gc.my_units() if x.unit_type() is bc.UnitType.Healer ]
    return len(y)



def getKarbonite(bc, gc):
    return gc.karbonite()

'''

I want to define some lists of similar functions in order to mutate 
Preferably, each function only is in one group.

'''


#params are bc, gc
select_factory_functions = [
    selectRandomFactory,
]

# params are bc, gc, unit of type factory
factory_produce_functions = [
    factory_produce_worker,
    factory_produce_knight,
    factory_produce_mage,
    factory_produce_ranger,
    factory_produce_healer,
    factory_produce_random
]


#params are bc, gc
select_worker_functions = [
    selectRandomWorker
]

select_worker_build_functions = [
    selectRandomWorker
]

worker_harvest_functions = [
    workerHarvestBehavior
]

worker_build_functions = [
    workerBuildBehavior,
    workerBuildRocket
]

#params are bc, gc, unit of type worker
worker_behavior_functions = [
    #workerBuildBehavior,
    workerActionBehavior1,
    workerActionBehavior2,
    workerActionBehavior3
    #workerBuildRocket
]

#params are bc, gc
select_knight_functions = [
    selectRandomKnight
]

#params are bc, gc, unit of type knight
knight_action_functions = [
    knight_action
]

#params are bc, gc
select_ranger_functions = [
    selectRandomRanger
]

#params are bc, gc, unit of type ranger
ranger_action_functions = [
    ranger_action
]

#params are bc, gc
select_mage_functions = [
    selectRandomMage
]

#params are bc, gc, unit of type ranger
mage_action_functions = [
    mage_action
]

#params are bc, gc
select_healer_functions = [
    selectRandomHealer
]

#params are bc, gc, unit of type ranger
healer_action_functions = [
    healer_action
]

select_attacker_functions = [
    selectRandomUnitThatCanAttack,
    selectUnitDealingMostDamageThatCanAttack,
    selectUnitWithLeastLifeThatCanAttack
]

select_moveable_unit_functions = [
    selectRandomUnitThatCanMove,
    selectUnitThatCanAttackToMove,
    selectWorkerToMoveTowardHarvesting
]

unit_attack_functions = [
    unitAttackClosestPossibleEnemy,
    unitAttackRandomPossibleEnemy
]

unit_heal_functions = [
    healer_action #todo, this isn't a correct function for this
]

unit_move_functions = [
    unitMoveRandomBehavior,
    unitMoveTowardAllyBehavior,
    unitMoveTowardEnemyBehavior
]

worker_can_harvest_functions = [
    worker_unit_can_harvest
]

worker_cant_harvest_functions = [
    workerCantHarvestBehavior
]

game_number_info_functions = [
    getRoundNumber,
    getNumberOfWorkers,
    getNumberOfFactories,
    getNumberOfKnights,
    getNumberOfRangers,
    getNumberOfMages,
    getNumberOfHealers,
    getNumberOfRockets,
    getKarbonite
]

random_chance_function = [
    randomChance
]

is_unit_type_functions = [
    isHealer,
    isKnight,
    isWorker,
    isRanger,
    isMage,
    isFactory,
    isRocket
]


allFunctionSets = [
    select_factory_functions,
    factory_produce_functions,
    select_worker_functions,
    select_worker_build_functions,
    worker_harvest_functions,
    worker_build_functions,
    worker_behavior_functions,
    select_knight_functions,
    knight_action_functions,
    select_ranger_functions,
    ranger_action_functions,
    select_mage_functions,
    mage_action_functions,
    select_healer_functions,
    healer_action_functions,
    select_attacker_functions,
    select_moveable_unit_functions,
    unit_attack_functions,
    unit_heal_functions,
    unit_move_functions,
    worker_can_harvest_functions,
    worker_cant_harvest_functions,
    game_number_info_functions,
    random_chance_function,
    is_unit_type_functions
]




def createRandomAttackTree():
    selectUnitFunction = random.choice(select_attacker_functions)
    selectUnitInfoNode = InformationNode(selectUnitFunction)
    
    isHealerNode = BooleanNode(isHealer)

    healFunction = random.choice(unit_heal_functions)
    healDecisionNode = DecisionNode(healFunction)

    if random.random() <= .75:
        # we do a separate function for Knight and ranged
        isKnightNode = BooleanNode(isKnight)
        knightAttackFunction = random.choice(unit_attack_functions)
        knightAttackDecisionNode = DecisionNode(knightAttackFunction)

        if random.random() <= .66:
            #separate for mage and ranger
            isRangerNode = BooleanNode(isRanger)
            rangerAttackFunction = random.choice(unit_attack_functions)
            rangerAttackNode = DecisionNode(rangerAttackFunction)
            mageAttackFunction = random.choice(unit_attack_functions)
            mageAttackNode = DecisionNode(mageAttackFunction)

            ifRangerNode = IfNode(isRangerNode, rangerAttackNode, mageAttackNode)
            ifKnightNode = IfNode(isKnightNode, knightAttackDecisionNode, ifRangerNode)



        else:
            rangedAttackFunction = random.choice(unit_attack_functions)
            rangedAttackDecisionNode = DecisionNode(rangedAttackFunction)
            ifKnightNode = IfNode(isKnightNode, knightAttackDecisionNode, rangedAttackDecisionNode)

        root = IfNode(isHealerNode, healDecisionNode, ifKnightNode, selectUnitInfoNode)
        return DecisionTree(root)


    else:
        attackFunction = random.choice(unit_attack_functions)
        attackDecisionNode = DecisionNode(attackFunction)

        root = IfNode(isHealerNode, healDecisionNode, attackDecisionNode, selectUnitInfoNode)
        return DecisionTree(root)


def createRandomHarvestTree():
    selectUnitFunction = random.choice(select_worker_functions)
    selectUnitInfoNode = InformationNode(selectUnitFunction)

    workerCanHarvestFunction = random.choice(worker_can_harvest_functions)
    canHarvestNode = BooleanNode(workerCanHarvestFunction)

    cantHarvestFunction = random.choice(worker_cant_harvest_functions)
    cantHarvestNode = DecisionNode(cantHarvestFunction)


    harvestFunction = random.choice(worker_harvest_functions)
    harvestNode = DecisionNode(harvestFunction)

    root = IfNode(canHarvestNode, harvestNode, cantHarvestNode, selectUnitInfoNode)
    return DecisionTree(root)


def createRandomBuildTree():
    #TODO, look at phases and how many things we have
    firstCheckFunction = random.choice(game_number_info_functions)
    firstChildLeftNode = InformationNode(firstCheckFunction)
    if firstCheckFunction is getRoundNumber or firstCheckFunction is getKarbonite:
        firstChildRightNode = OperandNode(random.randint(0,999))
    else:
        firstChildRightNode = createRandomValOperandNode(5,2)
    firstCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = firstChildLeftNode, secondChild = firstChildRightNode, isGCFunction = False)

    # Now we recurse
    leftSubtree = recursiveRandomBuildSubtree(3, 0, 0.9)
    rightSubtree = recursiveRandomBuildSubtree(3, 0, 0.9)

    root = IfNode(firstCheckBoolNode, leftSubtree, rightSubtree)
    return DecisionTree(root)



def recursiveRandomBuildSubtree(maxRecursion, currentRecursion, percentRecurse):
    #TODO, look at phases and how many things we have
    firstCheckFunction = random.choice(game_number_info_functions)
    firstChildLeftNode = InformationNode(firstCheckFunction)
    if firstCheckFunction is getRoundNumber or firstCheckFunction is getKarbonite:
        firstChildRightNode = OperandNode(random.randint(0,999))
    else:
        firstChildRightNode = createRandomValOperandNode(5,2)
    firstCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = firstChildLeftNode, secondChild = firstChildRightNode, isGCFunction = False)

    if currentRecursion == maxRecursion:
        #force Decision Node both
        if random.random() < 0.5:
            # choose worker to build
            select_builder_function = random.choice(select_worker_build_functions)
            lChildFunction = random.choice(worker_build_functions)
            lChildNode = DecisionNode(lChildFunction)
            rChildFunction = random.choice(worker_build_functions)
            rChildNode = DecisionNode(rChildFunction)
        else:
            select_builder_function = random.choice(select_factory_functions)
            lChildFunction = random.choice(factory_produce_functions)
            lChildNode = DecisionNode(lChildFunction)
            rChildFunction = random.choice(factory_produce_functions)
            rChildNode = DecisionNode(rChildFunction)

        selectBuilderNode = InformationNode(select_builder_function)

        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode, selectBuilderNode)
        return junctionNode


    if percentRecurse < random.random():
        #force Decision node left:
        if percentRecurse < random.random():
            #Also force Decision node right:

            if random.random() < 0.5:
                # choose worker to build
                select_builder_function = random.choice(select_worker_build_functions)
                lChildFunction = random.choice(worker_build_functions)
                rChildFunction = random.choice(worker_build_functions)
                lChildNode = DecisionNode(lChildFunction)
                rChildNode = DecisionNode(rChildFunction)
            else:
                select_builder_function = random.choice(select_factory_functions)
                lChildFunction = random.choice(factory_produce_functions)
                lChildNode = DecisionNode(lChildFunction)
                rChildFunction = random.choice(factory_produce_functions)
                rChildNode = DecisionNode(lChildFunction)

            selectBuilderNode = InformationNode(select_builder_function)
            junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode )
            return junctionNode


        else:
            #only the left is Decision
            if random.random() < 0.5:
                # choose worker to build
                select_builder_function = random.choice(select_worker_build_functions)
                lChildFunction = random.choice(worker_build_functions)
                lChildNode = DecisionNode(lChildFunction)
            else:
                select_builder_function = random.choice(select_factory_functions)
                lChildFunction = random.choice(factory_produce_functions)
                lChildNode = DecisionNode(lChildFunction)

            selectBuilderNode = InformationNode(select_builder_function, lChildNode)

            rChildNode = recursiveRandomBuildSubtree(maxRecursion, currentRecursion+1, percentRecurse)

            junctionNode = IfNode(firstCheckBoolNode, selectBuilderNode, rChildNode )
            return junctionNode


    elif percentRecurse < random.random():
        #force ONLY Decision node right:
        if random.random() < 0.5:
            # choose worker to build
            select_builder_function = random.choice(select_worker_build_functions)
            rChildFunction = random.choice(worker_build_functions)
            rChildNode = DecisionNode(rChildFunction)
        else:
            select_builder_function = random.choice(select_factory_functions)
            rChildFunction = random.choice(factory_produce_functions)
            rChildNode = DecisionNode(rChildFunction)

        selectBuilderNode = InformationNode(select_builder_function, rChildNode)

        lChildNode = recursiveRandomBuildSubtree(maxRecursion, currentRecursion+1, percentRecurse)

        junctionNode = IfNode(firstCheckBoolNode, lChildNode, selectBuilderNode)
        return junctionNode

    else:
        #recurse
        lChildNode = recursiveRandomBuildSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        rChildNode = recursiveRandomBuildSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
        return junctionNode




def createRandomMoveTree():
    #TODO
    gameCheckFunction = random.choice(game_number_info_functions)
    gameCheckNode = InformationNode(gameCheckFunction)
    if gameCheckFunction is getRoundNumber or gameCheckFunction is getKarbonite:
        gameCheckValueNode = OperandNode(random.randint(0,999))
    else:
        gameCheckValueNode = createRandomValOperandNode(5,2)
    gameCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = gameCheckNode, secondChild = gameCheckValueNode, isGCFunction = False)

    # now recurse
    leftSubtree = recursiveRandomMoveSubtree(3, 0, 0.8)
    rightSubtree = recursiveRandomMoveSubtree(3, 0, 0.8)
    root = IfNode(gameCheckBoolNode, leftSubtree, rightSubtree)
    return DecisionTree(root)



def recursiveRandomMoveSubtree(maxRecursion, currentRecursion, percentRecurse):
    #TODO, look at phases and how many things we have
    gameCheckFunction = random.choice(game_number_info_functions)
    gameCheckNode = InformationNode(gameCheckFunction)
    if gameCheckFunction is getRoundNumber or gameCheckFunction is getKarbonite:
        gameCheckValueNode = OperandNode(random.randint(0,999))
    else:
        gameCheckValueNode = createRandomValOperandNode(5,2)
    gameCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = gameCheckNode, secondChild = gameCheckValueNode, isGCFunction = False)

    if currentRecursion == maxRecursion:
        #force Decision Node both
        selectUnitNode = InformationNode(random.choice(select_moveable_unit_functions))

        lChildFunction = random.choice(unit_move_functions)
        lChildNode = DecisionNode(lChildFunction)
        rChildFunction = random.choice(unit_move_functions)
        rChildNode = DecisionNode(rChildFunction)

        junctionNode = IfNode(gameCheckBoolNode, lChildNode, rChildNode, selectUnitNode)
        return junctionNode


    if percentRecurse < random.random(): 
        #force Decision node left:
        lChildFunction = random.choice(unit_move_functions)
        lChildNode = DecisionNode(lChildFunction)
        select_unit_function = random.choice(select_moveable_unit_functions)

        if percentRecurse < random.random(): 
            #Also force right
            rChildFunction = random.choice(unit_move_functions)
            rChildNode = DecisionNode(rChildFunction)
            selectUnitNode = InformationNode(select_unit_function)

            junctionNode = IfNode(gameCheckBoolNode, lChildNode, rChildNode, selectUnitNode)

        else:
            rChildNode = recursiveRandomMoveSubtree(maxRecursion, currentRecursion+1, percentRecurse)
            selectUnitNode = InformationNode(select_unit_function, lChildNode)

            junctionNode = IfNode(gameCheckBoolNode, selectUnitNode, rChildNode)

        return junctionNode
    
    elif percentRecurse < random.random():
        #just right side
        lChildNode = recursiveRandomMoveSubtree(maxRecursion, currentRecursion+1, percentRecurse)

        rChildFunction = random.choice(unit_move_functions)
        rChildNode = DecisionNode(rChildFunction)
        select_unit_function = random.choice(select_moveable_unit_functions)
        selectUnitNode = InformationNode(select_unit_function, rChildNode)

        junctionNode = IfNode(gameCheckBoolNode, lChildNode, selectUnitNode)
        return junctionNode


    else:
        lChildNode = recursiveRandomMoveSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        rChildNode = recursiveRandomMoveSubtree(maxRecursion, currentRecursion+1, percentRecurse)

        junctionNode = IfNode(gameCheckBoolNode, lChildNode, rChildNode)
        return junctionNode




def createRandomTopTree():
    #TODO, look at phases and how many things we have
    firstCheckFunction = random.choice(game_number_info_functions)
    firstChildLeftNode = InformationNode(firstCheckFunction)
    if firstCheckFunction is getRoundNumber or firstCheckFunction is getKarbonite:
        firstChildRightNode = OperandNode(random.randint(0,999))
    else:
        firstChildRightNode = createRandomValOperandNode(5,2)
    firstCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = firstChildLeftNode, secondChild = firstChildRightNode, isGCFunction = False)

    # Now we recurse
    leftSubtree = recursiveRandomTopSubtree(4, 0, 0.9)
    rightSubtree = recursiveRandomTopSubtree(4, 0, 0.9)

    root = IfNode(firstCheckBoolNode, leftSubtree, rightSubtree)
    return DecisionTree(root)



def recursiveRandomTopSubtree(maxRecursion, currentRecursion, percentRecurse): #TODO, remove build specifics
    #TODO, look at phases and how many things we have
    firstCheckFunction = random.choice(game_number_info_functions)
    firstChildLeftNode = InformationNode(firstCheckFunction)
    if firstCheckFunction is getRoundNumber:
        firstChildRightNode = OperandNode(random.randint(0,999))
        # TODO money caps at 400 if not gathering it
    elif: firstCheckFunction is getKarbonite:
        firstChildRightNode = OperandNode(random.randint(0,400))
    else:
        firstChildRightNode = createRandomValOperandNode(5,2)
    firstCheckBoolNode = BooleanNode(None, operation = operator.lt, firstChild = firstChildLeftNode, secondChild = firstChildRightNode, isGCFunction = False)

    if currentRecursion == maxRecursion:
        #force Decision Node both
        lChildNode = createRandomTopTreeDecisionNode()
        rChildNode = createRandomTopTreeDecisionNode()
        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
        return junctionNode


    if percentRecurse < random.random():
        #force Decision node left:
        if percentRecurse < random.random():
            #Also force Decision node right:
            lChildNode = createRandomTopTreeDecisionNode()
            rChildNode = createRandomTopTreeDecisionNode()
            junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
            return junctionNode

        else:
            #only the left is Decision
            lChildNode = createRandomTopTreeDecisionNode()
            rChildNode = recursiveRandomTopSubtree(maxRecursion, currentRecursion+1, percentRecurse)
            junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
            return junctionNode


    elif percentRecurse < random.random():
        #force ONLY Decision node right:
        rChildNode = createRandomTopTreeDecisionNode()
        lChildNode = recursiveRandomTopSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
        return junctionNode

    else:
        #recurse
        lChildNode = recursiveRandomTopSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        rChildNode = recursiveRandomTopSubtree(maxRecursion, currentRecursion+1, percentRecurse)
        junctionNode = IfNode(firstCheckBoolNode, lChildNode, rChildNode)
        return junctionNode








