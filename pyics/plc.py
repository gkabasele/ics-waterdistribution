import logging
import traceback
import time
from utils import CO, HR, DI, IR, registers_type, PeriodicTask
from simplekv.fs import FilesystemStore
from pymodbus.server.sync import ModbusTcpServer, ModbusConnectedRequestHandler
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.exceptions import NoSuchSlaveException
from pymodbus.pdu import ModbusExceptions as merror
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


logger = logging.getLogger(__name__)


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
        ''' Callback when receiving a request, potentially update actuators

        :param request: the decoded request message

        :return:
        '''
        try:
            logger.debug("Received request")
            context = self.server.context[request.unit_id]
            response = request.execute(context)
            # check if its a write request
            if request.function_code in [5, 6, 15, 16]:
                is_coil = ((request.function_code % 5) == 0)
                self.update_actuator(request.address, request.value, is_coil)

        except NoSuchSlaveException as ex:
            logger.debug("requested slave does not exist: %s" % request.unit_id)
            if self.server.ignore_missing_slaves:
                return
            response = request.doException(merror.GatewayNoResponse)
        except Exception as ex:
            logger.debug("Datastore unable to fulfill request: %s; %s", ex, traceback.format_exc())
            response = request.doException(merror.SlaveFailure)

        response.transaction_id = request.transaction_id
        response.unit_id = request.unit_id
        self.send(response)

    def update_actuator(self, addr, value, is_coil):
        try:
            type_ = CO if is_coil else HR
            name = self.server.addr_to_var[type_][addr]
            self.server.put_store(name, value)
        except KeyError:
            logger.debug("Variable %s doest not exist" % name)

class VarPLCHandler(FileSystemEventHandler):

    '''
        Class to observe modification on process variable store
    '''
    
    def __init__(self, plc):

        self.plc = plc
        super(VarPLCHandler, self).__init__()

    def on_modified(self, event):
        varname = str(event.src_path).replace(self.plc.store.root + '/', '').encode('utf-8')
        logger.info("Modification of varname: %s" %varname )
        if varname in self.variables:
            logger.info("Updating variables for PLC %s" %self.plc.name)
            self.plc.update_registers()



class PLC(ModbusTcpServer, object):

    def __init__(self,
                 ip,
                 port,
                 store,
                 name,
                 discrete_input=1,
                 coils=1,
                 holding_reg=1,
                 input_reg=1,
                 handler=KVModbusRequestHandler,
                 **kwargs):

        self.store = FilesystemStore(store)
        (context, identity) = self._init_modbus(ip, port, discrete_input, coils, holding_reg, input_reg)
        self.context = context
        self.variables = {}
        self.addr_to_var = {HR: {}, DI: {}, IR: {}, CO: {}}
        self.index = {HR: 0, DI: 0, IR: 0, CO: 0}
        self.setting_address(kwargs)
        self.loop = None
        self.ip = ip
        self.port = port
        self.name = name
        self.duration = None
        logger.info("Creating a PLC server %s:%d" % (ip, port))
        super(PLC, self).__init__(context, identity=identity, address=(ip, port), handler=handler)

    def setting_address(self, var):
        # { Name : type(di,hr, eg...), size: 10 }
        for k, v in var.iteritems():
            _type, size = v
            addr = self.index[_type]
            self.variables[k] = ProcessVariable(_type, addr, size)
            self.addr_to_var[_type][addr] = k
            self.index[_type] += size

    def _init_modbus(self, ip, port, discrete_input, coils, holding_reg, input_reg):
        store = ModbusSlaveContext(
                di=ModbusSequentialDataBlock(0x00, [0]*discrete_input),
                co=ModbusSequentialDataBlock(0x00, [0]*coils),
                hr=ModbusSequentialDataBlock(0x00, [0]*holding_reg),
                ir=ModbusSequentialDataBlock(0x00, [0]*input_reg))

        context = ModbusServerContext(slaves=store, single=True)

        # Optional
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'MockPLCs'
        identity.ProductCode = 'MP'
        identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
        identity.ProductName = 'MockPLC 3000'
        identity.ModelName = 'MockPLC Ultimate'
        identity.MajorMinorRevision = '1.0'

        return context, identity

    def set(self, name, value):
        ''' Setting a process variable to the value

            :param name: Name of the process variable
            :param value: Value to set to the process variable
        '''
        var = self.variables[name]
        fx = registers_type[var.get_type()]
        self.context[0x0].setValues(fx, var.get_addr(), [value])

    def get(self, name):
        ''' Getting value of a process variable

            :param name: Name of the process variable

            :return: Value of the process variable
        '''
        var = self.variables[name]
        fx = registers_type[var.get_type()]
        return self.context[0x0].getValues(fx, var.get_addr(), count=var.get_size())

    def put_store(self, name, value):
        ''' Setting value to one of the actuator

            :param name: name of the actuator
            :param value: value to put to the actuator

        '''
        self.store.put(name, str(value))

    def export_variables(self, filename):
        '''Export mapping between variable and their address

           :param filename: name of the time to export the variables

           :return:

        '''
        f = open(filename+'/'+self.name+'.ex', 'w')
        logger.info("Exporting variable to {}".format(filename + "/" + self.name + ".ex"))
        for k, v in self.variables.iteritems():
            f.write("%s,%s:%s:%s,%s,%s\n" % (self.ip, self.port, k, v.get_type(), v.get_addr(), v.get_size()))
        f.close()

    def get_store(self, name, typeobj, default=None):
        ''' Getting value from one of the sensor

            :param name: name of the sensor
            :param typeobj: type of the value to get

            :return: value from the sensor if possible
        '''
        try:
            if typeobj == "b":
                item = self.store.get(name)
                if item == "True" or item == "False":
                    return item == "True"
                else:
                    raise TypeError
            else:
                item = typeobj(self.store.get(name))
                return item
        except KeyError:
            logger.error("Item KeyError: %s " % name)
            return default
        except ValueError:
            logger.error("Item Error: %s " % self.store.get(name))

    def add_variable(self, name, _type, size):
        ''' Add a process variable to the PLC

            :param name: name of the process variable
            :param _type: type of store for the process variable (coil, input register, ...)
            :param size: size needed to store the process variable

            :return:
        '''
        addr = self.index[_type]
        self.variable[name] = ProcessVariable(_type, addr, size)
        self.addr_to_var[addr] = name

    def update_registers(self, *args, **kwargs):
        ''' Update variable according to the sensor
            :return:
        '''
        logger.info("Attempting registers update")
        for k, v in self.variables.iteritems():
            if v.get_type() == CO:
                val = int(self.get_store(k, 'b'))
            else:
                val = self.get_store(k, float, 0)
            if val is not None:
                logger.info("Updating registers")
                self.set(k, val)

    def run(self, name, period, duration=None, *args, **kwargs):
        ''' Start the processing of the PLC, in a periodic fashion

            :param name: name of the task
            :param period: perform the task every period
            :param duration: duration of the task, the task is performed duration/period times
            :return:
        '''
        self.loop = PeriodicTask(name, period, self.update_registers, logger=logger, duration=duration,
                                 end=self.shutdown, *args, **kwargs)
        self.duration = duration
        self.loop.start()

    def wait_end(self, server=False):
        if server:
            if self.duration is None:
                self.serve_forever()
            else:
                current_time = time.time()
                end_time = current_time + self.duration

                while current_time <= end_time:
                    self.handle_request()
        self.loop.join()

    def stop(self):
        self.shutdown()
        self.stop()
