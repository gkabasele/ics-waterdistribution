from pyics.utils import *

TS = "timestamp"

# Variable Name
A1 = "approvisioning1"
A2 = "approvisioning2"

V1 = "valve1"
V2 = "valve2"
T1 = "tank1"
MS1 = "motorSpeed1"
M1a = "motor1a"
M1 = "motor1"

VT1 = "valveTank1"

S1 = "silo1"
VS1 = "valveSilo1"

S2 = "silo2"
VS2 = "valveSilo2"
MS2 = "motorSpeed2"
M2a = "motor2a"
M2 = "motor2"

TC = "tankCharcoal"
VTC = "valveTankCharcoal"

WE = "wagonEnd"
WC = "wagonCar"
WM = "wagonMoving"
WO = "wagonlidOpen"
WS = "wagonStart"

TF = "tankFinal"
VTF = "valveTankFinal"

# Type

varmap = {
        
        A1  : (HR,1),             
        A2  : (HR,1), 
        V1  : (CO,1), 
        V2  : (CO,1), 
        T1  : (HR,1), 
        MS1 : (HR,1),
        M1  : (CO,1), 
        M1a : (CO,1),
        VT1 : (CO,1),
        S1  : (HR,1), 
        VS1 : (CO,1),
        S2  : (HR,1),
        VS2 : (CO,1),
        MS2 : (HR,1),
        M2  : (CO,1),         
        M2a : (CO,1),
        TC  : (HR,1),
        VTC : (CO,1),
        WE  : (CO,1), 
        WC  : (HR,1), 
        WM  : (CO,1),
        WO  : (CO,1),
        WS  : (CO,1), 
        TF  : (HR,1),
        VTF : (CO,1)
        }

# Limit value
limitmap = {
        A1  : [0, 500],             
        A2  : [0, 500], 
        V1  : [1, 2], 
        V2  : [1, 2], 
        T1  : [0, 40], 
        MS1 : [0, 10, 20], 
        M1  : [1, 2],
        M1a : [1, 2],
        VT1 : [1, 2],
        S1  : [0, 40], 
        VS1 : [1, 2],
        S2  : [0, 20, 60],
        VS2 : [1, 2],
        MS2 : [0, 10, 20],
        M2  : [1, 2],         
        M2a : [1, 2],         
        TC  : [0, 500],
        VTC : [1, 2],
        WE  : [1, 2], 
        WC  : [0, 20], 
        WM  : [1, 2],
        WO  : [1, 2],
        WS  : [1, 2], 
        TF  : [0, 60],
        VTF : [1, 2]
        }

# Action duration

quick_dur = 1
motor_dur = 3
flow_dur = 3
carcoal_dur = 4
carcoal_push_dur = 2 
wagon_moving_dur = 2
amount_fluid_passing = 20

# Store
STORE = './variables'
EXPORT_VAR ='./lplc_var'
PLCS_DIR = './plcs'
TEMPLATES_DIR = 'templates'
PLC_PERIOD = 0.05
MTU_PERIOD = 1
DURATION = 310 

LOG = "ics.log"
PLCS_LOG = "plcs_log"
