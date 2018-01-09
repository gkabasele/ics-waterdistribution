import sys
import os
import redis
import math
from utils import PeriodicTask
import threading
from simplekv.fs import FilesystemStore
from twisted.internet.task import LoopingCall
from twisted.internet import reactor

class ComponentQueue(Queue):

    def __init__(self, size):
        '''Queue to pass physical element (water, oil...)

            :param in_comp: name of the producer component
            :param out_comp: name of the consummer component
        '''
        self.in_comp = None
        self.out_comp = None
        super(ComponentQueue, self).__init__(maxsize=0)

class Component(thrading.Thread):

    def __init__(self, name, inbuf, outbuf, store):
        '''Physical component of an industrial control system 

            :param  name: The name of the component
            :param  inbuf: Buffer to retrieve value
            :param  outbuf:  Buffer to set value
            :param  store: location of the store to set processes variables
        '''
        self.name = name
        self.inbuf = inbuf
        if inbuf:
            inbuf.out_comp = name
        self.outbuf = outbuf
        if outbuf:
            outbuf.in_comp = name
        self.store = FilesystemStore(store)

    def set_inbuf(self, inbuf):
        self.inbuf = inbuf
        inbuf.out_comp = self.name

    def set_outbuf(self, outbuf):
        self.outbuf = outbuf
        outbuf.in_comp = self.name

    def computation(self, *args):
        '''Computation done by the component

           :param  args: argument used by the component 
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

    def read_buffer(self):
        if not self.inbuf.empty():
            item = self.inbuf.get()

    def write_buffer(self, item):
        if not self.outbuf.full():
            item = self.outbuf.put(item)

    def start(self,name, period, duration, *args):
        '''
            Start a periodic task by starting a thread
        '''
        task = PeriodicTask(name, period, duration ,self.computation, *args) 
        print "Starting Component %s with task %s" % (self.name, name)
        task.start()
        task.join()


class Pump(Component):
    def __init__(self, name, inbuf, outbuf, store, flow_out, running):
        ''' Pump in a water distribution system

            :param flow_out: volume of water outputed by the pump (m^3/s)
            :param running: is the pump running or not
        '''
        super(Pump, self).__init__(name, inbuf, outbuf, store)
        self.flow_out = flow_out
        self.running = running
        

    def computation(self, *args):
        '''
            - Check if running from actuators
            - Change flow_out accordingly
        '''
        var_running = args[0][0]
        try:
            self.running = self.get(var_running, bool)
        except KeyError:
            self.set(var_running, self.running)    
        if not self.running:
            self.flow_out = 0
        #else :
        #    self.flow_out = self.get(*args)
        self.write_buffer(self.flow_out)





class Tank(Component):

    def __init__(self, name, inbuf, outbuf, store, height, radius ,level, hole, valve = None):
        ''' Water Tank in a water distribution system system

            :param height: height of the tank (m) 
            :param radius: radius of the tank (m)
            :param level:  level of the water in the tank
            :param hole: hole size in (m)
            :param valve: valve to open outlet placed on the tank 
        '''
        super(Tank, self).__init__(name, inbuf, outbuf, store)
        self.height = height
        self.radius = radius
        self.level = level
        self.hole = hole
        self.valve = valve


    def computation(self, *args):
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
            var_level = args[0][0]
            var_valve = args[0][1]

            if var_valve:
                try:
                    self.valve = self.get(var_valve,bool)
                except KeyError:
                    self.set(var_valve, self.valve)

            if self.valve:
                flow_out = (math.pi * (self.hole**2 ) * math.sqrt(2*self.level*GRAVITY))
            else: 
                flow_out = 0

            flow_in = self.inbuf.read_buffer()
            if not flow_in:
                flow_in = 0
            # FIXME change right formula
            rise = flow_out  - flow_in
            self.level = self.level - rise
            if self.level >= 0 :
                self.level = min(self.level, self.height) 
            else:
                self.level = 0 

            if self.outbuf != "":
                self.set(self.outbuf, flow_out)
            self.set(var_level, self.level)

class Valve(Component):
    def __init__(self, name, inbuf, outbuf, store, opened):
        '''Valve in a water distribution system
            :param opened: is the valve open or not
        '''
        super(Valve, self).__init__(name, inbuf, outbuf, store)
        self.opened = opened

    def computation(self, *args):
        '''
            - check actuator from store
            - change status, open or not
        '''
        var_opened = args[0][0]
        try :
            self.opened = self.get(var_opened, bool)
        except KeyError:
            self.set(var_opened, self.opened)

class Pipeline(Component):
    def __init__(self, name, inbuf, outbuf, store, flow_rate, length=None, diameter=None):
        '''Pipeline in a water distribution
            :param diameter:  size in m
            :param flow_rate: flow rate in the pipe in m^3/s
            :param length: length the pipe in meter
        '''
        super(Pipeline, self).__init__(name, inbuf, outbuf, store)
        self.diameter = diameter
        self.flow_rate = flow_rate
        self.length = length 

    def computation(self, *args):
        '''
            - compute out from in and diameter
            - compute flow rate 
        '''
        var_flow_rate = args[0][0]
        self.flow_rate = self.read_buffer()

        self.set(var_flow_rate, self.flow_rate)
        self.write_buffer(self.flow_rate)


