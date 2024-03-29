import os
import shutil
import time
import logging
import subprocess
from pyics.physical_process import  PhysicalProcess
from pyics.utils import *
from pyics.plc import PLC
from pyics.component import *
from waterdistribution import WaterDistribution
from constants import *


if os.path.exists(LOG):
    os.remove(LOG)

logging.basicConfig(filename = "ics.log", mode= 'w', format='[%(asctime)s][%(levelname)s][%(pathname)s-%(lineno)d] %(message)s', level= logging.DEBUG)

'''
+-----------+ +------+ +----------------+ +---------+
|   PUMP    |=| TANK1|=|    PIPELINE    |=| TANK2   |
+-----------+ +------+ +----------------+ +---------+

'''


# Constant
# tank
t_height= 50
t_diameter = 30
t_hole = 10
# pipeline
p_diameter = 20
p_length = 40


if os.path.exists(STORE):
    shutil.rmtree(STORE)

p = PhysicalProcess(STORE)

pump = p.add_component(Pump, 5, True)
tank1 = p.add_component(Tank, t_height, t_diameter, t_hole, valve=False, name='tank1' )
tank2 = p.add_component(Tank, t_height, t_diameter, t_hole, valve=False, name='tank2')
pipeline = p.add_component(Pipeline, p_length, p_diameter)

p.add_variable(pump, PUMP_RNG)
p.add_variable(tank1, TANK1_LVL)
p.add_variable(tank1, TANK1_VLV)
p.add_variable(pipeline, FLOW_RATE)
p.add_variable(tank2, TANK2_LVL)

(pump_out, tank1_in) = p.add_interaction(pump, tank1)
(tank1_out, pipe_in) = p.add_interaction(tank1, pipeline)
(pipe_out, tank2_in) = p.add_interaction(pipeline, tank2)

pump.add_task('pump-task', PERIOD, DURATION, PUMP_RNG, outbuf=pump_out) 
tank1.add_task('tank1-task', PERIOD, DURATION, TANK1_LVL, TANK1_VLV, inbuf=tank1_in, outbuf = tank1_out)
pipeline.add_task('pipeline-task', PERIOD, DURATION, FLOW_RATE, inbuf= pipe_in, outbuf = pipe_out)
tank2.add_task('tank2-task', PERIOD, DURATION, TANK2_LVL, inbuf= tank2_in)


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

#(pump_out, pump_err) = pump_proc.communicate()
(tank1_out, tank1_err) = tank1_proc.communicate()
#(pipe_out, pipe_err) = pipe_proc.communicate()
#(tank2_out, tank2_err) = tank2_proc.communicate()
(mtu_out, mtu_err) = mtu_proc.communicate()

#print pump_out
print tank1_out
print tank1_err
#print pipe_out
#print tank2_out
print mtu_out
print mtu_err

pump_proc.wait()
tank1_proc.wait()
pipe_proc.wait()
tank2_proc.wait()
mtu_proc.wait()
p.wait_end()
