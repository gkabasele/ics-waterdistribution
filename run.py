import os
import shutil
import time
from component import *
from twisted.internet import reactor 


'''
+-----------+ +------+ +----------------+ +---------+
|   PUMP    |=| TANK1|=|    PIPELINE    |=| TANK2   |
+-----------+ +------+ +----------------+ +---------+

'''

STORE = './variables'
PERIOD = 1
DURATION = 60

if os.path.exists('variables'):
    shutil.rmtree('variables')
    

#Variable Name
PUMP_RNG = "pump_running"
TANK1_LVL = "tank1_level"
TANK2_LVL = "tank2_level"
TANK1_VLV = "tank1_valve"
FLOW_RATE = "flow_rate"


pump_tank1_q = ComponentQueue(1)

tank1_pipeline_q = ComponentQueue(1)

pipeline_tank2_q = ComponentQueue(1)


pump = Pump('pump',None, pump_tank1_q, STORE, 5, True)
pump.start('pump', PERIOD, DURATION, PUMP_RNG)

tank1 = Tank('tank1', pump_tank1_q, tank1_pipeline_q, STORE, 50, 30, 0, 10, True)
tank1.start('tank1', PERIOD, DURATION, TANK1_LVL, TANK1_VLV)

pipeline = Pipeline('pipeline', tank1_pipeline_q, pipeline_tank2_q, STORE, 0)
pipeline.start('pipeline', PERIOD, DURATION, FLOW_RATE)

tank2 = Tank('tank2', pipeline_tank2_q, None, STORE, 50, 30, 0, 10, False) 
tank2.start('tank2', PERIOD, DURATION, TANK2_LVL)

pump.wait_end()
tank1.wait_end()
pipeline.wait_end()
tank2.wait_end()
#reactor.run()

#pump.stop()
#tank1.stop()
#pipeline.stop()
#tank2.stop()
