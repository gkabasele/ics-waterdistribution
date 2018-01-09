import threading
import Queue
from component import *
from twisted.internet.task import LoopingCall
from twisted.internet import reactor


class PhysicalProcess(object):

    def __init__(self, components=None):
        self.components = components if components else {}

    def add_interaction(self, comp1, buf, comp2):
        comp1.set_outbuf(buf)
        comp2.set_inbuf(buf)
    
    def add_component(self, component):
        self.components[component.name] = component

    def run(self, period, duration, fx, *args, **kwargs):
        loop = LoopingCall(f=fx, args, kwargs)
        loop.start(time)

