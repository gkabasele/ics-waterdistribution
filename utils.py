import threading
import sys
import time
import itertools

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


def first_true(iterable, default=False, pred=None):
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    """
    return next(filter(pred, iterable), default)
