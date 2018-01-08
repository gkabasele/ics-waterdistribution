from simplekv.fs import FilesystemStore
import os
import shutil
import signal
import subprocess
import time


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
if os.path.exists('./variables'):
    shutil.rmtree(STORE)

# CMD Variable
STR = '--storename'
IN = '--in_value'
OUT = '--out_value'
FR = '--flow_rate'
WTR = '--water_level'
VLV = '--valve_state'
PFL = '--pipe_fl'
RUN = '--running'


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

FLOW_RATE = "pipe_flow_rate"


# Running processes
py = ['/usr/bin/python']

# Creating command to run script for each component
#'pump.py --out_value %s --storename %s' % (PUMP_OUT, STORE)
pump_cmd = ['pump.py', OUT, PUMP_OUT, STR, STORE, RUN, PUMP_RUNNING]

tank1_cmd = ['tank1.py', IN, TANK1_IN, OUT, 
                TANK1_OUT, STR, STORE, WTR ,
                TANK1_LEVEL, VLV, TANK1_VALVE]

pipe_cmd = ['pipeline.py', IN, PIPE_IN, OUT, 
            PIPE_OUT, STR, STORE, 
            PFL, FLOW_RATE]

tank2_cmd = ['tank2.py', IN, TANK2_IN, STR,
                STORE, WTR, TANK2_LEVEL]

pump_proc = subprocess.Popen(py + pump_cmd)
time.sleep(1)
tank1_proc = subprocess.Popen(py + tank1_cmd)
time.sleep(1)
pipe_proc = subprocess.Popen(py + pipe_cmd)
time.sleep(1)
tank2_proc = subprocess.Popen(py + tank2_cmd)
time.sleep(1)
