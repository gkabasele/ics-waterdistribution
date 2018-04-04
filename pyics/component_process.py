import sys
import simpy
import os
import math
import logging
from simplekv.fs import FilesystemStore
from utils import *

logger = logging.getLogger(__name__)


class ComponentProcess(object):

    def __init__(self, env, store, name, *args, **kwargs):

        ''' Physical component of an industrial control system

            :param env: environment for the process simulation
            :param store: location of the store to set processes variables
            :param name: the name of the component
        '''
        self.name = name
        self.store = FilesystemStore(store)

        self.env = env
        self.action = env.process(self.computation(args, kwargs))


    def computation(self, *args, **kwargs):

        ''' Computation done by the component
            
            :param args: argument used by the component
            :param kwargs: key argument used by the Component
        '''

        raise NotImplementedError

    def get(self, name, typeobj):

        '''Get value from actuators

           :param name: name of the process variable
           :param typeobj: type of the process variable
        '''
        if typeobj == "b":
            val = self.store.get(name)
            if val == "True" or val == "False":
                return val == "True"
            else:
                raise TypeError
        return typeobj(self.store.get(name))

    def set(self, name, value):

        '''Set value to sensors
           
           :param name: name of the process variable
           :param value: value to set to the process variable 
        '''
        self.store.put(name, str(value))

