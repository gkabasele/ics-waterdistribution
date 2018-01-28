import unittest
import shutil
from pyics.component import *
from pyics.physical_process import *
from pyics.plc import *
from simplekv.fs import FilesystemStore

class TestPLC(unittest.TestCase):

    # called before each case
    def setUp(self):
        self.store = "variable_store"
        self.lvl = "level"
        self.vlv = "valve"
        self.press = "pressure"
        self.temp = "temp"
        
        self.plc = PLC('localhost', 5020, self.store, "plc", 
                        holding_reg = 3,
                        input_reg = 2,
                        level = (HR,3), 
                        valve = (CO,1),
                        pressure = (IR,1),
                        temp = (IR,1))

    # called after each case
    def tearDown(self):
        if os.path.exists(self.store):
            shutil.rmtree(self.store)

        self.plc.server_close()

    def test_setting_address(self):
        self.assertEquals(len(self.plc.addr_to_var[HR]), 1)
        self.assertEquals(len(self.plc.addr_to_var[IR]), 2)

        self.assertEquals(self.plc.index[HR], 3)
        self.assertEquals(self.plc.index[IR], 2)

        self.assertEquals(len(self.plc.variables), 4) 
        self.assertEquals(self.plc.variables[self.lvl].get_size(), 3)
        self.assertEquals(self.plc.variables[self.temp].get_addr(), 1)

    def test_set_get_store(self):
        self.plc.put_store(self.vlv, True)
        self.assertTrue(self.plc.get_store(self.vlv, 'b'))

    def test_set_get_register(self):
        self.plc.set(self.vlv, True)
        self.plc.set(self.press, 10)
        self.assertTrue(self.plc.get(self.vlv)[0])
        self.assertEquals(self.plc.get(self.press)[0], 10)

    def test_export_variables(self):
        filename = "plc_test"
        if os.path.exists(filename):
                shutil.rmtree(filename)

        os.mkdir(filename)
        self.plc.export_variables(filename)
        f = open(filename+'/'+self.plc.name+'.ex', 'r')
        lines = f.readlines()
        self.assertEquals(len(lines), 4)


        prefix = "localhost,5020:"
        var = [
                prefix+"level:h,0,3\n",
                prefix+"valve:c,0,1\n",
                prefix+"pressure:i,0,1\n",
                prefix+"temp:i,1,1\n"
              ]

        print lines
        for i in var:
            self.assertTrue(i in lines)
    
        f.close()
        os.remove(filename+"/"+self.plc.name+'.ex')
        os.rmdir(filename)
        

    def test_update_registers(self):
        store = FilesystemStore(self.store)
        self.plc.set(self.vlv, False)
        self.plc.set(self.temp, 5)
        self.assertFalse(self.plc.get(self.vlv)[0])
        self.assertEquals(self.plc.get(self.temp)[0], 5)
        store.put(self.vlv, str(True))
        store.put(self.temp, str(10))
        self.plc.update_registers()
        self.assertTrue(self.plc.get(self.vlv)[0])
        self.assertEquals(self.plc.get(self.temp)[0],10)
        
if __name__ == '__main__':
    unittest.main()
