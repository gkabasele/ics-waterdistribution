import os
import shutil
import time
from component import *


'''
+-----------+ +------+ +----------------+ +---------+
|   PUMP    |=| TANK1|=|    PIPELINE    |=| TANK2   |
+-----------+ +------+ +----------------+ +---------+

'''

STORE = './variables'
DURATION = 60

if os.path.exists('./variables'):
    shutil.rmtree(STORE)
    

#Variable Name
PUMP_RNG = "pump_running"
TANK1_LVL = "tank1_level"
TANK2_LVL = "tank2_level"
TANK1_VLV = "tank1_valve"
FLOW_RATE = "flow_rate"


pump_tank1_q = ComponentQueue(1)

tank1_pipeline_q = ComponentQueue(1)

pipeline_tank2_q = ComponentQueue(1)


pump = Pump('pump',None, pump_tank1_q, store, 5, True)
pump.run(1, PUMP_RNG)

tank1 = Tank('tank1', pump_tank1_q, tank1_pipeline_q, store, 50, 30, 0, 10, True)
tank1.run(1, TANK1_LVL, TANK1_VLV)

pipeline = Pipeline('pipeline', tank1_pipeline_q, pipeline_tank2_q, store, 0)
pipeline.run(1, FLOW_RATE)

tank2 = Tank('tank2', pipeline_tank2_q, None, store, 50, 30, 0, 10, False) 
tank2.run(1, TANK2_LVL)

end = time.time() + DURATION

while time.time() < end:
    pass

pump.stop()
tank1.stop()
pipeline.stop()
tank2.stop()
