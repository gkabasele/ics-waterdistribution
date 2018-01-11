import os
import shutil
from component import *


class PhysicalProcess(object):

    def __init__(self, store):
        
        if os.path.exists(store):
            shutil.rmtree(store)

        # {comp1.name : [VAR1, VAR2]}
        self.variables = {}
        # {comp1.name : name}
        self.components = {}
        # {comp1.name : { comp2.name: (index_in, index_out)}} 
        self.links = {}

    def add_variable(self, comp ,var):
        self.variables[comp.name].append(var)

    def add_interaction(self, comp1, comp2, size):
        ''' Simulate the interaction between 2 physical component
            :param comp1: a physical component
            :param comp2: a physical component
            :param size: size of the buffer linking the 2 component
        '''
        # check if it already exist
        try:
            self.links[comp1.name][comp2.name]
        except KeyError:
            print "This interaction already exist"
            return

        buf = ComponentQueue(size)

        index_out = comp1.add_outbuf(buf)
        index_in = comp2.add_inbuf(buf)
        if comp1.name not in self.links:
            self.links[comp1.name] = {comp2.name : (index_out, index_in)}
        elif comp2.name not in self.links[comp1.name]:
            self.links[comp1.name][comp2.name] = (index_out, index_in)
    
    def add_component(self, component):
        self.components[component.name] = component
        if component.name not in self.variables:
            self.variables[component.name] = []

    def run(self, period, duration, fx, *args, **kwargs):
        ''' Start all components of the process
        '''
        pass 
