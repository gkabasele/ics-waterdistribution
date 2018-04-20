from pymodbus.client.sync import ModbusTcpClient
from pyics.mty import MTU, ProcessRange
from constants import *

class MTUMedSystem(MTU):

    def __init__(self, ip, port, client=ModbusTcpClient):

        # approvisionning
        self.a1 = 0
        self.a2 = 0
        self.a3 = 0

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
        self.ws = False
        self.wo = False
        self.wm = False

        # final tank
        self.tf = 0
        self.vtf = False

        super(MTUMedSystem, self).__init__(ip, port, client)

    def main_loop(self, *args, **args):
        for attr in vars(self):
            setattr(self, attr, self.get_variable(attr.upper()))

            if self.t1 < 40:

                if self.vt1:
                    self.change_coil(VT1, False)

                if self.t1 >= 0 and self.t1 <20:
                    self.change_coil(V1, True)
                    self.change_coil(V2, False)

                if self.t1 >= 20 :
                    self.change_coil(V1, False)
                    self.change_coil(V2, True)

            elif self.t1 == 40:
                if self.v1:
                    self.change_coil(V1, False)
                if self.v2:
                    self.change_coil(V2, False)                
                
                if not self.m1: 
                    self.change_coil(M1, True)
                if self.m1:
                    self.change_coil(M1, False)
                    self.change_coil(VT1, True)


                

                
    def change_coil(self, name, val):
        setattr(self, name.lower(), val)
        self.write_variable(name, getattr(self, name.lower()))


