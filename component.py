import sys
import os
import redis
import math

GRAVITY = 9.8

class Component(Object):

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
        self.store = store
        # Value read from the messaging queue
        self.values = {}

    def computation(*args):
        '''
            Computation done by the component 
        '''
        print "This method must be overriden"

    def get(self, name):
        '''
            Get value from actuators
        '''
        return self.store.get(name)

    def set(self, name, value):
        '''
            Set value to sensors
        '''
        store.set(name, value)



class Pump(Component):
    def __init__(self, name, in_value, out_value, store, flow_out, running):
        '''
            - flow_out : flow_out outputed by the pump (m^3/s)
            - running : is the pump running or not
        '''
        super.__init__(name, in_value, out_value, store)
        self.flow_out = flow_out
        self.running = running

    def computation(*args):
        '''
            - Check if running from actuators
            - Change flow_out accordingly
        '''
        self.running = self.get(args)
        if not self.running:
            self.flow_out = 0
        else :
            self.flow_out = self.get(args)
         
        self.set(self.out_value, self.flow_out)




class Tank(Component):

    def __init__(self, height, radius ,level, hole, valve = None):
        '''
            - height : height of the tank (m) 
            - radius : radius of the tank (m)
            - level :  level of the water in the tank
            - hole : hole size in (m)
            - valve : valve to open outlet placed on the tank 
        '''
        super.__init__(name, in_value, out_value, store)
        self.height = height
        self.radius = radius
        self.level = level
        self.hole = hole
        self.valve = valve

    def computation(*args):
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
            if self.valve.opened:
                flow_out = self.hole * math.sqrt(2*self.level*GRAVITY) 
            else: 
                flow_out = 0

            flow_in = self.get(self.in_value)
            # FIXME change right formula
            rise = flow_out  - flow_in
            self.level = self.level - rise
            if self.level >= 0 :
                self.level = min(self.level, self.height) 
            else:
                self.level = 0 

            self.set(self.out_value, flow_out)
            self.set(args,self.level)

class Valve(Component):
    def __init__(self, name, in_value, out_value, store, opened):
        '''
            - opened, flag whether the valve is running or not
        '''
        super.__init__(name, in_value, out_value, store)
        self.opened = opened

    def computation(*args):
        '''
            - check actuator from store
            - change status, open or not
        '''
        self.opened = self.get(args)

class Pipe(Component):
    def __init__(self, name, in_value, out_value, store, diameter, flow_rate, length, valve=None):
        '''
            - diameter :  size in mm
            - flow_rate : flow rate in the pipe in m^3/s
            - length : length the pipe in meter
        '''
        super.__init__(name, in_value, out_value, store)
        self.diameter = diameter
        self.flow_rate = flow_rate
        self.length = length 

    def computation(*args):
        '''
            - compute out from in and diameter
            - compute flow rate 
        '''
        self.flow_rate = self.get(in_value)
        self.set(args, self.flow_rate)
        self.set(out_value, self.flow_rate)


