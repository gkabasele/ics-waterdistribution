from component import *
import argparse



def main(args):
    valve = Valve(args.name_valve, 
                  args.valve_in, 
                  args.valve_out, 
                  args.storename, 
                  args.opened) 
    valve.start("valve-tank1", args.period, args.duration, args.valve_state)

    tank = Tank(args.name,
                args.in_value,
                args.out_value,
                args.storename,
                args.height,
                args.radius,
                0,
                args.hole,
                valve)
    tank.start("tank1", args.period, args.duration, args.water_level)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--height", dest="height", type=float, action="store", default = 50)
    parser.add_argument("--radius", dest="radius", type=float, action="store", default = 30)
    parser.add_argument("--hole", dest="hole", type=float, action="store", default = 10)
    parser.add_argument("--name", dest="name", action="store")
    parser.add_argument("--in_value", dest="in_value", action="store")
    parser.add_argument("--out_value", dest="out_value", action="store")
    parser.add_argument("--name_valve", dest="name_valve", action="store")
    parser.add_argument("--valve_in", dest="valve_in", action="store")
    parser.add_argument("--valve_out", dest="valve_out", action="store")
    parser.add_argument("--opened", dest="opened", action="store")
    parser.add_argument("--storename", dest="storename", action="store")
    parser.add_argument("--water_level", dest="water_level", action="store")
    parser.add_argument("--valve_state", dest="valve_state", action="store")
    parser.add_argument("--period", dest="period",type=int ,action="store")
    parser.add_argument("--duration", dest="duration", type=int, action="store") 
    args = parser.parse_args()

    main(args)
