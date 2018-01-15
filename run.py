import os
import shutil
import time
from physical_process import  PhysicalProcess
from plc import PLC
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

# Constant
# tank
t_height= 50
t_diameter = 30
t_hole = 10
# pipeline
p_diameter = 20
p_length = 40

# Variable Name
PUMP_RNG = "pump_running"
TANK1_LVL = "tank1_level"
TANK2_LVL = "tank2_level"
TANK1_VLV = "tank1_valve"
FLOW_RATE = "flow_rate"


p = PhysicalProcess(STORE)

pump = p.add_component(Pump, 5, True)
tank1 = p.add_component(Tank, t_height, t_diameter, t_hole, valve=True, name='tank1' )
tank2 = p.add_component(Tank, t_height, t_diameter, t_hole, valve=False, name='tank2')
pipeline = p.add_component(Pipeline, p_length, p_diameter)

p.add_variable(pump, PUMP_RNG)
p.add_variable(tank1, TANK1_LVL)
p.add_variable(tank1, TANK1_VLV)
p.add_variable(pipeline, FLOW_RATE)
p.add_variable(tank2, TANK2_LVL)

index_pump_tank = p.add_interaction(pump, tank1)
index_tank_pipe = p.add_interaction(tank1, pipeline)
index_pipe_tank = p.add_interaction(pipeline, tank2)

pump.add_task('pump-task', PERIOD, DURATION, PUMP_RNG, outbuf=index_pump_tank[0]) 
tank1.add_task('tank1-task', PERIOD, DURATION, TANK1_LVL, TANK1_VLV, inbuf=index_pump_tank[1], outbuf = index_tank_pipe[0])
pipeline.add_task('pipeline-task', PERIOD, DURATION, FLOW_RATE, inbuf= index_tank_pipe[1], outbuf = index_pipe_tank[0])
tank2.add_task('tank2-task', PERIOD, DURATION, TANK2_LVL, inbuf= index_pipe_tank[1])

plc_tank = PLC('localhost', 5020, STORE, 1, 1, 1, 1, tank2_level = (HR,1)) 

p.run()
plc_tank.run('plc-tank2', PERIOD, DURATION)

plc_tank.wait_end()
p.wait_end()

print plc_tank.get(TANK2_LVL)


