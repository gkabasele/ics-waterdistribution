import os
import shutil
import time
import logging
import subprocess
from physical_process import  PhysicalProcess
from utils import *
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
    shutil.rmtree(EXPORT_VAR)

os.mkdir(EXPORT_VAR)

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


p.run()

# run PLC
py = "python"
ip = "localhost"
ip_args = "--ip"
port_args = "--port"
store_args = "--store"
prefix = "script_plc_"
ex = "--export"


pump_proc = subprocess.Popen([py, prefix+"pump.py", ip_args, ip, port_args, str(5020), store_args, STORE, ex, EXPORT_VAR], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
tank1_proc = subprocess.Popen([py, prefix+"tank1.py", ip_args, ip, port_args, str(5021), store_args, STORE, ex, EXPORT_VAR], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
pipe_proc = subprocess.Popen([py, prefix+"pipe.py", ip_args, ip, port_args, str(5022), store_args, STORE, ex, EXPORT_VAR], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
tank2_proc = subprocess.Popen([py, prefix+"tank2.py", ip_args, ip, port_args, str(5023), store_args, STORE, ex, EXPORT_VAR], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# run MTU
mtu_proc = subprocess.Popen([py, "script_mtu.py", ip_args, ip, port_args, str(3000), "--import", EXPORT_VAR], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#print pump_proc.communicate()
#print tank1_proc.communicate()
#print pipe_proc.communicate()
#print tank2_proc.communicate()
#print mtu_proc.communicate()

pump_proc.wait()
tank1_proc.wait()
pipe_proc.wait()
tank2_proc.wait()
mtu_proc.wait()
p.wait_end()

#print plc_pump.get(PUMP_RNG)
#print plc_tank1.get(TANK1_LVL)
#print plc_tank1.get(TANK1_VLV)
#print plc_pipe.get(FLOW_RATE)
#print plc_tank2.get(TANK2_LVL)


