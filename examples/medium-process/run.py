import shutil
import os
import medium_process
import threading
import argparse
import subprocess
from constants import *
from plc_generators import *


parser = argparse.ArgumentParser()
parser.add_argument("--create", dest="create_dir", action="store_true")
args = parser.parser_args

if os.path.exists(STORE):
    shutil.rmtree(STORE)

if os.path.exists(PLCS_DIR):
    shutil.rmtree(PLCS_DIR)

os.mkdir(STORE)
os.mkdir(PLCS_DIR)


t = threading.Thread(name='process', target=medium_process.start, args=(STORE,))
t.start()


processes = {}
processes_output = {}
cre = "--create" if args.create_dir else ""

for port,filename in enumerate(os.listdir(PLCS_DIR), 0):
    if filename.endswith(".py"):
        proc = subprocess.Popen(["python", filename, "--ip", "localhost", "--port", str(5020+port), --store, STORE, "--duration", str(DURATION), "--ex", EXPORT_VAR, cre], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes[filename] = proc

mtu_proc = subprocess.Popen(["python", "script_mtu.py", "--ip", "--port", str(3000), "--duration", str(DURATION) , "--import", EXPORT_VAR], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(mtu_out, mtu_err) = mtu_proc.communicate()

for k,v in processes.iteritems():
    (proc_out, proc_err) = v.communicate()
    processes_output[k] = (proc_out, proc_err)
    v.wait()

mtu_proc.wait()
t.join()




t.join()
