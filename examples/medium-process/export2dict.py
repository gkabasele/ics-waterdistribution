import argparse
import pickle
import re
import pdb
from datetime import datetime
from ast import literal_eval

TS = 0
DICT = 2

regex = "(?P<ts>\[(\d|\-| |:|\.)*\]) (?P<d>\{(\w|'|:|,| )*\})"
dateformat = "%Y-%m-%d %H:%M:%S.%f"

def main(inname, outname):

    states = []

    reg = re.compile(regex)

    with open(inname, "r") as fname:
        for line in fname:
            if line == "\n":
                continue
            res = reg.match(line).groups()
            if res is not None:
                timestamp = res[TS].replace("[", "").replace("]","")
                ts = datetime.strptime(timestamp, dateformat)
                if 'None' not in line:
                    d = res[DICT]
                    state = literal_eval(d)
                    state['timestamp'] = ts
                    states.append(state)


    with open(outname, "wb") as fname:
        pickle.dump(states, fname)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--in", action="store", dest="inname")
    parser.add_argument("--out", action="store", dest="outname")

    args = parser.parse_args()

    main(args.inname, args.outname)
