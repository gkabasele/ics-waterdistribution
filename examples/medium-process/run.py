import shutil
import os
import time
import pdb
import medium_process
import threading
import argparse
import subprocess
import plc_generator
import logging
import store_watcher
from constants import *


logging.basicConfig(filename=LOG, mode='w', format='[%(asctime)s][%(levelname)s][%(pathname)s-%(lineno)d] %(message)s', level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("--create", dest="create_dir", action="store_true", help="Create export directory for variable processes")
parser.add_argument("--nb", dest="nb_round", type=int, default=5, action="store", help="Number of iteration for the process execution") 

parser.add_argument("--export_process", dest="export_process", action="store", help="File to see state of process variable over time")

parser.add_argument("--do_attack", action="store_true", default=False, dest="do_attack", help="perform the slow down attack on physical process")
parser.add_argument("--export_attack", action="store", dest="atk_time", help="perform the slow down attack on physical process")
args = parser.parse_args()

if os.path.exists(PLCS_LOG):
    shutil.rmtree(PLCS_LOG)


if os.path.exists(STORE):
    shutil.rmtree(STORE)

if os.path.exists(PLCS_DIR):
    shutil.rmtree(PLCS_DIR)

if args.create_dir:
    if os.path.exists(EXPORT_VAR):
        shutil.rmtree(EXPORT_VAR)
    os.mkdir(EXPORT_VAR)

os.mkdir(STORE)
os.mkdir(PLCS_DIR)
os.mkdir(PLCS_LOG)

plc_generator.create_plc_scripts()

cre = "--create" if args.create_dir else ""
t = threading.Thread(name='process', target=store_watcher.start, args=(STORE, args.nb_round, 
                                                                       args.do_attack, args.atk_time))
t.start()

processes = {}
processes_output = {}

for port,filename in enumerate(os.listdir(PLCS_DIR), 0):
    if filename.endswith(".py"):
        proc = subprocess.Popen(["python", PLCS_DIR+"/"+filename, "--ip", "127.0.0.1", "--port", str(5020+port), "--store", STORE, "--duration", str(args.nb_round), "--period", str(PLC_PERIOD), "--export", EXPORT_VAR, cre], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes[filename] = proc

mtu_proc = subprocess.Popen(["python", "script_mtu.py", "--ip", "127.0.0.1", "--port", str(3000), "--duration", str(args.nb_round), "--import", EXPORT_VAR, "--export", args.export_process], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#(mtu_out, mtu_err) = mtu_proc.communicate()

#for k,v in processes.iteritems():
#    (proc_out, proc_err) = v.communicate()
#    processes_output[k] = (proc_out, proc_err)
#    print proc_out
#    print proc_err
#    #v.wait()
#
#t.join()
#
#print mtu_out
#print mtu_err

#for k, v in processes_output.items():
#    out, err = v
#    print "{}".format(k)
#    print out
#    print err
