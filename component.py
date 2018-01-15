import sys
import os
import redis
import math
import threading
import Queue
import logging
from simplekv.fs import FilesystemStore
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from utils import *

logging.basicConfig(filename='lphys.log', level=logging.DEBUG, mode= 'w')


class ComponentQueue(Queue.Queue, object):

    def __init__(self, size):
        '''Queue to pass physical element (water, oil...)

            :param in_comp: name of the producer component
            :param out_comp: name of the consummer component
        '''
        self.in_comp = None
        self.out_comp = None
        super(ComponentQueue, self).__init__(maxsize=size)

class Component(object):

    def __init__(self, store, name):

        '''Physical component of an industrial control system 

            :param  name: The name of the component
            :param  store: location of the store to set processes variables
        '''
        self.name = name
        self.inbufs = []
        self.outbufs = []
        self.store = FilesystemStore(store)
        self.tasks = {}

    def computation(self, *args, **kwargs):
        '''Computation done by the component

           :param  args: argument used by the component 
           :param  kwargs: key argument used by the component
        '''
        raise NotImplementedError

    def get(self, name, typeobj):
        '''Get value from actuators

           :param name: name of the process variable
           :param typeobj: type of the process variable
        '''
        return typeobj(self.store.get(name))

    def set(self, name, value):
        '''Set value to sensors
           
           :param name: name of the process variable
           :param value: value to set to the process variable 
        '''
        self.store.put(name, str(value))

    def get_inbuf(self, index):
        '''Return one of the input buffer
           :param index: index of the requested buffer
        '''
        return self.inbufs[index]

    def add_inbuf(self, inbuf):
        '''Add an input buffer to the component
           :param inbuf: input buffer to add 
        '''
        
        self.inbufs.append(inbuf)
        inbuf.out_comp = self.name
        return len(self.inbufs) - 1

    def add_outbuf(self, outbuf):
        '''Add an output buffer to the component
           :param outbuf: output buffer to add
        '''
        self.outbufs.append(outbuf)
        outbuf.in_comp = self.name
        return len(self.outbufs) - 1 

    def get_outbuf(self, index):
        ''' Return one of the output buffer
            :param index: index of the requested buffer
        '''
        return self.outbufs[index]

    def has_inbuf(self):
        '''Has the component an input buffer
        '''
        return len(self.inbufs) > 0

    def has_outbuf(self):
        '''Has the component an output buffer
        '''
        return len(self.outbufs) > 0

    def read_buffer(self, index, default=None ):
        inbuf = self.inbufs[index]
        if not inbuf.empty():
            item = inbuf.get()
            return item
        return default

    def write_buffer(self, item, index):
        outbuf = self.outbufs[index]
        if not outbuf.full():
            outbuf.put(item)

    def add_task(self,name, period, duration=None, *args, **kwargs):
        '''Start a periodic task by starting a thread

            :param name: name of the task
            :param period: period of the task
            :param duration: duration of the task, if None, does not stop
        '''
        self.tasks[name] = PeriodicTask(name, period, self.computation, duration, *args, **kwargs) 


    def start(self):
        '''Start all the task of the component
        '''
        s= "Starting Component %s with task: \n" % self.name
        for k,v in self.tasks.iteritems():
            s+= "\t%s\n" % k
            v.start()

        logging.info(s)

    def wait_end(self):    
        for v in self.tasks.itervalues():
           v.join()


class Pump(Component):
    def __init__(self,
                 store, 
                 flow_out, 
                 running, 
                 name='pump'): 
        ''' Pump in a water distribution system

            :param flow_out: volume of water outputed by the pump (m^3/s)
            :param running: is the pump running or not
        '''
        super(Pump, self).__init__(store, name)
        self.flow_out = flow_out
        self.running = running
        

    def computation(self, *args, **kwargs):
        '''
            - Check if running from actuators
            - Change flow_out accordingly
        '''
        var_running = args[0]
        index_out = kwargs.get(OUTBUF) 
        if index_out is None:
            logging.debug("No index provided for %s" % self.name)
            return 
        try:
            self.running = self.get(var_running, bool)
        except KeyError:
            self.set(var_running, self.running)    
            logging.debug("%s : Setting variable %s to %s" %(self.name, var_running, self.running))
        if not self.running:
            self.flow_out = 0
        self.write_buffer(self.flow_out, index_out)

class Tank(Component):

    def __init__(self, 
                 store,
                 height,
                 diameter,
                 hole,
                 level = 0,
                 valve = False,
                 name = 'tank'): 

        ''' Water Tank in a water distribution system system

            :param height: height of the tank (m) 
            :param diameter: diameter of the tank (m)
            :param level:  level of the water in the tank
            :param hole: diameter of the hole size in (m)
            :param valve: valve to open outlet placed on the tank 
        '''
        super(Tank, self).__init__(store, name)
        self.height = height
        self.diameter = diameter
        self.level = level
        self.hole = hole
        self.valve = valve

    def computation(self, *args, **kwargs):
            '''
                - compute output rate
                - change flow level
                - output flow rate
            '''
            '''
                Bernouilli equation  : a * sqrt(2*g*h)
                - a : size of the hole in the tank to output water (m^2)
                - h : level of water in the tank (m)
                - g : acceleration of gravity (9.8 m/s^2)
                Conservation of mass : flow_in - flow_out
            ''' 
            #FIXME check args
            var_level = args[0]

            index_in = kwargs.get(INBUF)
            index_out = kwargs.get(OUTBUF)
            if index_in is None and index_out is None:
                logging.debug("No index provided %s" % self.name)
                return

            var_valve = None 
            if self.valve:
                var_valve = args[1]

            if var_valve:
                try:
                    self.valve = self.get(var_valve,bool)
                except KeyError:
                    self.set(var_valve, self.valve)
                    logging.debug("%s: Setting %s to %s" % (self.name, var_valve, self.valve))
            
            if self.has_inbuf():
                logging.debug("reading buffer %s" % self.name)
                flow_in = self.read_buffer(index_in, 0)
            else:
                flow_in = 0
            # FIXME Verify Formula of water level rise
            
            self.level += (flow_in  / (math.pi * (self.diameter/2)**2))
            self.level = min(self.level, self.height) 

            if self.valve:
                flow_out = (math.pi * ((self.hole/2)**2 ) * math.sqrt(2*self.level*GRAVITY))
            else: 
                flow_out = 0

            self.level -= (flow_out /(math.pi * (self.diameter/2)**2)) 
            self.level = max(self.level, 0)

            if self.has_outbuf():
                self.write_buffer(flow_out, index_out)

            self.set(var_level, self.level)
            logging.debug("%s : Setting %s to %s" %(self.name, var_level, self.level))

class Valve(Component):
    def __init__(self, 
                 store, 
                 opened, 
                 name='valve'): 
        '''Valve in a water distribution system
            :param opened: is the valve open or not
        '''
        super(Valve, self).__init__(store, name)
        self.opened = opened

    def computation(self, *args, **kwargs):
        '''
            - check actuator from store
            - change status, open or not
        '''
        var_opened = args[0]
        
        try :
            self.opened = self.get(var_opened, bool)
        except KeyError:
            self.set(var_opened, self.opened)

class Pipeline(Component):
    def __init__(self, 
                 store, 
                 length,
                 diameter,
                 flow_rate = 0,
                 name='pipeline'): 

        '''Pipeline in a water distribution
            :param diameter:  size in m
            :param flow_rate: flow rate in the pipe in m^3/s
            :param length: length the pipe in meter
        '''
        super(Pipeline, self).__init__(store, name)
        self.diameter = diameter
        self.flow_rate = flow_rate
        self.length = length 


    def computation(self, *args, **kwargs):
        '''
            - compute out from in and diameter
            - compute flow rate 
        '''
        var_flow_rate = args[0]

        index_in = kwargs.get(INBUF)
        index_out = kwargs.get(OUTBUF)
        
        if index_in is None and index_out is None:
            logging.debug("no index provided %s" % self.name)
            return 

        self.flow_rate = self.read_buffer(index_in, self.flow_rate)

        self.set(var_flow_rate, self.flow_rate)
        logging.debug("%s: Setting %s to %s" % (self.name, var_flow_rate, self.flow_rate))
        self.write_buffer(self.flow_rate, index_out)


