'''
I want to define some lists of similar functions in order to mutate 
Preferably, each function only is in one group.

'''
import DecisionTreeUtils as dtu

#params are bc, gc
select_factory_functions = [
    dtu.selectRandomFactory,
]

# params are bc, gc, unit of type factory
factory_produce_functions = [
    dtu.factory_produce_worker,
    dtu.factory_produce_knight,
    dtu.factory_produce_mage,
    dtu.factory_produce_ranger,
    dtu.factory_produce_healer,
    dtu.factory_produce_random
]


#params are bc, gc
select_worker_functions = [
    dtu.selectRandomWorker
]

#params are bc, gc, unit of type worker
worker_behavior_functions = [
    dtu.workerHarvestBehavior,
    dtu.workerBuildBehavior,
    dtu.workerActionBehavior1,
    dtu.workerActionBehavior2,
    dtu.workerActionBehavior3,
    dtu.workerBuildRocket
]

#params are bc, gc
select_knight_functions = [
    dtu.selectRandomKnight
]

#params are bc, gc, unit of type knight
knight_action_functions = [
    dtu.knight_action
]

#params are bc, gc
select_ranger_functions = [
    dtu.selectRandomRanger
]

#params are bc, gc, unit of type ranger
ranger_action_functions = [
    dtu.ranger_action
]

#params are bc, gc
select_mage_functions = [
    dtu.selectRandomMage
]

#params are bc, gc, unit of type ranger
mage_action_functions = [
    dtu.mage_action
]

#params are bc, gc
select_healer_functions = [
    dtu.selectRandomHealer
]

#params are bc, gc, unit of type ranger
healer_action_functions = [
    dtu.healer_action
]

