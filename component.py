import sys
import os
import redis
import math
import threading
import Queue
from simplekv.fs import FilesystemStore
from twisted.internet.task import LoopingCall
from twisted.internet import reactor
from utils import *

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
        self.task = None

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
        if self.inbuf and not self.inbuf.empty():
            item = self.inbuf.get()
            return item

    def write_buffer(self, item):
        if self.outbuf and not self.outbuf.full():
            self.outbuf.put(item)

    def run(self, period,*args):
        if self.task:
            task.start(period)
        else:
            self.task = LoopingCall(f=self.computation, arg=args)
            self.task.start(period)

    def stop(self):
        self.task.stop()

    def start(self,name, period, duration=None, *args):
        '''
            Start a periodic task by starting a thread
        '''
        self.task = PeriodicTask(name, period, self.computation, duration, *args) 
        print "Starting Component %s with task %s" % (self.name, name)
        self.task.start()


    def wait_end(self):    
        self.task.join()


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
        self.write_buffer(self.flow_out)





class Tank(Component):

    def __init__(self, name, inbuf, outbuf, store, height, diameter ,level, hole, valve = None):
        ''' Water Tank in a water distribution system system

            :param height: height of the tank (m) 
            :param diameter: diameter of the tank (m)
            :param level:  level of the water in the tank
            :param hole: diameter of the hole size in (m)
            :param valve: valve to open outlet placed on the tank 
        '''
        super(Tank, self).__init__(name, inbuf, outbuf, store)
        self.height = height
        self.diameter = diameter
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
            var_valve = None 
            if self.valve:
                var_valve = args[0][1]

            if var_valve:
                try:
                    self.valve = self.get(var_valve,bool)
                except KeyError:
                    self.set(var_valve, self.valve)
            
            flow_in = self.read_buffer()
            if not flow_in:
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

            self.write_buffer(flow_out)
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


