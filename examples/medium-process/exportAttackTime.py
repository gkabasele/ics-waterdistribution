import re
from ast import literal_eval
import pdb
from datetime import datetime, timedelta
import constants
import yaml

TS = 0
DICT = 2

ONE_SEC = timedelta(seconds=1)

regex = "(?P<ts>\[(\d|\-| |:|\.)*\]) (?P<d>\{(\w|'|:|,| )*\})"
dateformat = "%Y-%m-%d %H:%M:%S.%f"

export_date_format = "%d/%m/%Y %H:%M:%S"

slow_down_attack = "./slowDown_attack_v3.txt"
out_slow_down_invariant = "./slowDown_atk_time_inv.yml"
out_slow_down_time = "./slowDown_atk_time_time.yml"
#out_slow_down = "./slowDown_export.time.txt"

tank_overflow_attack = "./overflow_attack_v2.txt"
out_overflow_invariant = "./overflow_atk_time_inv.yml"
out_overflow_time = "./overflow_atk_time_time.yml"
#out_overflow = "./overflow_export.time.txt"

COUNT = "count"
VARS = "vars"
VAR = "var"
FROM = "from"
TO = "to"

def update_attack_time(ts, start, end, attack_time):

    if start is None:
        return ts, ts + ONE_SEC
    elif ts == end:
        return start, ts + ONE_SEC
    elif ts > end:
        attack_time.append({'start': start.strftime(export_date_format),
                            "end": end.strftime(export_date_format)})
        return ts, ts + ONE_SEC
    else:
        pdb.set_trace()

def export_attack_invariant(infile, outfile, export_overflow):
    reg = re.compile(regex)
    with open(infile, "r") as fname:
        sd_atk = []
        of_atk = []
        sd_atk_start = None
        sd_atk_end = None
        of_atk_start = None
        of_atk_end = None
        sd_cnt = 0
        of_cnt = 0

        for line in fname:
            if line == "\n":
                continue
            res = reg.match(line).groups()
            if res is not None:
                timestamp = res[TS].replace("[", "").replace("]", "")
                ts = datetime.strptime(timestamp, dateformat)
                ts = ts - timedelta(microseconds=ts.microsecond)
                if 'None' not in line:
                    d = res[DICT]
                    state = literal_eval(d)
                    state['timestamp'] = ts

                if (state['tank1'] > 40 and state['valve1'] == 2 and
                        state['valve2'] == 2 and state['valveTank1'] == 1):
                    of_atk_start, of_atk_end = update_attack_time(ts, of_atk_start, of_atk_end, of_atk)
                    of_cnt += 1

                if (state['tank1'] < 40 and state['tank1'] > 0  and
                        state['silo1'] > 0 and state['silo1'] < 40 and state['valveTank1'] == 1 and
                        state['valve1'] == 1 and state['valve2'] == 1):
                    sd_atk_start, sd_atk_end = update_attack_time(ts, sd_atk_start, sd_atk_end, sd_atk)
                    sd_cnt += 1

    if export_overflow:
        with open(outfile, "w+") as outfname:
            yaml.dump(of_atk, outfname, default_flow_style=False)
            print("Overflow: {}\n".format(of_cnt))
    else:
        with open(outfile, "w+") as outfname:
            yaml.dump(sd_atk, outfname, default_flow_style=False)
            print("Slow Down: {}\n".format(sd_cnt))

def update_last_value(old, new, crit_value):
    if new in crit_value:
        return new
    else:
        return old

def in_between(value, limit1, limit2):
    if limit1 > limit2:
        return limit2 < value and value < limit1
    else:
        return limit1 < value and value < limit2

def export_attack_time(infile, outfile):
    reg = re.compile(regex)
    with open(infile, "r") as fname:

        last = {k : None for k in constants.varmap}
        impacts = {k : False for k in constants.varmap}

        #(from, to, in_transition)
        cond = {
            constants.S2 : (20, 60, False),
            constants.WC : (20, 0, False),
            constants.TF : (0, 60, False),
            constants.WS : (1, 2, False),
            constants.WE : (2, 1, False),
            constants.WO : (1, 2, False),
            constants.M2 : (1, 2, False),
            constants.V1 : (1, 2, False),
            constants.V2 : (1, 2, False),
            constants.M1 : (1, 2, False),
            constants.VS1: (1, 2, False),
            constants.VS2: (1, 2, False),
            constants.VTF: (1, 2, False),
            constants.VTC: (1, 2, False)
            }

        mapping = {}
        for line in fname:
            if line == "\n":
                continue
            res = reg.match(line).groups()
            if res is not None:
                timestamp = res[TS].replace("[", "").replace("]", "")
                ts = datetime.strptime(timestamp, dateformat)
                ts = ts - timedelta(microseconds=ts.microsecond)
                if "None" not in line:
                    d = res[DICT]
                    state = literal_eval(d)
                    state["timestamp"] = ts

                mapping[ts] = {COUNT: 0, VARS: []}

                if last[constants.T1] is not None:
                    for k in cond.keys():
                        if impacts[k] and last[k] == cond[k][0]:
                            # Represent the variable that take longer time
                            # staying in the same value. The transition occuring when the
                            # value change is malicious because it is late
                            if (in_between(state[k], cond[k][0], cond[k][1]) and
                                    not cond[k][2]):
                                mapping[ts][COUNT] = mapping[ts][COUNT]+1
                                trans = {VAR: k, FROM: last[k], TO: state[k]}
                                mapping[ts][VARS].append(trans)
                                cond[k] = (cond[k][0], cond[k][1], True)

                            if state[k] == cond[k][1]:
                                mapping[ts][COUNT] = mapping[ts][COUNT]+1
                                trans = {VAR: k, FROM: last[k], TO: state[k]}
                                mapping[ts][VARS].append(trans)
                                impacts[k] = False
                                cond[k] = (cond[k][0], cond[k][1], False)

                    # Full run of emptying tank
                    if (last[constants.S1] == 0 and state[constants.S1] == 40 and
                            last[constants.T1] == 40 and state[constants.T1] == 0 and
                            impacts[constants.S1] and impacts[constants.T1]):

                        #Two transitions are impacted
                        mapping[ts][COUNT] = mapping[ts][COUNT]+2
                        trans = {VAR: constants.S1, FROM: last[constants.S1],
                                 TO: state[constants.S1]}
                        mapping[ts][VARS].append(trans)
                        trans = {VAR: constants.T1, FROM: last[constants.T1],
                                 TO: state[constants.T1]}
                        mapping[ts][VARS].append(trans)
                        impacts[constants.S1] = False
                        impacts[constants.T1] = False

                    if ((last[constants.VT1] == 2 and state[constants.VT1] == 1) and
                            state[constants.S1] >= 5 and state[constants.S1] <= 35 and
                            state[constants.T1] >= 5 and state[constants.T1] <= 35 and
                            state[constants.V1] == 1 and state[constants.V2] == 1):
                        mapping[ts][COUNT] = mapping[ts][COUNT]+1
                        trans = {VAR: constants.VT1, FROM: last[constants.VT1],
                                 TO: state[constants.VT1]}
                        mapping[ts][VARS].append(trans)

                        for k in impacts.keys():
                            impacts[k] = True

                    if (last[constants.VT1] == 1 and state[constants.VT1] == 2 and
                            impacts[constants.S1] and impacts[constants.T1]):
                        mapping[ts][COUNT] = mapping[ts][COUNT]+1
                        trans = {VAR: constants.VT1, FROM: last[constants.VT1],
                                 TO: state[constants.VT1]}
                        mapping[ts][VARS].append(trans)

                for k in last.keys():
                    last[k] = update_last_value(last[k], state[k],
                                                constants.limitmap[k])

        with open(outfile, "w+") as outfname:
            yaml.dump(mapping, outfname, default_flow_style=False)

export_attack_invariant(tank_overflow_attack, out_overflow_invariant, True)

export_attack_invariant(slow_down_attack, out_slow_down_invariant, False)

export_attack_time(slow_down_attack, out_slow_down_time)

