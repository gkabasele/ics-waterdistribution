from component import *
import argsparse

def main(args):
    pump = Pump(args.name,
                args.in_value,
                args.out_value,
                args.storename,
                args.running)
    pump.start("pump-tank1", args.period, args.duration, args.flow_out)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", dest="name",default="pump", action="store")
    parser.add_argument("--in_value", dest="in_value", default= None, action="store")
    parser.add_argument("--out_value", dest="out_value", action="store")
    parser.add_argument("--storename", dest="storename", action="store")
    parser.add_argument("--running", dest="running", default=True, type=bool, action="store")
    parser.add_argument("--flow_out", dest="flow_out", type=float, default= 5, action="store")
    parser.add_argument("--period", dest="period",type=int, default=1 ,action="store")
    parser.add_argument("--duration", dest="duration", type=int, default=600, action="store") 

    args = parser.parse_args()
    
