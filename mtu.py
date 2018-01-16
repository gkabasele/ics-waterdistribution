import logging
import math

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.client.sync import ConnectionException
from plc import ProcessVariable, PLC
from utils import *

class ProcessRange(object):

    def __init__(self, high, low, fh=None, fl=None):
        self.high = high
        self.low = low
        if fh is not None and fl is not None:
            self.action = (fh,fl)

    def execute_action(self, value, *args, **kwargs):
        if value < low:
            self.action[1](args, kwargs)
        elif value > high:
            self.action[0](args, kwargs)

    def add_action(self, fh, fl):
        self.action = f

class MTU(object):

    def __init__(self,
                 ip,
                 port,
                 client=ModbusTcpClient):

        # Keeping track of information of the variable, name : type,addr,size
        self.variables = {}
        # Keeping track of PLC storing the variable, name : plc
        self.plcs = {}
        # Keeping track of the 
        self.cond = {}

        # (ip,port) to modbus client
        self.clients = {}

        self.ip = ip
        self.port = port
        self.client_class = client
        self.task = None

    def import_variables(self, filename):
        hist = set()
        f = open(filename, 'r')
        for line in f:
            l = line.split(':')
            ip, port = tuple(l[0].split(','))
            name = l[1] 
            _type,addr,size = tuple(line.split(':')[2].split(','))

            if (ip,port) not in hist:
                self.add_plc(ip, port, name, ProcessVariable(_type, addr, size))
                hist.add((ip,port))
            else:
                self.add_plc(ip, port, name, ProcessVariable(_type, addr,size), False)
        f.close()
             

    def add_plc(self, plc_ip, plc_port, name, process_variable, create_client=True):

        try:
            if create_client:
                client = self.client_class(host=plc_ip, port=plc_port, source_address(self.ip, self.port))            
                self.clients[(ip,port)] = client 
                self.port += 1
            else:
                client = self.clients[(plc_ip, plc_port)]

            self.variables[name] = process_variable
            self.plcs[name] = client

        except ConnectionException:
            print "Unable to connect to Modbus Server %s:%d" %(plc_ip, plc_port)

    def add_cond(self, name, high, low, fh=None, fl=None):
        self.cond[name] = ProcessRange(high, low, fh, fl)

    def create_task(self, name, period, duration=None, *args, **kwargs):
        self.task = PeriodicTask(name, period, self.main_loop, duration, *args, **kwargs) 

    #TODO add other function
    def get_variable(self, name):
        var = self.variables[name]
        res = None
        if var.get_type() == CO :
            res = self.plcs[name].read_coils(var.get_addr(),var.get_size())[0]  
        elif var.get_type() == HR:
            res = self.plcs[name].read_holding_registers(var.get_addr(), var.get_size())[0]
        return res

    def write_variable(self, name, value):
        var = self.variables[name]
        if var.get_type == CO : 
            self.plcs[name].write_coil(var.get_addr(), value)
        elif var.get_type() == HR:
            self.plcs[name].write_register(var.get_addr(), value)
        
    def start(self):
        self.task.start()
    
    def wait_end(self):
        self.task.join()

    def main_loop(self, *args, **kwargs):
        raise NotImplementedError
    

class WaterDistribution(MTU):

    PUMP_RNG = "pump_running"
    TANK1_LVL = "tank1_level"
    TANK1_VLV = "tank1_valve"
    FLOW_RATE = "flow_rate"
    TANK2_LVL = "tank2_level"


    def main_loop(self, *args, **kwargs):
        pump = self.get_variable(PUMP_RNG)
        t1_lvl = self.get_variable(TANK1_LVL)
        t1_vlv = self.get_variable(TANK1_VLV)
        flow_rate = self.get_variable(FLOW_RATE)
        t2_lvl = self.get_variable(TANK2_LVL)

        print "Pump: ", pump
        print "Level Tank1: ", t1_lvl
        print "Valve Tank1: ", t1_vlv
        print "Flow rate: ", flow_rate
        print "Level Tank2: ", t2_lvl

        cond_t1 = self.cond[TANK1_LVL]
        cond_flow_rate = self.cond[FLOW_RATE]
        cond_t2 = self.cond[TANK2_LVL]

        cond_t1.execute_action()
        cond_flow_rate.execute_action()
        cond_t2 = self.execute_action()

    def close_valve(self):
        self.write_variable(TANK1_VLV, False)

    def open_valve(self):
        self.write_variable(TANK1_LVL, True)


