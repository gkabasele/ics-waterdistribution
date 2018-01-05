from component import *
import argparse

def main(args):
    pipeline = Pipe(args.name,
                    args.in_value,
                    args.out_value,
                    args.storename,
                    0)
    pipeline.start("pipe", args.period, args.duration, args.flow_rate)

if __name__ == "__main__" :

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", dest="name", default="pipe", action="store")
    parser.add_argument("--in_value", dest="in_value", action="store")
    parser.add_argument("--out_value", dest="out_value", action="store")
    parser.add_argument("--storename", dest="storename", action="store")
    parser.add_argument("--period", dest="period", type=int, default=1, action="store")
    parser.add_argument("--duration", dest="duration", type=int, default=600, action="store")
    parser.add_argument("--flow_rate", dest="flow_rate", type=float, default= 0,action = "store")
    args = parser.parse_args()

    main(args)

