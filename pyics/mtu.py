import logging
import math
import os
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.client.sync import ConnectionException
from pymodbus.exceptions import ModbusIOException
from plc import ProcessVariable, PLC
from utils import *

logger = logging.getLogger(__name__)

class ProcessRange(object):

    def __init__(self, low, high, fl=None, fh=None):
        self.high = high
        self.low = low
        if fl is not None and fh is not None:
            self.action = (fl,fh)

    def execute_action(self, value, *args, **kwargs):
        if value < self.low:
            self.action[0](*args, **kwargs)
        elif value > self.high:
            self.action[1](*args, **kwargs)

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

    def get_dir(self, dirname):
        for filename in os.listdir(dirname):
            self.import_variables(dirname+"/"+filename)


    def import_variables(self, filename):
        hist = set()
        f = open(filename, 'r')
        for line in f:
            l = line.split(':')
            ip, sport = tuple(l[0].split(','))
            port = int(sport)
            name = l[1] 
            _type,addr,size = tuple(line.split(':')[2].split(','))


            if (ip,port) not in hist:
                if self.add_plc(ip, port, name, ProcessVariable(_type, int(addr), int(size))):
                    hist.add((ip,port))
            else:
                self.add_plc(ip, port, name, ProcessVariable(_type, int(addr),int(size)), False)
        f.close()
             

    def add_plc(self, plc_ip, plc_port, name, process_variable, create_client=True):
        try:
            if create_client:
                client = self.client_class(host=plc_ip,port=plc_port, source_address=(self.ip, self.port))
                if client.connect():
                    self.clients[(plc_ip,plc_port)] = client 
                    self.port += 1
                else: 
                    logger.info("Could not connect the server %s:%s" % (plc_ip, plc_port))
                    print "Could not connect to the server %s:%s" % (plc_ip, plc_port)
            else:
                client = self.clients[(plc_ip, plc_port)]
            
            if client.socket:
                logger.info("Adding variable %s at PLC(%s:%d)" % (name, plc_ip, plc_port))
                self.variables[name] = process_variable
                self.plcs[name] = client
                return True
        except ConnectionException:
            logger.error("Unable to connect to Modbus server %s:%s" % (plc_ip, plc_port))
            print "Unable to connect to Modbus server %s:%s" % (plc_ip, plc_port)

    def add_cond(self, name, low, high, fl=None, fh=None):
        self.cond[name] = ProcessRange(low, high, fl, fh)

    def create_task(self, name, period, duration=None, *args, **kwargs):
        self.task = PeriodicTask(name, period, self.main_loop, duration, *args, **kwargs) 

    #TODO add other function
    def get_variable(self, name):
        try:
            var = self.variables[name]
            res = None
            type_ = var.get_type()
            if type_ == CO :
                res = self.plcs[name].read_coils(var.get_addr(),var.get_size()).bits[0]  
            elif type_ == HR:
                res = self.plcs[name].read_holding_registers(var.get_addr(), var.get_size()).registers[0]
            elif type_ == IR:
                res = self.plcs[name].read_input_registers(var.get_addr(), var.get_size()).registers[0]
            elif type_ == DI:
                res = self.plcs[name].read_discrete_inputs(var.get_addr(), var.get_size()).bits[0]

            return res

        except ConnectionException:
            logger.error("Unable to read value %s from Modbus" % (name))
            print "Unable to read value %s from Modbus" % (name)
        except AttributeError:
            if type(res) is ModbusIOException:
                logger.error("ModbusIOException: %s " % name )
                print res.message
        except KeyError:
            logger.error("Variable name: %s does not exist"% (name))
            print "Variable name: %s does not exist"% (name)

    def write_variable(self, name, value):
        try:
            var = self.variables[name]
            if var.get_type() == CO : 
                self.plcs[name].write_coil(var.get_addr(), value)
            elif var.get_type() == HR:
                self.plcs[name].write_register(var.get_addr(), value)
            else:
                print "Invalid variable type"
        except ConnectionException:
            logger.error("Unable to write value %s to %s" %(value, name ))
            print "Unable to write value %s to %s" %(value, name)
        except KeyError:
            logger.error("Variable name: %s does not exist" % (name))
            print "Variable name: %s does not exist" % name

    def start(self):
        self.task.start()
    
    def wait_end(self):
        self.task.join()

    def close(self):
        for v in self.clients.itervalues():
            v.close()

    def main_loop(self, *args, **kwargs):
        raise NotImplementedError
    

#class WaterDistribution(MTU):
#
#    def __init__(self, ip, port, client=ModbusTcpClient):
#        
#        self.pump = False
#        self.t1_lvl = 0
#        self.t1_vlv = False
#        self.pipeline = 0
#        self.t2_lvl = 0
#        super(WaterDistribution, self).__init__(ip, port, client)
#
#
#    def main_loop(self, *args, **kwargs):
#
#        self.pump = self.get_variable(PUMP_RNG)
#        self.t1_lvl = self.get_variable(TANK1_LVL)
#        self.t1_vlv = self.get_variable(TANK1_VLV)
#        self.flow_rate = self.get_variable(FLOW_RATE)
#        self.t2_lvl = self.get_variable(TANK2_LVL)
#
#        print "Pump: %s,T1_LVL: %s, T1_VLV: %s, FR: %s, T2_LVL: %s" % (self.pump, self.t1_lvl, self.t1_vlv, self.flow_rate, self.t2_lvl) 
#
#        if self.t1_lvl is not None:
#            cond_t1 = self.cond[TANK1_LVL]
#            cond_t1.execute_action(self.t1_lvl)
#        if self.flow_rate is not None:
#            cond_flow_rate = self.cond[FLOW_RATE]
#            cond_flow_rate.execute_action(self.flow_rate)
#        if self.t2_lvl is not None:
#            cond_t2 = self.cond[TANK2_LVL]
#            cond_t2.execute_action(self.t2_lvl)
#
#    def close_valve(self, *args, **kwargs):
#        if self.t1_vlv:
#            self.write_variable(TANK1_VLV, False)
#
#    def open_valve(self, *args, **kwargs):
#        if not self.t1_vlv:
#            self.write_variable(TANK1_VLV, True)


