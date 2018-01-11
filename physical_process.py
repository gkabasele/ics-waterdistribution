import threading
import Queue
from component import *
from twisted.internet.task import LoopingCall
from twisted.internet import reactor


class PhysicalProcess(object):

    def __init__(self):
        self.components = {}
        # {comp1 : { comp2: (index_in, index_out)}} 
        self.links = {}

    def add_interaction(self, comp1, comp2, buf):
        ''' Simulate the interaction between 2 physical component
            :param comp1: a physical component
            :param comp2: a physical component
            :param buf: the buffer linking the 2 component
        '''
        # check if it already exist
        try:
            self.links[comp1.name][comp2.name]
        except KeyError:
            print "This interaction already exist"
            return

        index_out = comp1.add_outbuf(buf)
        index_in = comp2.add_inbuf(buf)
        if comp1.name not in self.links:
            self.links[comp1.name] = {comp2.name : (index_out, index_in)}
        elif comp2.name not in self.links[comp1.name]:
            self.links[comp1.name][comp2.name] = (index_out, index_in)
    
    def add_component(self, component):
        self.components[component.name] = component

    def run(self, period, duration, fx, *args, **kwargs):
        pass
