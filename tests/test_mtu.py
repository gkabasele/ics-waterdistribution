import unittest
import threading
from icstest import ICSTest
from pyics.component import *
from pyics.physical_process import *
from pyics.plc import *
from pyics.mtu import *

class PLCTestThread(threading.Thread):

    def __init__(self, plc):
        threading.Thread.__init__(self)
        self.plc = plc

    def run(self):
        self.plc.serve_forever()

class TestMTU(unittest.TestCase):

    # called before each case
    def setUp(self):
        self.store = "variable_store"
        self.lvl = "level"
        self.vlv = "valve"
        self.press = "pressure"
        self.temp = "temp"

        self.plc = PLC("localhost", 5020, self.store,
                       "plc",
                       level = (HR,1),
                       valve = (CO,1),
                       pressure = (IR,1),
                       temp = (IR,1))
        self.plc.set(self.lvl, 0)
        self.plc.set(self.press, 10)
        self.plc.set(self.temp, 5)
        self.plc.set(self.vlv, False)


        self.filename = "plc_test"
        if os.path.exists(self.filename):
            shutil.rmtree(self.filename)

        os.mkdir(self.filename)
        self.plc.export_variables(self.filename) 

        self.mtu = ICSTest("localhost", 3000)
        self.mtu.get_dir(self.filename)


    # called after each case
    def tearDown(self):
        if os.path.exists(self.store):
            shutil.rmtree(self.store)

        if os.path.exists(self.filename):
            shutil.rmtree(self.filename)

        self.mtu.close()
        #self.plc.shutdown()
        #self.plc.server_close()
    
    def test_cond(self):

        def func_low(val):
            val.append(-1)
        def func_high(val):
            val.append(2) 

        fl = func_low
        fh = func_high

        val = []

        cond = ProcessRange(5, 10, fl=fl, fh=fh)
        cond.execute_action(3, val) 
        self.assertTrue(-1 in val)

        cond.execute_action(11, val)
        self.assertTrue(2 in val)
        self.plc.server_close()


    #def test_get_variable(self):
    #    plc_thread =  PLCTestThread(self.plc)
    #    plc_thread.start()
    #    self.assertEquals(self.mtu.get_variable(self.lvl), 0) 
    #    self.assertEquals(self.mtu.get_variable(self.temp), 5)
    #    self.assertEquals(self.mtu.get_variable(self.press), 10)
    #    self.assertFalse(self.mtu.get_variable(self.vlv))
    #    self.plc.shutdown()
    #    self.plc.server_close()

    def test_write_variable(self):
        plc_thread = PLCTestThread(self.plc)
        plc_thread.start()
        self.mtu.write_variable(self.vlv, True)
        self.assertTrue(self.mtu.get_variable(self.vlv))
        self.plc.shutdown()
        #plc_thread.join()

if __name__ == "__main__":
    unittest.main()
