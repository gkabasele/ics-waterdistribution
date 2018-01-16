import os
import shutil
import time
from physical_process import  PhysicalProcess
from plc import PLC
from mtu import WaterDistribution
from component import *
from twisted.internet import reactor 


'''
+-----------+ +------+ +----------------+ +---------+
|   PUMP    |=| TANK1|=|    PIPELINE    |=| TANK2   |
+-----------+ +------+ +----------------+ +---------+

'''

STORE = './variables'
EXPORT_VAR = 'lplc_var.ex'
PERIOD = 1
DURATION = 60

if os.path.exists(EXPORT_VAR):
    os.remove(EXPORT_VAR)

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

plc_pump = PLC('localhost', 5021, STORE, pump_running = (CO,1))
plc_tank1 = PLC('localhost', 5022, STORE, tank1_level = (HR,1), tank1_valve = (CO,1))
plc_pipe = PLC('localhost', 5023, STORE, flow_rate = (IR,1))
plc_tank2 = PLC('localhost', 5020, STORE, tank2_level = (HR,1)) 

plcs = [plc_pump, plc_tank1, plc_pipe, plc_tank2]

for plc in plcs:
    plc.export_variables(EXPORT_VAR)


p.run()

plc_pump.run('plc-pump', PERIOD, DURATION)
plc_tank1.run('plc-tank1', PERIOD, DURATION)
plc_pipe.run('plc-pipe', PERIOD, DURATION)
plc_tank2.run('plc-tank2', PERIOD, DURATION)

mtu = WaterDistribution('localhost', 3000)
mtu.import_variables(EXPORT_VAR)
mtu.add_cond(TANK1_LVL, 0, 30, mtu.close_valve, mtu.open_valve)
mtu.add_cond(FLOW_RATE, 0, 20, mtu.close_valve, mtu.open_valve)
mtu.add_cond(TANK2_LVL, 0, 30, mtu.open_valve, mtu.close_valve)
mtu.create_task('mtu', PERIOD, DURATION)
mtu.start()

plc_pump.wait_end(True)
plc_tank1.wait_end(True)
plc_pipe.wait_end(True)
plc_tank2.wait_end(True)
p.wait_end()
mtu.wait_end

#print plc_pump.get(PUMP_RNG)
#print plc_tank1.get(TANK1_LVL)
#print plc_tank1.get(TANK1_VLV)
#print plc_pipe.get(FLOW_RATE)
#print plc_tank2.get(TANK2_LVL)


