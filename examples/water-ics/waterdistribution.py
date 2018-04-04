from pymodbus.client.sync import ModbusTcpClient
from pyics.mtu import MTU, ProcessRange 
from constants import *

class WaterDistribution(MTU):

    def __init__(self, ip, port, client=ModbusTcpClient):
        
        self.pump = False
        self.t1_lvl = 0
        self.t1_vlv = False
        self.pipeline = 0
        self.t2_lvl = 0
        super(WaterDistribution, self).__init__(ip, port, client)


    def main_loop(self, *args, **kwargs):

        self.pump = self.get_variable(PUMP_RNG)
        self.t1_lvl = self.get_variable(TANK1_LVL)
        self.t1_vlv = self.get_variable(TANK1_VLV)
        self.flow_rate = self.get_variable(FLOW_RATE)
        self.t2_lvl = self.get_variable(TANK2_LVL)

        print "Pump: %s,T1_LVL: %s, T1_VLV: %s, FR: %s, T2_LVL: %s" % (self.pump, self.t1_lvl, self.t1_vlv, self.flow_rate, self.t2_lvl) 

        if self.t1_lvl is not None:
            cond_t1 = self.cond[TANK1_LVL]
            cond_t1.execute_action(self.t1_lvl)
        if self.flow_rate is not None:
            cond_flow_rate = self.cond[FLOW_RATE]
            cond_flow_rate.execute_action(self.flow_rate)
        if self.t2_lvl is not None:
            cond_t2 = self.cond[TANK2_LVL]
            cond_t2.execute_action(self.t2_lvl)

    def close_valve(self, *args, **kwargs):
        if self.t1_vlv:
            self.write_variable(TANK1_VLV, False)

    def open_valve(self, *args, **kwargs):
        if not self.t1_vlv:
            self.write_variable(TANK1_VLV, True)

