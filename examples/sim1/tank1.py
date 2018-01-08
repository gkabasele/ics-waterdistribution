from component import *
import argparse

def main(args):

    tank = Tank(args.name,
                args.in_value,
                args.out_value,
                args.storename,
                args.height,
                args.radius,
                0,
                args.hole,
                args.opened)
    tank.start("tank1", args.period, args.duration, args.water_level, args.valve_state)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--height", dest="height", type=float, action="store", default = 50)
    parser.add_argument("--radius", dest="radius", type=float, action="store", default = 30)
    parser.add_argument("--hole", dest="hole", type=float, action="store", default = 10)
    parser.add_argument("--name", dest="name", default="tank1",action="store")
    parser.add_argument("--in_value", dest="in_value", action="store")
    parser.add_argument("--out_value", dest="out_value", action="store")
    parser.add_argument("--name_valve", dest="name_valve", default="valve-tank1", action="store")
    parser.add_argument("--opened", dest="opened",type=bool, default=True, action="store")
    parser.add_argument("--storename", dest="storename", action="store")
    parser.add_argument("--water_level", dest="water_level", action="store")
    parser.add_argument("--valve_state", dest="valve_state", action="store")
    parser.add_argument("--period", dest="period", type=int, default= 1, action="store")
    parser.add_argument("--duration", dest="duration", type=int, default=60, action="store") 
    args = parser.parse_args()
    main(args)
