import argparse
from utils import *
from mtu import *


def main(args):
    mtu =  WaterDistribution(args.ip, args.port)
    mtu.get_dir(args.filename)
    mtu.add_cond(TANK1_LVL, 0, 30, mtu.close_valve, mtu.open_valve)
    mtu.add_cond(FLOW_RATE, 0, 20, mtu.close_valve, mtu.open_valve)
    mtu.add_cond(TANK2_LVL, 1, 30, mtu.open_valve, mtu.close_valve)
    mtu.create_task('mtu', args.period, args.duration)
    mtu.start()
    mtu.wait_end()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", dest="ip", default="localhost", action="store")
    parser.add_argument("--port", dest="port", default="port", type=int, action="store")
    parser.add_argument("--period", dest="period", type=int, default=1, action="store")
    parser.add_argument("--duration", dest="duration", type=int, default=60, action="store")
    parser.add_argument("--import", dest="filename", action="store")
    args = parser.parse_args()
    main(args)
