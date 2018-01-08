import sys
import os
import redis
import math
from utils import PeriodicTask
from simplekv.fs import FilesystemStore
GRAVITY = 9.8

class Component(object):

    def __init__(self, name, in_value, out_value, store):
        '''
            Physical component of an industrial control system 
            - name : name of the component
            - in_value : key where to get value 
            - out_value : key where to set value 
        '''
        self.name = name
        self.in_value = in_value
        self.out_value = out_value
        self.store = FilesystemStore(store)

    def computation(self, *args):
        '''
            Computation done by the component 
        '''
        print "This method must be overriden"

    def get(self, name, typeobj):
        '''
            Get value from actuators
        '''
        return typeobj(self.store.get(name))

    def set(self, name, value):
        '''
            Set value to sensors
        '''
        self.store.put(name, str(value))

    def start(self,name, period, duration, *args):
        '''
            Start a periodic task by starting a thread
        '''
        task = PeriodicTask(name, period, duration ,self.computation, *args) 
        print "Starting Component %s with task %s" % (self.name, name)
        task.start()
        task.join()


class Pump(Component):
    def __init__(self, name, in_value, out_value, store, flow_out, running):
        '''
            - flow_out : flow_out outputed by the pump (m^3/s)
            - running : is the pump running or not
        '''
        super(Pump, self).__init__(name, in_value, out_value, store)
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
         
        self.set(self.out_value, self.flow_out)




class Tank(Component):

    def __init__(self, name, in_value, out_value, store, height, radius ,level, hole, valve = None):
        '''
            - height : height of the tank (m) 
            - radius : radius of the tank (m)
            - level :  level of the water in the tank
            - hole : hole size in (m)
            - valve : valve to open outlet placed on the tank 
        '''
        super(Tank, self).__init__(name, in_value, out_value, store)
        self.height = height
        self.radius = radius
        self.level = level
        self.hole = hole
        self.valve = valve


    '''
        args: water_level, valve
    '''
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
                flow_out = (math.pi* (self.hole**2 )* math.sqrt(2*self.level*GRAVITY))
            else: 
                flow_out = 0

            try:
                flow_in = self.get(self.in_value, float)
            except KeyError:
                flow_in = 0
            # FIXME change right formula
            rise = flow_out  - flow_in
            self.level = self.level - rise
            if self.level >= 0 :
                self.level = min(self.level, self.height) 
            else:
                self.level = 0 

            if self.out_value != "":
                self.set(self.out_value, flow_out)
            self.set(var_level, self.level)

class Valve(Component):
    def __init__(self, name, in_value, out_value, store, opened):
        '''
            - opened, flag whether the valve is running or not
        '''
        super(Valve, self).__init__(name, in_value, out_value, store)
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
    def __init__(self, name, in_value, out_value, store, flow_rate, length=None, diameter=None):
        '''
            - diameter :  size in m
            - flow_rate : flow rate in the pipe in m^3/s
            - length : length the pipe in meter
        '''
        super(Pipeline, self).__init__(name, in_value, out_value, store)
        self.diameter = diameter
        self.flow_rate = flow_rate
        self.length = length 

    def computation(self, *args):
        '''
            - compute out from in and diameter
            - compute flow rate 
        '''
        var_flow_rate = args[0][0]
        try:
            self.flow_rate = self.get(self.in_value, float)
        except KeyError:
            pass

        self.set(var_flow_rate, self.flow_rate)
        self.set(self.out_value, self.flow_rate)


