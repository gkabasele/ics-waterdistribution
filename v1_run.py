import os
import shutil
import time
import logging
import utils
import subprocess
from physical_process import  PhysicalProcess
from plc import PLC
from mtu import WaterDistribution
from component import *
from twisted.internet import reactor 
from pymodbus.server.sync import ModbusConnectedRequestHandler

if os.path.exists(LOG):
    os.remove(LOG)

logging.basicConfig(filename = "ics.log", mode= 'w', format='[%(levelname)s][%(pathname)s-%(lineno)d] %(message)s', level= logging.DEBUG)

'''
+-----------+ +------+ +----------------+ +---------+
|   PUMP    |=| TANK1|=|    PIPELINE    |=| TANK2   |
+-----------+ +------+ +----------------+ +---------+

'''


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

plc_pump = PLC('localhost', 5021, STORE, 'plc-pump',pump_running = (CO,1))
plc_tank1 = PLC('localhost', 5022, STORE, 'plc-tank1' ,tank1_level = (HR,1), tank1_valve = (CO,1))
plc_pipe = PLC('localhost', 5023, STORE, 'plc-pipe',flow_rate = (IR,1))
plc_tank2 = PLC('localhost', 5020, STORE, 'plc-tank2',tank2_level = (HR,1)) 


p.run()

# run PLC


# run MTU

p.wait_end()
plc_pump.run('plc-pump', PERIOD, DURATION)
plc_tank1.run('plc-tank1', PERIOD, DURATION)
plc_pipe.run('plc-pipe', PERIOD, DURATION)
plc_tank2.run('plc-tank2', PERIOD, DURATION)

mtu = WaterDistribution('localhost', 3000)
mtu.import_variables(EXPORT_VAR)

plc_pump.wait_end(True)
plc_tank1.wait_end(True)
plc_pipe.wait_end(True)
plc_tank2.wait_end(True)
p.wait_end()
mtu.wait_end

print plc_pump.get(PUMP_RNG)
print plc_tank1.get(TANK1_LVL)
print plc_tank1.get(TANK1_VLV)
print plc_pipe.get(FLOW_RATE)
print plc_tank2.get(TANK2_LVL)


