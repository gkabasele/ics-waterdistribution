import os
import shutil
from utils import CustomDict
from component import *


class PhysicalProcess(object):

    def __init__(self, store):
        
        if os.path.exists(store):
            shutil.rmtree(store)

        self.store = store

        # {comp1.name : [VAR1, VAR2]}
        self.variables = CustomDict()
        # {comp1.name : name}
        self.components = CustomDict()
        # {comp1.name : { comp2.name: (index_in, index_out)}} 
        self.links = {} 

    def get_comp(self, name):
        ''' Return a component

            :param name: name of the component
        '''
        return self.components[name]

    def get_index(self, comp1, comp2):
        return self.components[comp1.name][comp2.name]



    def add_variable(self, comp ,var):
        ''' Add a process variable

            :param var: process variable
        '''
        if comp.name in self.components:
            self.variables[comp.name].append(var)
        else:
            print "The component has not been added to the physical process"

    def add_interaction(self, comp1, comp2, size=1):
        ''' Simulate the interaction between 2 physical component

            Return index of input buffer and output buffer

            :param comp1: a physical component
            :param comp2: a physical component
            :param size: size of the buffer linking the 2 component
        '''
        # check if it already exist
        try:
            self.links[comp1.name][comp2.name]
            print "The interaction %s -> %s  already exist" % (comp1.name, comp2.name)
            return
        except KeyError:
            pass

        buf = ComponentQueue(size)

        index_out = comp1.add_outbuf(buf)
        index_in = comp2.add_inbuf(buf)
        if comp1.name not in self.links:
            self.links[comp1.name] = {comp2.name : (index_out, index_in)}
        elif comp2.name not in self.links[comp1.name]:
            self.links[comp1.name][comp2.name] = (index_out, index_in)
        return  index_out, index_in
    
    def add_component(self, component, *args, **kwargs):
        ''' Add a new component to the physical process
            
            :param component: a physical component class
        '''
        comp = component(self.store, *args, **kwargs)
        self.components[comp.name] = comp
        if comp.name not in self.variables:
            self.variables[comp.name] = []
            return comp

    def run(self):
        ''' Start all components of the process
        '''
        for v in self.components.itervalues():
            v.start()

    def wait_end(self):
        for v in self.components.itervalues():
            v.wait_end()
