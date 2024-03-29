import os
import random
from datetime import datetime

import simpy
import simpy.rt

from pyics.component_process import ComponentProcess
from pyics.utils import *
from constants import *



class Container():

    def __init__(self, value, speed, limit=0):
        self.value = value
        self.speed = speed
        self.speed_index = 0
        self.limit = limit

    def transfer(self, other, src=None, dst=None, now=None):
        if now is not None:
            print("({}) Tranferring from {} to {}".format(now,
                                                          src, dst))
        amount = min(self.value, self.speed[self.speed_index])
        self.value = max(self.value - amount, 0)
        if other.value + amount > other.limit:
            raise ValueError("Overflow")

        other.value = min(other.value + amount, other.limit)


        if self.value == 0:
            self.speed_index = (self.speed_index + 1) % len(self.speed)

    def empty(self, name=None, now=None):
        if now is not None:
            print("({} Emptying {}".format(now, name))

        self.value = max(self.value - self.speed[self.speed_index], 0)

        if self.value == 0:
            self.speed_index = (self.speed_index + 1) % len(self.speed)


class MediumProcess(ComponentProcess):

    def __init__(self, env, store, name, lock, do_attack, 
                 atk_filename, *args, **kwargs):

        super(MediumProcess, self).__init__(env, store, name, lock, *args, **kwargs)


        # approvisionning
        self.approvisioning1 = Container(0, [5, 2], limit=500)
        self.approvisioning2 = Container(0, [5, 2], limit=500)

        # first tank
        self.valve1 = False
        self.valve2 = False
        self.motor1 = False
        self.motor2 = False
        self.tank1 = Container(0, [2, 10, 5], limit=60)
        self.valveTank1 = False

        # first silo
        self.silo1 = Container(0, [4, 5], limit=60)
        self.valveSilo1 = False

        # second silo
        self.silo2 = Container(0, [5, 10], limit=80)
        self.motor2 = False
        self.valveSilo2 = False

        # second tank (charcoal)
        self.tankCharcoal = Container(0, [5, 2], limit=500)
        self.valveTankCharcoal = False

        # wagon
        self.wagonEnd = False
        self.wagonCar = Container(0, [2, 5], limit=40)
        self.wagonStart = True
        self.wagonlidOpen = False
        self.wagonMoving = False

        # final tank
        self.tankFinal = Container(0, [10, 5], limit=80)
        self.valveTankFinal = False

        self.valve_sync = {x : -1 for x in varmap.keys() if x.startswith("valve")}
        self.valve_sync[WO] = -1

        self.set(A1, self.approvisioning1.value)
        self.set(A2, self.approvisioning2.value)
        self.set(V1, self.valve1)
        self.set(V2, self.valve2)
        self.set(T1, self.tank1.value)
        self.set(M1, self.motor1)
        self.set(VT1, self.valveTank1)
        self.set(S1, self.silo1.value)
        self.set(VS1, self.valveSilo1)
        self.set(S2, self.silo2.value)
        self.set(VS2, self.valveSilo2)
        self.set(M2, self.motor2)
        self.set(TC, self.tankCharcoal.value)
        self.set(VTC, self.valveTankCharcoal)
        self.set(WE, self.wagonEnd)
        self.set(WC, self.wagonCar.value)
        self.set(WO, self.wagonlidOpen)
        self.set(WM, self.wagonMoving)
        self.set(WS, self.wagonStart)
        self.set(TF, self.tankFinal.value)
        self.set(VTF, self.valveTankFinal)

        self.do_attack = do_attack

        # Number steps
        self.cur_step = 0

        # Start step for the attack
        self.start_step = 600

        # Frame size of the attack
        self.frame_size = 60

        # Waiting size
        self.wait_size = 300

        #attack time
        self.attack_time = self.gen_attack_time()
        self.curr_atk_time = 0

        #attack type
        self.atk_types = [VT1, VS2, WO]
        self.cur_type = 0
        self.running_atk = False

        self.atk_filename = atk_filename

    def computation(self, *args, **kwargs):

        print "(%d) Starting physiscal process tank" % (self.env.now)

        while True:
            print "(%d) Approvisionning A1 and A2, tankCharcoal" % (self.env.now)
            yield self.env.timeout(quick_dur)
            self.approvisioning1.value = min(self.approvisioning1.value + 2*amount_fluid_passing,
                                             self.approvisioning1.limit)

            self.approvisioning2.value = min(self.approvisioning2.value + 2*amount_fluid_passing,
                                             self.approvisioning2.limit)

            self.tankCharcoal.value = min(self.tankCharcoal.value + 2*amount_fluid_passing,
                                          self.tankCharcoal.limit)

            self.set(A1, self.approvisioning1.value)
            self.set(A2, self.approvisioning2.value)
            self.set(TC, self.tankCharcoal.value)
            self.lock.acquire()
            self.valves_effect()
            self.lock.release()
            self.cur_step += 1

    def gen_attack_time(self):
        curr = [x for x in range(self.start_step, self.start_step + self.frame_size + 1)]
        end = curr[-1]
        for x in range(10):
            start = end + self.wait_size
            ex = [x for x in range(start, start + self.frame_size + 1)]
            curr.extend(ex)
            end = curr[-1]
        return curr

    def valves_effect(self):
        attack = False

        if self.do_attack:

            if self.curr_atk_time < len(self.attack_time):
                attack = (self.cur_step == self.attack_time[self.curr_atk_time])

            if attack:
                self.curr_atk_time += 1
                self.atk_filename.write(str(datetime.now()) + ": 1\n")
                self.running_atk = True
            else:
                if self.running_atk:
                    self.cur_type = (self.cur_type + 1) % len(self.atk_types)
                    self.running_atk = False

        if self.get(V1, "b"):
            self.pass_fluid(V1, A1, T1)

        if self.get(V2, "b"):
            self.pass_fluid(V2, A2, T1)

        if self.get(VT1, "b"):
            if attack and self.atk_types[self.cur_type] == VT1:
                self.valveTank1 = False
                self.set(VT1, self.valveTank1)

            else:
                self.pass_fluid(VT1, T1, S1)

        if self.get(VS1, "b"):
            self.pass_fluid(VS1, S1, S2)

        if self.get(VTC, "b"):
            self.pass_fluid(VTC, TC, WC)

        if self.get(WO, "b"):


            if attack and  self.atk_types[self.cur_type] == WO:
                self.wagonlidOpen = False
                self.set(WO, self.wagonlidOpen)

            else:
                self.pass_fluid(WO, WC, S2)

        if self.get(VS2, "b"):

            if attack and self.atk_types[self.cur_type] == VS2:
                self.valveSilo2 = False
                self.set(VS2, self.valveSilo2)

            else:
                self.pass_fluid(VS2, S2, TF)

        if self.get(VTF, "b"):
            self.release_tank(VTF, TF)

    def move_wagon(self):
        print "(%d) moving the wagon" % (self.env.now)
        if self.wagonEnd:
            self.wagonEnd = False
            self.wagonStart = True
            self.wagonMoving = False

        elif self.wagonStart:
            self.wagonStart = False
            self.wagonEnd = True
            self.wagonMoving = False

        self.set(WE, self.wagonEnd)
        self.set(WS, self.wagonStart)
        self.set(WM, self.wagonMoving)

    def running_motor(self, name):
        print "(%d) running motor %s" % (self.env.now, name)

    def release_tank(self, valve, tank_name):
        if self.valve_sync[valve] == self.env.now:
            return
        else:
            tank = getattr(self, tank_name)
            self.valve_sync[valve] = self.env.now
            print "(%d) tank %s is open, releasing %d of tank final" % (self.env.now,
                                                                        tank_name,
                                                                        tank.value)
            tank.empty()
            self.set(tank_name, tank.value)

    def pass_fluid(self, valve, attr_from, attr_to):
        if self.valve_sync[valve] == self.env.now:
            return
        else:
            self.valve_sync[valve] = self.env.now
            print "(%d) %s is open, passing fluid to %s" % (self.env.now, attr_from, attr_to)
            tmp_from = getattr(self, attr_from)
            tmp_to = getattr(self, attr_to)
            tmp_from.transfer(tmp_to)
            self.set(attr_from, getattr(self, attr_from).value)
            self.set(attr_to, getattr(self, attr_to).value)

    def empty_wagon(self, attr):
        print "(%d) [Error] emptying %s"  % (self.env.now, attr)
        tmp = getattr(self, attr)
        tmp.value = max(tmp.value - tmp.step, 0)
        self.set(attr, getattr(self, attr).value)

def start(store, nb_round):
    env = simpy.rt.RealtimeEnvironment(factor=1)
    phys_proc = (MediumProcess(env, store, "Medium Process", nb_round))
    env.run(until=nb_round)
