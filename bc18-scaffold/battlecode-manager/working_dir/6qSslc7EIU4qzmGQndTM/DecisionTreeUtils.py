import random
from enum import Enum
import Node
import DecisionTree


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
    randomProbNode = BooleanNode(randomChance, [0.25])

    lastIf = IfNode(randomProbNode, moveNode, attackNode)
    secondIf = IfNode(randomProbNode, buildNode, lastIf)
    firstIf = IfNode(randomProbNode, harvestNode, secondIf)
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
    workerIfNode = IfNode(randomProbNode1, workerBuildRocket, workerBuildNode)
    selectWorkerNode = InformationNode(selectRandomWorker, workerIfNode)

    buildUnitNode = DecisionNode(factory_produce_random)
    selectRandomFactoryNode = InformationNode(selectRandomFactory, buildUnitNode)
    
    factoryIfNode = IfNode(randomProbNode2, selectRandomFactoryNode, selectWorkerNode)

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
    ifHealerNode = IfNode(isHealerNode, moveTowardAllyNode, elseIfWorkerNode)
    #need to pick a unit
    selectUnitNode = InformationNode(selectRandomMoveableUnit, ifHealerNode)
    moveTree = DecisionTree(selectUnitNode)
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
def selectRandomFactory(boardController):
    gc = boardController.GameController()
    factories = [x for x in gc.my_units() if x.unit_type == boardController.UnitType.Factory]
    return random.choice(factories)

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
    healers = [x for x in gc.my_units() if x.unit_type == boardController.UnitType.Healer]
    return random.choice(healers)

def selectRandomMoveableUnit(boardController):
    gc = boardController.GameController();
    units = [x for x in gc.my_units() if x.unit_type != boardController.UnitType.Factory]
    units = [x for x in units if x.unit_type != boardController.UnitType.Rocket]
    return random.choice(units)

def selectRandomRobotForAttack(boardController):
    gc = boardController.GameController();
    nonWorkers = [x for x in gc.my_units() if x.unit_type != boardController.UnitType.Factory]
    nonWorkers = [x for x in nonWorkers if x.unit_type != boardController.UnitType.Rocket]
    nonWorkers = [x for x in nonWorkers if x.unit_type != boardController.UnitType.Worker]
    return random.choice(nonWorkers)

def selectRandomRocket(boardController):
    gc = boardController.GameController()
    rockets = [x for x in gc.my_units() if x.unit_type == boardController.UnitType.Rocket]
    return random.choice(rockets)


# Boolean Functions
def isKnight(boardController, unit):
    return unit.unit_type == boardController.UnitType.Knight

def isRanger(boardController, unit):
    return unit.unit_type == boardController.UnitType.Ranger

def isMage(boardController, unit):
    return unit.unit_type == boardController.UnitType.Mage

def isHealer(boardController, unit):
    return unit.unit_type == boardController.UnitType.Healer

def isWorker(boardController, unit):
    return unit.unit_type == boardController.UnitType.Worker

def isFactory(boardController, unit):
    return unit.unit_type == boardController.UnitType.Factory

def isRocket(boardController, unit):
    return unit.unit_type == boardController.UnitType.Rocket


#Behaviors
def workerHarvestBehavior(boardController, unit):
    gc = boardController.GameController()
    #d = random.choice(directions)
    bot_can_harvest = worker_can_harvest(boardController, unit.id)
    #bot_occupiable = find_occupiable(boardController, unit)

    if bot_can_harvest:
        gc.harvest(unit.id, bot_can_harvest)
    return

def workerBuildBehavior(boardController, unit):
    gc = boardController.GameController()
    bot_occupiable = find_occupiable(boardController, unit)

    #replicate
    if bot_occupiable and gc.can_replicate(unit.id, bot_occupiable):
        gc.replicate(unit.id, bot_occupiable)

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

def workerActionBehavior1(boardController, unit):
    gc = boardController.GameController()
    d = random.choice(directions)
    bot_can_harvest = worker_can_harvest(boardController, unit.id)
    bot_occupiable = find_occupiable(boardController, unit)


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

def workerActionBehavior2(boardController, unit):
    gc = boardController.GameController()
    d = random.choice(directions)
    bot_can_harvest = worker_can_harvest(boardController, unit.id)
    bot_occupiable = find_occupiable(boardController, unit)

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

def workerActionBehavior3(boardController, unit):
    gc = boardController.GameController()
    d = random.choice(directions)
    bot_can_harvest = worker_can_harvest(boardController, unit.id)
    bot_occupiable = find_occupiable(boardController, unit)

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

def workerBuildRocket(boardController, unit):
    gc = boardController.GameController()
    bot_occupiable = find_occupiable(boardController, unit)
    if gc.karbonite() > boardController.UnitType.Rocket.blueprint_cost() and bot_occupiable and gc.can_blueprint(unit.id, bc.UnitType.Rocket, bot_occupiable):
        gc.blueprint(unit.id, bc.UnitType.Rocket, bot_occupiable)
    return

def unitMoveRandomBehavior(boardController, unit):
    gc = boardController.GameController()
    d = random.choice(directions)
    if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)
    return

def unitMoveTowardEnemyBehavior(boardController, unit):
    gc = boardController.GameController()
    d = get_direction_of_closest_enemy(boardController, unit)
    if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
        gc.move_robot(unit.id, d)
    else:
        unitMoveRandomBehavior(boardController, unit)
    return

def unitMoveTowardAllyBehavior(boardController, unit):
    gc = boardController.GameController()
    d = get_direction_of_closest_ally(boardController, unit)
    if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
        gc.move_robot(unit.id, d)
    else:
        unitMoveRandomBehavior(boardController, unit)
    return

def nonWorkerAttackBehavior(boardController, unit):
    if unit.unit_type == boardController.UnitType.Knight:
        return knight_action(boardController, unit)
    if unit.unit_type == boardController.UnitType.Ranger:
        return ranger_action(boardController, unit)
    if unit.unit_type == boardController.UnitType.Mage:
        return mage_action(boardController, unit)
    if unit.unit_type == boardController.UnitType.Healer:
        return healer_action(boardController, unit)


# Taken straight from the medium player
def rocketBehavior(boardController, unit):
    gc = boardController.GameController()
    my_team = gc.team()
    location = unit.location
    if location.is_on_map():
        nearby = gc.sense_nearby_units_by_team(location.map_location(), 9, my_team)
        for other in nearby:
            if other.team == my_team and gc.can_load(unit.id, other.id):
                # print('Loaded a ' + other.unit_type + ' into rocket!')
                gc.load(unit.id, other.id)
                continue
    destination = rocket_destination(boardController, unit.id)
    if gc.can_launch_rocket(unit.id, destination) and (len(unit.structure_garrison()) >= 6 or gc.round() >= 400): #leave these numbers for now
        gc.launch_rocket(unit.id, destination)
    if unit.location.map_location().planet == boardController.Planet.Mars:
        bot_occupiable = find_occupiable(unit)
        if bot_occupiable:
            gc.unload(unit.id, find_occupiable(unit))
    return



def factory_produce_worker(boardController, unit):
    bot_occupiable = find_occupiable(boardController, unit)
    factory_produce(boardController, unit, bc.UnitType.Worker, bot_occupiable)
    return
    
def factory_produce_knight(boardController, unit):
    bot_occupiable = find_occupiable(boardController, unit)
    factory_produce(boardController, unit, bc.UnitType.Knight, bot_occupiable)
    return

def factory_produce_mage(boardController, unit):
    bot_occupiable = find_occupiable(boardController, unit)
    factory_produce(boardController, unit, bc.UnitType.Mage, bot_occupiable)
    return

def factory_produce_ranger(boardController, unit):
    bot_occupiable = find_occupiable(boardController, unit)
    factory_produce(boardController, unit, bc.UnitType.Ranger, bot_occupiable)
    return

def factory_produce_healer(boardController, unit):
    bot_occupiable = find_occupiable(boardController, unit)
    factory_produce(boardController, unit, bc.UnitType.Healer, bot_occupiable)
    return

def factory_produce_random(boardController, unit):
    bot_occupiable = find_occupiable(boardController, unit)
    factory_produce(boardController, unit, random_unit_type(boardController), bot_occupiable)
    return

def knight_action(boardController, unit):
    gc = boardController.GameController()
    bot_occupiable = find_occupiable(boardController, unit)
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
            direction = get_direction_of_closest_enemy(boardController, unit)
            if direction:
                gc.move_robot(unit.id, direction)
            else:
                gc.move_robot(unit.id, bot_occupiable)

def ranger_action(boardController, unit):
    gc = boardController.GameController()
    bot_occupiable = find_occupiable(boardController, unit)
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
            direction = get_direction_of_closest_enemy(boardController, unit)
            if direction:
                gc.move_robot(unit.id, direction)
            else:
                gc.move_robot(unit.id, bot_occupiable)

def mage_action(boardController, unit):
    gc = boardController.GameController()
    bot_occupiable = find_occupiable(boardController, unit)
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
            direction = get_direction_of_closest_enemy(boardController, unit)
            if direction:
                gc.move_robot(unit.id, direction)
            else:
                gc.move_robot(unit.id, bot_occupiable)

def healer_action(boardController, unit):
    gc = boardController.GameController()
    bot_occupiable = find_occupiable(boardController, unit)
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
            direction = get_direction_of_closest_ally(boardController, unit)
            if direction:
                gc.move_robot(unit.id, direction)
            else:
                gc.move_robot(unit.id, bot_occupiable)

''' The following were taken from the medium player's helper functions '''

#gives adjacent direction or space for a unit to move or place something
def find_occupiable(boardController, unit):
    gc = boardController.GameController()
    if unit.location.is_in_garrison():
        return None
    # Create a random order of directions
    random_directions = list(boardController.Direction)
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

def worker_can_harvest(boardController, unit_id):
    gc = boardController.GameController()
    for direct in list(boardController.Direction):
        if gc.can_harvest(unit_id, direct):
             return direct
    return None

def factory_produce(boardController, unit, unit_type, bot_occupiable):
    gc = boardController.GameController()
    garrison = unit.structure_garrison()
    if len(garrison) > 0:
        if bot_occupiable and gc.can_unload(unit.id, bot_occupiable):
            gc.unload(unit.id, bot_occupiable)
    elif gc.can_produce_robot(unit.id, unit_type):
        gc.produce_robot(unit.id, unit_type)

def random_unit_type(boardController):
    unit_types = [boardController.UnitType.Knight, boardController.UnitType.Ranger, boardController.UnitType.Mage, boardController.UnitType.Healer]
    return random.choice(unit_types)

def rocket_destination(boardController, unit_id):
    x = random.randint(0, gc.starting_map(boardController.Planet.Mars).width)
    y = random.randint(0, gc.starting_map(boardController.Planet.Mars).height)
    location = boardController.MapLocation(boardController.Planet.Mars, x, y)
    if gc.starting_map(boardController.Planet.Mars).is_passable_terrain_at(location):
        return boardController.MapLocation(boardController.Planet.Mars, x, y)
    else:
        return rocket_destination(unit_id)

def get_direction_of_closest_enemy(boardController, unit):
    gc = boardController.GameController()
    my_team = gc.team()
    enemy_team = boardController.Team.Red if my_team == boardController.Team.Blue else boardController.Team.Blue
    closest_enemy_dist = 99999
    closest_enemy_id = None
    direction = None
    nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.vision_range, enemy_team)
    for other in nearby:
        if other.team != my_team:
            distance = unit.location.map_location().distance_squared_to(other.location.map_location())
            if distance < closest_enemy_dist:
                closest_enemy_dist = distance
                closest_enemy_id = other.id;
                if closest_enemy_id:
                    direction = unit.location.map_location().direction_to(other.location.map_location())
    return direction


def get_direction_of_closest_ally(boardController, unit):
    gc = boardController.GameController()
    closest_ally_dist = 99999
    closest_ally_id = None
    direction = None
    my_team = gc.team();
    nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.vision_range, my_team)
    for other in nearby:
        if other.team == my_team:
            distance = unit.location.map_location().distance_squared_to(other.location.map_location())
            if distance < closest_ally_dist:
                closest_ally_dist = distance
                closest_ally_id = other.id;
                if closest_ally_id:
                    direction = unit.location.map_location().direction_to(other.location.map_location())
    return direction


def randomChance(chanceTrue = 0.25) -> bool:
    roll = random.random()
    return roll <= chanceTrue



