import re
import yaml
import pdb

from datetime import datetime, timedelta
from ast import literal_eval

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

def export_attack_time(infile, outfile):
    reg = re.compile(regex)
    with open(infile, "r") as fname:
        t1 = None
        s1 = None
        vt1 = None
        v1 = None
        v2 = None
        impact_s1t1 = False
        impact_v1 = False
        impact_v2 = False
        n_malicious_trans = 0
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

                mapping[ts] = n_malicious_trans

                if t1 is not None:
                    if (((vt1 == 2 and state['valveTank1'] == 1) or
                         (vt1 == 1 and state['valveTank1'] == 2)) and
                            state['silo1'] >= 5 and state['silo1'] <= 35 and
                            state['tank1'] >= 5 and state['tank1'] <= 35 and
                            state['valve1'] == 1 and state['valve2'] == 1):
                        mapping[ts] = mapping[ts]+1
                        impact_s1t1 = True
                        impact_v1 = True
                        impact_v2 = True

                    if (s1 == 0 and state['silo1'] == 40 and
                            t1 == 40 and state['tank1'] == 0) and impact_s1t1:
                        #Two transition are impacted
                        mapping[ts] = mapping[ts]+2
                        impact_s1t1 = False

                    if v1 == 1 and state['valve1'] == 2 and impact_v1:
                        mapping[ts] = mapping[ts]+1
                        impact_v1 = False

                    if v2 == 1 and state['valve2'] == 2 and impact_v2:
                        mapping[ts] = mapping[ts]+1
                        impact_v2 = False

                t1 = update_last_value(t1, state['tank1'], [0, 40])
                s1 = update_last_value(s1, state['silo1'], [0, 40])
                vt1 = update_last_value(vt1, state['valveTank1'], [1, 2])
                v1 = update_last_value(v1, state['valve1'], [1, 2])
                v2 = update_last_value(v2, state['valve2'], [1, 2])

        with open(outfile, "w+") as outfname:
            yaml.dump(mapping, outfname, default_flow_style=False)

export_attack_invariant(tank_overflow_attack, out_overflow_invariant, True)

export_attack_invariant(slow_down_attack, out_slow_down_invariant, False)

export_attack_time(slow_down_attack, out_slow_down_time)

