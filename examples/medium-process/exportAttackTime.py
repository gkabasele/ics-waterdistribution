import re
import pdb

from datetime import datetime
from ast import literal_eval

TS = 0
DICT = 2

regex = "(?P<ts>\[(\d|\-| |:|\.)*\]) (?P<d>\{(\w|'|:|,| )*\})"
dateformat = "%Y-%m-%d %H:%M:%S.%f"

slow_down_attack = "./slowDown_attack_v3.txt"
out_slow_down = "./slowDown_export.time.txt"

tank_overflow_attack = "./overflow_attack_v2.txt"
out_overflow = "./overflow_export.time.txt"


def export_attack_main(infile, outfile):
    reg = re.compile(regex)
    with open(infile, "r") as fname:
        with open(outfile, "w") as outfname:
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

                    #pdb.set_trace() 
                    if state['tank1'] > 40 and state['valve1']==2 and state['valve2']==2 and state['valveTank1']==1:
                        outfname.write("[{}] Overflow Attack\n".format(ts))

                    if (state['tank1'] < 40 and state['tank1'] > 0  and 
                            state['silo1'] > 0 and state['silo1'] < 40 and state['valveTank1']==1 and
                            state['valve1'] == 1 and state['valve2'] == 1):
                        outfname.write("[{}] Slow Down Attack\n".format(ts))

export_attack_main(slow_down_attack, out_slow_down)

export_attack_main(tank_overflow_attack, out_overflow)

