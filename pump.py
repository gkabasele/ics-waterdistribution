from component import *
import argparse

def main(args):
    pump = Pump(args.name,
                "",
                args.out_value,
                args.storename,
                args.flow_out,
                args.running)
    pump.start("pump-tank1", args.period, args.duration, args.running)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", dest="name",default="pump", action="store")
    parser.add_argument("--out_value", dest="out_value", action="store")
    parser.add_argument("--storename", dest="storename", action="store")
    parser.add_argument("--running", dest="running", default=True, type=bool, action="store")
    parser.add_argument("--flow_out", dest="flow_out", type=float, default= 5, action="store")
    parser.add_argument("--period", dest="period",type=int, default=1 ,action="store")
    parser.add_argument("--duration", dest="duration", type=int, default=60, action="store") 

    args = parser.parse_args()
    
