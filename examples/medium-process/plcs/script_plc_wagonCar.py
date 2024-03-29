import argparse
import logging
import sys
import os
from pyics.utils import *
from pyics.plc import *

print "Launching wagonCar"
if os.path.exists("wagonCar.log"):
    os.remove("wagonCar.log")

logging.basicConfig(filename = "plcs_log" + "/wagonCar.log", mode = 'w', format='[%(asctime)s][%(levelname)s][%(pathname)s-%(lineno)d] %(message)s', level = logging.INFO)

def main(args):
    plc = PLC(args.ip, args.port, args.store, "plc-wagonCar", wagonCar = ('h', 1))
    if args.create_ex:
        plc.export_variables(args.filename)
    plc.run("wagonCar", args.period, args.duration)
    plc.wait_end(True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", dest="ip", default="127.0.0.1", action="store")
    parser.add_argument("--port", dest="port", type=int, action="store")
    parser.add_argument("--store", dest="store", action="store")
    parser.add_argument("--period", dest="period", type=float, default=1, action="store")
    parser.add_argument("--duration", dest="duration", type=int, default=60, action="store")
    parser.add_argument("--export", dest="filename", action="store")
    parser.add_argument("--create", dest="create_ex", action="store_true")
    args, unknown = parser.parse_known_args()
    print(args)
    main(args)