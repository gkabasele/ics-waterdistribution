import sys
import time
import Queue
import logging
from utils import *
from simplekv.fs import FilesystemStore
from pymodbus.server.sync import ModbusTcpServer, ModbusConnectedRequestHandler
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.factory import ServerDecoder

from twisted.internet.task import LoopingCall
from twisted.internet import reactor

logging.basicConfig(filename='lplc.log', level=logging.DEBUG, mode='w')

class ProcessVariable(object):

    def __init__(self, _type, addr, size):

        self._type = _type
        self.addr = addr
        self.size = size

    def get_type(self):
        return self._type
    
    def get_addr(self):
        return self.addr

    def get_size(self):
        return self.size

    def __str__(self):
        return "(%s, %s, %s)" % (self._type, self.addr, self.size)


class KVModbusRequestHandler(ModbusConnectedRequestHandler):

    def execute(self, request):
        ''' The callback to call with the resulting message

        :param request: the decoded request message
        '''
        try:
            context = self.server.context[request.unit_id]
            response = request.execute(context)
            # updating actuator 
            #check if its a write request
            if utils.first_true(ServerDecoder._function_table[4,7], None, lambda x: isinstance(x,request)):  
                self.update_actuator(request.address, request.value)

        except NoSuchSlaveException as ex:
            _logger.debug("requested slave does not exist: %s" % request.unit_id )
            if self.server.ignore_missing_slaves:
                return
            response = request.doException(merror.GatewayNoResponse)
        except Exception as Ex:
            _logger.debug("Datastore unable to fulfill request: %s; %s", ex, traceback.format_exc())
            response = request.doException(merror.SlaveFailure)
        response.transaction_id = request.transaction_id
        response.unit_id = request.unit_id
        self.send(response)

    def update_actuator(self, addr, value):
        try:
            name =  self.server.addr_to_var[addr]
            self.server.store.put(name, value)  
        except KeyError:
            print "Variable %s doest not exist" % name
        

class PLC(ModbusTcpServer, object):

    def __init__(self, 
                 ip, 
                port,
                store,
                discrete_input,
                coils,
                holding_reg,
                input_reg,
                **kwargs):

        self.store = FilesystemStore(store)
        (context, identity) =  self._init_modbus(ip, port, discrete_input, coils, holding_reg, input_reg)
        self.context = context
        self.variables = {}
        self.addr_to_var = {}
        self.index = {HR : 0, DI: 0, IR: 0, CO: 0}
        self.setting_address(kwargs)
        self.loop = None
        super(PLC, self).__init__(context, identity=identity, address=(ip, port), handler = KVModbusRequestHandler)


    def setting_address(self, var):
        # { Name : type(di,hr, eg...), size: 10 }
        for k,v in var.iteritems():
            _type,size = v
            addr = self.index[_type]
            self.variables[k] = ProcessVariable(_type, addr, size)
            self.addr_to_var[addr] = k
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

        return context,identity


    def set(self, name, value):
        var = self.variables[name]
        fx = registers_type[var.get_type()]
        self.context[0x0].setValues(fx, var.get_addr(), [value])

    def get(self, name):
        var = self.variables[name]
        fx = registers_type[var.get_type()]
        return self.context[0x0].getValues(fx, var.get_addr(), count=var.get_size())

    def put_store(self, name, value):
        self.store.put(name, str(value))


    def get_store(self, name, typeobj, default=None):
        try:
            item = typeobj(self.store.get(name))
            logging.debug("Item: %s" % item)
            return item
        except KeyError:
            item = default
        except ValueError:
            logging.debug("Item Error: %s " % self.store.get(name)) 

    def add_variable(self, name, _type, size):
        addr = self.index[_type]
        self.variable[name] = ProcessVariable(_type, addr, size)
        self.addr_to_var[addr] = name


    def update_registers(self, *args,**kwargs):
        for k,v in self.variables.iteritems():
            if v.get_type() == CO:
                val = int(self.get_store(k,bool))           
            else:
                val = self.get_store(k, float)
            if val:
                self.set(k,val)

    def run(self, name, period, duration=None, *args, **kwargs):
        self.loop = PeriodicTask(name, period, self.update_registers, duration, *args, **kwargs)
        self.loop.start()

    def wait_end(self, server=False):
        if server:
            self.serve_forever()
        self.loop.join()
