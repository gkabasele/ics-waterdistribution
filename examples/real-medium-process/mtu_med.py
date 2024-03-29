import logging
from datetime import datetime
from pymodbus.client.sync import ModbusTcpClient
from pyics.mtu import MTU, ProcessRange
from constants import *


logger = logging.getLogger(__name__)

class MTUMedSystem(MTU):

    def __init__(self, ip, port, export_file, client=ModbusTcpClient):


        self.varmap = {
                            A1  : 0,             
                            A2  : 0, 
                            V1  : False, 
                            V2  : False, 
                            T1  : 0, 
                            M1  : False, 
                            M1a : False, 
                            MS1 : 0, 
                            VT1 : False,
                            S1  : 0, 
                            VS1 : False,
                            S2  : 0,
                            VS2 : False,
                            M2  : False,         
                            M2a : False,         
                            MS2 : 0,         
                            TC  : 0,
                            VTC : False,
                            WE  : False, 
                            WC  : 0, 
                            WM  : False,
                            WO  : False,
                            WS  : False, 
                            TF  : 0,
                            VTF : False
        }


        self.running_m1 = False
        self.running_m1a = False
        self.running_m2 = False
        self.running_m2a = False
        self.emptying_t1 = False
        self.emptying_s2 = False
        self.emptying_s1 = False
        self.emptying_wg = False
        self.emptying_tf = False

        # motor1 running waiting
        self.m1_running_waiting = 0
        self.m1a_running_waiting = 0

        self.motor_waiting = 10

        self.m2_running_waiting = 0
        self.m2a_running_waiting = 0

        self.export_file = export_file

        super(MTUMedSystem, self).__init__(ip, port, client)



    def write_and_flush(self, msg):
        self.export_file.write(msg)
        self.export_file.flush()

    def write_to_logfile(self):
        msg = str(self.varmap)
        msg.replace("False", "1").replace("True", "2")
        logger.info(msg)

    def main_loop(self, *args, **kargs):
        for k, v in self.varmap.iteritems():
            self.varmap[k] = self.get_variable(k)

        if any(x is None for x in self.varmap.itervalues()):
            return

        self.write_to_logfile()
        msg = "[{}] {}, e1:{}, es1:{}, ew:{}, ".format(datetime.now(), self.varmap, 
                                                       self.emptying_t1, self.emptying_s1, 
                                                       self.emptying_wg)


        msg += "es2:{}, rm1:{}, rm1a:{}, ".format(self.emptying_s2, 
                                                   self.running_m1,
                                                   self.running_m1a)

        msg += "rm1w:{}, rm1aw:{}, rm2w:{}, rm2aw:{} ".format(self.m1_running_waiting,
                                                              self.m1a_running_waiting,
                                                              self.m2_running_waiting,
                                                              self.m2a_running_waiting)


        msg += "rm2:{}, rm2a:{}, ef:{}\n\n".format(self.running_m2,
                                                   self.running_m2a,
                                                   self.emptying_tf)

        self.export_file.write(msg)

        self.tank1_management()
        self.wagon_management()

        if self.varmap[TF] < 60:

            if self.varmap[TF] == 0:
                self.emptying_tf = False

            if self.varmap[VTF] and not self.emptying_tf:
                if self.varmap[VTF]:
                    self.change_coil(VTF, False)

            elif self.emptying_tf and not self.varmap[VTF]:
                self.change_coil(VTF, True)

        elif self.varmap[TF] == 60:
            self.change_coil(VTF, True)
            self.emptying_s2 = False
            self.running_m2 = False
            self.emptying_tf = True

        if self.varmap[S1] < 40 and self.emptying_s1 and not self.varmap[VS1]:
            self.change_coil(VS1, True)

        if self.varmap[S2] < 20 and not self.emptying_s2:
            if self.varmap[VS2]:
                self.change_coil(VS2, False)
            if self.varmap[M2]:
                self.change_coil(M2, False)

        elif self.varmap[S2] == 20 and not self.emptying_s2:
            if self.varmap[S1] == 40:
                self.change_coil(VS1, True)
                self.emptying_s1 = True

        # case where the emptying was interrupted
        elif self.varmap[S2] <= 60 and self.emptying_s2 and not self.varmap[VS2]:
            self.change_coil(VS2, True)

        elif self.varmap[S2] == 60:
            if self.varmap[S1] == 0:
                self.change_coil(VS1, False)
                self.emptying_s1 = False

            if self.varmap[M2]:
                if self.varmap[TF] < 60 and not self.emptying_tf:
                    self.change_coil(M2, False)
                    self.change_coil(VS2, True)
                    self.emptying_s2 = True
            else:
                if not self.running_m2:
                    self.change_coil(M2, True)
                    self.running_m2 = True
                else:
                    self.change_coil(M2, False)

    def tank1_management(self):
        if self.varmap[T1] < 40 and not self.emptying_t1:
            if self.varmap[VT1]:
                self.change_coil(VT1, False)

            if self.varmap[T1] >= 0 and self.varmap[T1] < 20:
                self.change_coil(V1, True)
                if self.varmap[V2]:
                    self.change_coil(V2, False)

            if self.varmap[T1] >= 20:
                self.change_coil(V2, True)
                if self.varmap[V1]:
                    self.change_coil(V1, False)

        elif self.varmap[T1] < 40 and self.emptying_t1 and not self.varmap[VT1]:
            self.change_coil(VT1, True)
            if self.varmap[V1]:
                self.change_coil(V1, False)
            if self.varmap[V2]:
                self.change_coil(V2, False)

        elif self.varmap[T1] == 40:
            if self.varmap[V1]:
                self.change_coil(V1, False)
            if self.varmap[V2]:
                self.change_coil(V2, False)

            if self.varmap[M1] and self.varmap[M1a]:
                if (self.m1_running_waiting + self.m1a_running_waiting) >= 2 * self.motor_waiting:
                    self.change_coil(M1, False)
                    self.change_coil(M1a, False)

                    if self.varmap[S1] < 40:
                        if self.varmap[S1] == 0:
                            self.change_coil(VT1, True)
                            self.emptying_t1 = True
                else:
                    self.m1a_running_waiting += 1

            elif self.varmap[M1] and not self.varmap[M1a]:

                self.m1_running_waiting += 1
                if self.m1_running_waiting == self.motor_waiting:
                    self.change_coil(M1a, True)
                    self.running_m1a = True

            else:
                if not self.running_m1:
                    self.change_coil(M1, True)
                    self.running_m1 = True
                else:
                    if self.varmap[S1] == 0:
                        self.change_coil(VT1, True)
                        self.emptying_t1 = True

        if self.varmap[S1] == 40:
            self.running_m1 = False
            self.running_m1a = False
            self.m1_running_waiting = 0
            self.m1a_running_waiting = 0
            self.emptying_t1 = False

    def wagon_management(self):
        if self.varmap[WS]:
            if self.varmap[WC] < 20:
                self.change_coil(VTC, True)
            elif self.varmap[WC] == 20 and not self.varmap[WE]:
                self.change_coil(VTC, False)
                self.change_coil(WM, True)
        elif self.varmap[WE]:

            if self.varmap[WC] == 20 and self.varmap[S2] == 0:
                self.change_coil(WO, True)
                self.emptying_wg = True

            elif self.varmap[WC] < 20 and not self.varmap[WO] and self.emptying_wg:
                self.change_coil(WO, True)

            elif self.varmap[WC] == 0 and not self.varmap[WS]:
                self.change_coil(WO, False)
                self.emptying_wg = False
                self.change_coil(WM, True)

    def change_coil(self, name, val):
        if self.varmap[name] != val:
            self.varmap[name] = val
            self.write_variable(name, val)
            logger.info("Changing %s to %s" %(name, val))

