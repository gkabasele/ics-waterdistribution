from component import *
import argparse

def main(args):
    tank = Tank(args.name,
                args.in_value,
                None,
                args.storename,
                args.height,
                args.radius,
                0,
                args.hole)
    tank.start("tank2", args.period, args.duration, args.water_level)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--height", dest="height", type=float, action="store", default = 50)
    parser.add_argument("--radius", dest="radius", type=float, action="store", default = 30)
    parser.add_argument("--hole", dest="hole", type=float, action="store", default = 10)
    parser.add_argument("--name", dest="name", action="store")
    parser.add_argument("--in_value", dest="in_value", action="store")
    parser.add_argument("--storename", dest="storename", action="store")
    parser.add_argument("--water_level", dest="water_level", action="store")
    parser.add_argument("--period", dest="period", type=int, default=1, action="store")
    parser.add_argument("--duration", dest="duration", type=int, default=600, action="store")
    args = parser.parse_args()

    main(args)
