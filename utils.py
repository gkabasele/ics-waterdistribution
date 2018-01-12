import threading
import sys
import time
import itertools

HR = "hr"
CO = "co"
IR = "ir"
DI = "di"

GRAVITY = 9.8
INBUF = "inbuf"
OUTBUF = "outbuf"

registers_type = {DI:2, IR:4, HR:3, CO:1}

class PeriodicTask(threading.Thread):
    # period in second
    def __init__(self, name, period, task, duration=None,*args, **kwargs):
        threading.Thread.__init__(self)
        self.name = name
        self.period = period
        self.duration = duration 
        self.task = task
        self.args = args
        self.kwargs = kwargs

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
            if self.duration and (current_time - start_time) >= self.duration:
                break
            self.task(*self.args, **self.kwargs)
            time.sleep(next(g))

    def run(self):
        self.do_every()


class CustomDict(dict):
    ''' Custom dictionnary to ensure that a key is inserted only once
        
    '''
    def __setitem__(self, k, v):
        if k in self.keys():
            raise ValueError("Key already exists")
        else:
            return super(CustomDict, self).__setitem__(k, v)

def first_true(iterable, default=False, pred=None):
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    """
    return next(filter(pred, iterable), default)

def wait_until(predicate, timeout=30, period=0.25, *args, **kwargs):
    end = time.time() + timeout
    res = False
    while time.time() < end:
        if predicate(*args, **kwargs):
            res = True
            break
        time.sleep(period)
    return res
