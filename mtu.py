import logging
import math
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.client.sync import ConnectionException
from pymodbus.exceptions import ModbusIOException
from plc import ProcessVariable, PLC
from utils import *

logger = logging.getLogger(__name__)

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

class ModbusTcpClientThread(threading.Thread):

    def __init__(self, name, client):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        pass

class MTU(object):

    def __init__(self,
                 ip,
                 port,
                 client=ModbusTcpClient):

        # Keeping track of information of the variable, name : type,addr,size
        self.variables = {}
        # Keeping track of PLC storing the variable, name : plc
        self.plcs = {}
        # Keeping track of the condition for a variable
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
                self.add_plc(ip, int(port), name, ProcessVariable(_type, int(addr), int(size)))
                hist.add((ip,port))
            else:
                self.add_plc(ip, int(port), name, ProcessVariable(_type, int(addr),int(size)), False)
        f.close()
             

    def add_plc(self, plc_ip, plc_port, name, process_variable, create_client=True):

        try:
            if create_client:
                client = self.client_class(host=plc_ip, port=plc_port, source_address=(self.ip, self.port))            
                if client.connect():
                    self.clients[(plc_ip,plc_port)] = client 
                    self.port += 1
            else:
                client = self.clients[(plc_ip, plc_port)]
            
            if client.socket:
                logger.info("Adding variable %s at PLC(%s:%d)" % (name, plc_ip, plc_port))
                self.variables[name] = process_variable
                self.plcs[name] = client

        except ConnectionException:
            logger.error("Unable to connect to Modbus server %s:%d" % (plc_ip, plc_port))

    def add_cond(self, name, high, low, fh=None, fl=None):
        self.cond[name] = ProcessRange(high, low, fh, fl)

    def create_task(self, name, period, duration=None, *args, **kwargs):
        self.task = PeriodicTask(name, period, self.main_loop, duration, *args, **kwargs) 

    #TODO add other function
    def get_variable(self, name):
        var = self.variables[name]
        try:
            res = None
            if var.get_type() == CO :
                res = self.plcs[name].read_coils(var.get_addr(),var.get_size()).bits[0]  
            elif var.get_type() == HR:
                res = self.plcs[name].read_holding_registers(var.get_addr(), var.get_size()).registers[0]
            elif var.get_type() == IR:
                res = self.plcs[name].read_input_registers(var.get_addr(), var.get_size()).registers[0]
            elif var.get_type() == DI:
                res = self.plcs[name].read_discrete_inputs(var.get_addr(), var.get_size()).bits[0]
            return res
        except ConnectionException:
            logger.error("Unable to read value %s from Modbus" % (name))
        except ModbusIOException:
            logger.error("ModbusIOException: %s " % name )

    def write_variable(self, name, value):
        var = self.variables[name]
        try:
            if var.get_type == CO : 
                self.plcs[name].write_coil(var.get_addr(), value)
            elif var.get_type() == HR:
                self.plcs[name].write_register(var.get_addr(), value)
        except ConnectionException:
            logger.error("Unable to write value %s from %s:%d" %(name))

    def start(self):
        self.task.start()
    
    def wait_end(self):
        self.task.join()

    def close(self):
        for v in self.clients.itervalues():
            v.close()

    def main_loop(self, *args, **kwargs):
        raise NotImplementedError
    

class WaterDistribution(MTU):

    # FIXME put all in a list
    PUMP_RNG = "pump_running"
    TANK1_LVL = "tank1_level"
    TANK1_VLV = "tank1_valve"
    FLOW_RATE = "flow_rate"
    TANK2_LVL = "tank2_level"


    def main_loop(self, *args, **kwargs):

        pump = self.get_variable(self.PUMP_RNG)
        print "Pump: ", pump

        t1_lvl = self.get_variable(self.TANK1_LVL)
        print "Level Tank1: ", t1_lvl

        t1_vlv = self.get_variable(self.TANK1_VLV)
        print "Valve Tank1: ", t1_vlv
        
        flow_rate = self.get_variable(self.FLOW_RATE)
        print "Flow rate: ", flow_rate

        t2_lvl = self.get_variable(self.TANK2_LVL)
        print "Level Tank2: ", t2_lvl
        print "\n"

        if t1_lvl is not None:
            cond_t1 = self.cond[self.TANK1_LVL]
            cond_t1.execute_action()
        if flow_rate is not None:
            cond_flow_rate = self.cond[self.FLOW_RATE]
            cond_flow_rate.execute_action()
        if t2_lvl is not None:
            cond_t2 = self.cond[self.TANK2_LVL]
            cond_t2.execute_action()

    def close_valve(self):
        self.write_variable(TANK1_VLV, False)

    def open_valve(self):
        self.write_variable(TANK1_LVL, True)


