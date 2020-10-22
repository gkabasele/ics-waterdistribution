import sys
import argparse
import time
import logging
from tankOverflow import TankOverflow
from slowDown import SlowDown
from stopProcess import StopProcess

logging.basicConfig(filename="new_slowDown_atk.log", mode="w", format='[%(asctime)s][%(levelname)s][%(pathname)s-%(lineno)d] %(message)s', level= logging.INFO)

def main(ip, port, period, duration, filename, export_file, attack, start):
    time.sleep(start)
    classname = attack.replace(attack[0], attack[0].upper())
    attack_class = getattr(sys.modules[__name__], classname)
    with open(export_file, "w") as fn:
        mtu = attack_class(ip, port, fn)
        mtu.get_dir(filename)
        mtu.create_task('attacker', period, duration)
        mtu.start()
        mtu.wait_end()

if  __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", action="store", dest="ip")
    parser.add_argument("--port", type=int, action="store", dest="port")
    parser.add_argument("--period", type=float, default=1, action="store",
                        dest="period")
    parser.add_argument("--duration", type=int, default=60, action="store", dest="duration")
    parser.add_argument("--import", action="store", dest="filename", help="Import variable")
    parser.add_argument("--export", action="store", dest="export_file", help="File to export attack time")
    parser.add_argument("--start", type=int, default=120, action="store", dest="start")
    parser.add_argument("--attack", action="store", dest="attack", help="Name of attack")

    args = parser.parse_args()

    main(args.ip, args.port, args.period, args.duration, args.filename,
         args.export_file, args.attack, args.start)
