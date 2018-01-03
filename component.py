import sys
import os
import redis
from pubsub import pub

class Component(Object):

    def __init__(self, name, in_value, out_value, store):
        '''
            Physical component of an industrial control system 
            - name : name of the component
            - in_value : name of the topic to subscribe to
            - out_value : name of the topic to publish to
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

    def get_from_store(self, name):
        '''
            Get value from actuators
        '''
        return self.store.get(name)

    def set_to_store(self, name, value):
        '''
            Set value to sensors
        '''
        store.set(name, value)


class Tank(Component):

    def __init__(self, level, pump = None):
        '''
            - level :  level of the water in the tank
            - pump : pump placed on the tank to transfer water
        '''
        super.__init__(name, in_value, out_value, store)
        self.level = level
        self.pump = pump

    def computation(*args):
        if pump:
            '''
                - Read pressure
                - compute output rate
                - change flow level
                - publish
            '''
            output = 0.0
            if self.level > 0 and output < self.level:
                self.level = self.level - output
                pub.sendMessage(out_value, arg1=output)

class Pump(Component):
    def __init__(self, name, in_value, out_value, store, pressure, running):
        '''
            - pressure : level of pressure outputed by the pump
            - running : is the pump running or not
        '''
        super.__init__(name, in_value, out_value, store)
        self.pressure = pressure
        self.running = running

    def computation(*args):
        '''
            - Check if running from actuators
            - Change pressure accordingly
        '''
        if not self.running:
            self.pressure = 0
         

class Pipe(Component):
    def __init__(self, name, in_value, out_value, store, diameter, flow_rate, length, valve=None):
        '''
            - diameter :  size in mm
            - flow_rate : flow rate in the pipe in m^3/s
            - length : lenght the pipe in meter
        '''
        super.__init__(name, in_value, out_value, store)
        self.diameter = diameter
        self.flow_rate = flow_rate
        self.length = length 
        self.valve = valve

    def computation(*args):
        '''
            - check if valve open
            - compute out from in and diameter
            - compute flow rate 
        '''
        pass

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
        pass

