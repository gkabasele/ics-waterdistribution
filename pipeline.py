from component import *
import argparse

def main(args):
    pipeline = Pipeline(args.name,
                    args.in_value,
                    args.out_value,
                    args.storename,
                    args.flow_rate)
    pipeline.start("pipe", args.period, args.duration, args.pipe_fl)

if __name__ == "__main__" :

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", dest="name", default="pipe", action="store")
    parser.add_argument("--in_value", dest="in_value", action="store")
    parser.add_argument("--out_value", dest="out_value", action="store")
    parser.add_argument("--storename", dest="storename", action="store")
    parser.add_argument("--period", dest="period", type=int, default=1, action="store")
    parser.add_argument("--duration", dest="duration", type=int, default=60, action="store")
    parser.add_argument("--flow_rate", dest="flow_rate", type=float, default= 0, action = "store")
    parser.add_argument("--pipe_fl", dest="pipe_fl", action= "store")
    args = parser.parse_args()

    main(args)

