import threading
import sys
import time

HR = "hr"
CO = "co"
IR = "ir"
DI = "di"

registers_type = {DI:2, IR:4, HR:3, CO:1}

class PeriodicTask(threading.Thread):
    # period in second
    def __init__(self, name, period, duration, task,*args):
        threading.Thread.__init__(self)
        self.name = name
        self.period = period
        self.duration = duration
        self.task = task
        self.args = args

    def do_every(self):
        def g_tick():
            t = time.time()
            count = 0
            while True:
                count += 1
                yield max(t + count*self.period - time.time(), 0)
        g = g_tick()
        start_time = time.time()
        while True:
            current_time = time.time()
            if (current_time - start_time) >= self.duration:
                break
            self.task(self.args)
            time.sleep(next(g))

    def run(self):
        self.do_every()
