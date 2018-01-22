import argparse
from ..utils import *
from ..plc import *

def main(args):
    plc = PLC(args.ip, args.port, args.store, flow_rate = (IR,1))
    plc.export_variables(EXPORT_VAR)
    plc.run('plc-pipe', args.period, args.duration)
    plc.wait_end(True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", dest="ip", default="localhost", action="store")
    parser.add_argument("--port", dest="port", type=int, action="store")
    parser.add_argument("--store", dest="store", action="store")
    parser.add_argument("--period", dest="period", type=int, default=1, action="store")
    parser.add_argument("--duration", dest="duration", type=int, default=60, action="store")

    args = parser.parse_args()
    main(args)

