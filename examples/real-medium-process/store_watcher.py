import time
import simpy
import simpy.rt
import threading
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from medium_process import MediumProcess
from constants import *

class VarProcessHandler(FileSystemEventHandler):

    def __init__(self, process):
        self.process = process

        super(VarProcessHandler, self).__init__()

    def display_msg(self, var):
        print("Change on {}".format(var))

    # Monitor changes on the variable process store
    def on_modified(self, event):
        varname = str(event.src_path).replace(self.process.store.root +'/', '').encode('utf-8')
        #Check if it is a boolean value
        if varmap[varname][0] == CO:
            do_something = self.process.get(varname, "b")
            self.process.lock.acquire()
            if do_something:
                if varname == V1:
                    #self.process.pass_fluid(V1, A1, T1)
                    self.display_msg(V1)

                elif varname == V2:
                    #self.process.pass_fluid(V2, A2, T1)
                    self.display_msg(V2)

                elif varname == M1:
                    self.display_msg(M1)
                    #self.process.running_motor()

                elif varname == M1a:
                    self.display_msg(M1a)
                    #self.process.running_motor()

                elif varname == VT1:
                    self.display_msg(VT1)
                    #self.process.pass_fluid(VT1, T1, S1)

                elif varname == VS1:
                    self.display_msg(VS1)
                    #self.process.pass_fluid(VS1, S1, S2)

                elif varname == VTC:
                    self.display_msg(VTC)
                    #if self.process.wagonStart:
                    #    self.process.pass_fluid(VTC, TC, WC)
                    #elif self.process.wagonEnd:
                    #    print "[Error] Releasing tank charcoal for nothing"

                elif varname == WM:
                    self.process.move_wagon()

                elif varname == WO:
                    self.display_msg(WO)

                    #if self.process.wagonStart:
                    #    self.process.empty_wagon(WC)
                    #elif self.process.wagonEnd:
                    #    self.process.pass_fluid(WO, WC, S2)

                elif varname == M2:
                    self.display_msg(M2)
                    #self.process.running_motor()

                elif varname == M2a:
                    self.display_msg(M2a)
                    #self.process.running_motor()

                elif varname == VS2:
                    self.display_msg(VS2)
                    #self.process.pass_fluid(VS2, S2, TF)

                elif varname == VTF:
                    self.display_msg(VTF)
                    #self.process.release_tank(VTF, TF)
            self.process.lock.release()

def start(store, nb_round, do_attack_motor, do_attack_valve, atk_time):
    env = simpy.rt.RealtimeEnvironment(factor=1)
    lock = threading.Lock()
    fname = None
    if atk_time is not None:
        fname = open(atk_time, "w")

    process = MediumProcess(env, store, "Medium Process", lock, do_attack_motor,
                            do_attack_valve, fname)
    t = threading.Thread(name='medium', target=env.run, kwargs={'until':nb_round})
    t.start()
    handler = VarProcessHandler(process)
    observer = Observer()
    observer.schedule(handler, path=store, recursive=True)
    print "Starting observer"
    observer.start()
    #time.sleep(DURATION)
    time.sleep(nb_round+10)
    print "Stopping observer"
    observer.stop()

    if fname is not None:
        fname.close()

