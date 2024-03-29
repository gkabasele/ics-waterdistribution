import argparse
from pyics.utils import *
from pyics.plc import *
from constants import *


def main(args):
    plc = PLC(args.ip, args.port, args.store, "plc-tank1", tank1_level = (HR,1), tank1_valve = (CO,1))   
    plc.run('plc-tank1', args.period, args.duration)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", dest="ip", default="localhost", action="store")
    parser.add_argument("--port", dest="port", default="port", type=int, action="store")
    parser.add_argument("--store", dest="store", action="store")
    parser.add_argument("--period", dest="period", type=int, default=1, action="store")
    parser.add_argument("--duration", dest="duration", type=int, default=60, action="store")
    parser.add_argument("--export", dest="filename", action="store")
    args = parser.parse_args()
    main(args)
