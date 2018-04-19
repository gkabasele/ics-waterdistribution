import os
import time
import simpy
import simpy.rt
import subprocess
import threading
import shutil
import argparse

from pyics.component_process import ComponentProcess
from pyics.utils import *
from constants import *

class MediumProcess(ComponentProcess):

    def __init__(self, env, store, name, *args, **kwargs):

        super(MediumProcess, self).__init__(env, store, name, *args, **kwargs)

        # approvisionning
        self.a1 = 50
        self.a2 = 50
        self.a3 = 20

        # first tank
        self.v1 = False
        self.v2 = False
        self.m1 = False
        self.m2 = False
        self.t1 = 0
        self.vt1 = False
        
        # first silo
        self.s1 = 0
        self.vs1 = False

        # second silo
        self.s2 = 0
        self.m2 = False
        self.vs2 = False

        # second tank (charcoal)
        self.tc = 0
        self.vtc = False

        # wagon
        self.we = False
        self.wc = 0
        self.ws = True
        self.wo = False
        self.wm = False

        # final tank
        self.tf = 0
        self.vtf = False

        self.set(A1, self.a1)
        self.set(A2, self.a2)
        self.set(A3, self.a2)
        self.set(V1, self.v1)
        self.set(V2, self.v2)
        self.set(T1, self.t1)
        self.set(M1, self.m1)
        self.set(VT1, self.vt1)
        self.set(S1, self.s1)
        self.set(VS1, self.vs1)
        self.set(S2, self.s2)
        self.set(VS2, self.vs2)
        self.set(M2, self.m2)
        self.set(TC, self.tc)
        self.set(VTC, self.vtc)
        self.set(WE, self.we)
        self.set(WC, self.wc)
        self.set(WO, self.wo)
        self.set(WM, self.wm)
        self.set(WS, self.ws)
        self.set(TF, self.tf)
        self.set(VTF, self.vtf)

    def computation(self, *args, **kwargs):

        motor_dur = 5
        flow_dur = 3
        carcoal_dur = 4
        carcoal_push_dur = 2
        wagon_moving_dur = 2

        amount_fluid_passing = 20

        print "(%d) Staring physiscal process tank" % (self.env.now)

        for i in range(2):
            self.v1 = self.get(V1, "b")
            if self.v1:
                self.pass_fluid(amount_fluid_passing, A1, T1)
                #Close the valve automatically

            self.v2 = self.get(V2, "b")
            if self.v2:
               self.pass_fluid(amount_fluid_passing, A2, T1)

            self.motor1 = self.get(M1, "b")
            if self.motor1:
                print "(%d) running motor1" % (self.env.now)
                yield self.env.timeout(motor_dur)

            self.vt1 = self.get(VT1, "b")
            if self.vt1:
                self.pass_fluid(self.t1, T1, S1)
            
            self.vs1 = self.get(VS1, "b")
            if self.vs1:
                self.pass_fluid(self.s1, S1, S2)

            self.vtc = self.get(VTC, "b")
            self.ws = self.get(WS, "b")
            if self.vtc:
                self.pass_fluid(amount_fluid_passing, TC, WC)
                self.ws = True

            self.wm = self.get(WM, "b")
            if self.wm:
                print "(%d) moving the wagon" % (self.env.now)
                if self.we:
                    self.we = False
                    self.ws = True
                elif self.ws:
                    self.ws = False
                    self.we = True

            self.wo = self.get(WO, "b")
            if self.wo : 
                self.pass_fluid(amount_fluid_passing, WC, S2) 

            self.m2 = self.get(M2, "b")
            if self.m2:
                print "(%d) running motor2" % (self.env.now)
                yield  self.env.timeout(motor_dur)

            self.vs2 = self.get(VS2, "b")
            if self.vs2 :
                self.pass_fluid(self.s2, S2, TF)

            self.vtf = self.get(VTF, "b")
            if self.vtf :
                print "(%d) tank final is open, releasing %d of tank final" % (self.env.now, self.tf)
                self.tf = 0
                self.set(TF, self.tf)

            print "(%d) Approvisionning A1 and A2, tank" % (self.env.now)
            yield self.env.timeout(carcoal_dur)
            self.a1 += 20
            self.a2 += 20
            self.a3 += 20
            self.set(A1, self.a1)
            self.set(A2, self.a2)
            self.set(A3, self.a3)

                
    def pass_fluid(self, amount, from_var, to_var):
        print "(%d) %s is open, passing fluid to %s" % (self.env.now, from_var, to_var)
        attr_from = from_var.lower()
        attr_to = to_var.lower()
        yield self.env.timeout(flow_dur)
        tmp_from = getattr(self, attr_from)
        tmp_to = getattr(self, attr_to)
        setattr(self, attr_from, tmp_from - amount)
        setattr(self, attr_to, tmp_to - amount)
        self.set(from_var, getattr(self, attr_from))
        self.set(to_var, getattr(self, attr_to))

def start(store):
    env = simpy.rt.RealtimeEnvironment(factor=1)
    phys_proc = (MediumProcess(env, store, "Medium Process"))
    env.run()
