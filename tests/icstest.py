from pymodbus.client.sync import ModbusTcpClient
from pyics.mtu import MTU, ProcessRange 

LVL = "level"
VLV = "valve"
PRESS = "pressure"
TEMP = "temp"

class ICSTest(MTU):

    def __init__(self, ip, port, client=ModbusTcpClient):

        self.level = {LVL : 0}
        self.valve = {VLV : False}
        self.press = {PRESS : 0}
        self.temp  = {TEMP : 0}
        
        super(ICSTest, self).__init__(ip, port, client)


    def main_loop(self, *args, **kwargs):

        for k,v in self.__dict__:
            name = v.keys()
            val = self.get_variable(name)
            if val is not None:
                self.__setattr__(k,{name : val})  
                if name in self.cond:
                    cond = self.cond[name]
                    cond.execute_action(val)
        
    def close_valve(self, *args, **kwargs):
        self.write_variable(VLV, False)

    def open_valve(self, *args, **kwargs):
        self.write_variable(VLV, True)

