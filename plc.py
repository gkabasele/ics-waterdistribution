import sys
import time
from utils import *
from simplekv.fs import FilesystemStore
from pymodbus.server.sync import ModbusTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from twisted.internet.task import LoopingCall
from twisted.internet import reactor


class ProcessVariable(object):

    def __init__(self, _type, addr, size):

        self._type = _type
        self.addr = addr
        self.size = size

    def _type(self):
        return self._type
    
    def addr(self):
        return self.addr

    def size(self):
        return self.size

class PLC(object):

    def __init__(self, 
                 ip, 
                port,
                store,
                discrete_input,
                coils,
                holding_reg,
                input_reg,
                *kwargs):

        self.ip = ip   
        self.port = port
        self.store = FilesystemStore(store)
        (self.server, self.context) = self._init_modbus(ip, port, discrete_input, coils, holding_reg, input_reg)
        self.variables = {}
        self.setting_address(kwargs)
            
        self.index = {HR : 0, DI: 0, IR: 0, CO: 0}

    def setting_address(self, var):
        # { Name : type(di,hr, eg...), size: 10 }
        for k,v in var.iteritems():
            _type,size = v
            addr = index[_type]
            self.variables[k] = ProcessVariable(_type, addr, size)
            self.index[_type] += size

    def _init_modbus(self, ip, port, discrete_input, coils, holding_reg, input_reg):
        store = ModbusSlaveContext(
                di = ModbusSequentialDataBlock(0x00, [0]*discrete_input),
                co = ModbusSequentialDataBlock(0x00, [0]*coils),
                hr = ModbusSequentialDataBlock(0x00, [0]*holding_reg),
                ir = ModbusSequentialDataBlock(0x00, [0]*input_reg))

        context = ModbusServerContext(slaves=store, single=True)

        #Optional
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'MockPLCs'
        identity.ProductCode = 'MP'
        identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
        identity.ProductName = 'MockPLC 3000'
        identity.ModelName = 'MockPLC Ultimate'
        identity.MajorMinorRevision = '1.0'

        server = ModbusTcpServer(context, identity=identity , address=(ip, port))
        return server,context


    def set(self, name, value):
        var = self.variables[name]
        fx = registers_type[var.type()]
        context[0x0].setValues(fx, var.addr(), [value])

    def get(self, name):
        var = self.variables[name]
        fx = registers_type[var.type()]
        context[0x0].getValues(fx, var.addr(), count=var.size())[0]

    def add_variable(self, name, _type, size):
        addr = self.index[_type]
        self.variable[name] = ProcessVariable(_type, addr, size)

    def update_registers(self):
        for k,v in self.variables.iteritems():
            pass            

    def process_request(self, request, client):
        "update kv store"
        pass
    
    def run(self, period, duration):
        time = period
        loop = LoopingCall(f=update_registers, address=(self.context,))
        loop.start(time, now=False)
        self.server.serve_forever()
