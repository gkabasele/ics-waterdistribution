from simplekv.fs import FilesystemStore
import os
import signal
import subprocess


STORE = './variables'



'''
+-----------+
|  PUMP     |
+-----------+
        ||
    +---------------+                                   +---------------+ 
    |               |                                   |               |
    |  TANK 1       |                                   | TANK 2        |
    |               |-----------------------------------|               |
    |               |               PIPE                |               |
    |               |-----------------------------------|               |
    |               |                                   |               |
    |               |                                   |               |
    |               |                                   |               |
    +-------------- +                                   +-------------- +





'''

# CMD Variable
STR = '--storename'
IN = '--in_value'
OUT = '--out_value'
FR = '--flow_rate'


# Flow circuit
PUMP_OUT = "pump_out"
TANK1_IN = PUMP_OUT

TANK1_OUT = "tank1_out"
PIPE_IN =  TANK1_OUT

PIPE_OUT = "pipe_out" 
TANK2_IN = PIPE_OUT

# Process Variable
PUMP_RUNNING = "pump_running"

TANK1_LEVEL = "tank1_level"
TANK2_LEVEL = "tank2_level"

TANK1_VALVE = "tank1_valve"
TANK2_VALVE = "tank2_valve"

FLOW_RATE = "pipe_flow_rate"


# Running processes
py = ['/usr/bin/python']

# Creating command to run script for each component
#'pump.py --out_value %s --storename %s' % (PUMP_OUT, STORE)
pump_cmd = ['pump.py', OUT, PUMP_OUT, STR, STORE]

tank1_cmd = ['tank1.py', IN, TANK1_IN, OUT, 
                TANK1_OUT, STR, STORE, 'water_level',
                TANK1_LEVEL, 'valve_state', TANK1_VALVE]

pipe_cmd = ['pipeline.py', IN, PIPE_IN, OUT, 
            PIPE_OUT, STR, STORE, 
            FR, FLOW_RATE]

tank2_cmd = ['tank2.py', IN, TANK2_IN, STR, STORE, 'water_level']

print "Creating Pump Process \n"
pump_proc = subprocess.Popen(py + pump_cmd)
tank1_proc = subprocess.Popen(py + tank1_cmd)
print "Creating Pipe Process \n"
pipe_proc = subprocess.Popen(py + pipe_cmd)
tank2_proc = subprocess.Popen(py + tank2_cmd)
