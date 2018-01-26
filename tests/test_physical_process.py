import unittest
from pyics.component import *
from pyics.physical_process import *

class TestPhysicalProcess(unittest.TestCase):

    # called before each case
    def setUp(self):
        self.store = "variable_store"
        self.tank1_lvl = "t1_lvl"
        self.tank1_vlv = "t1_vlv"
        self.tank2_lvl = "t2_lvl"
        self.tank2_vlv = "t2_vlv"

        self.phys = PhysicalProcess(self.store)

    # called after each case
    def tearDown(self):
        if os.path.exists(self.store):
            shutil.rmtree(self.store)

    def test_add_interaction(self):
        tank1 = self.phys.add_component(Tank, 50, 30, 10, valve=True, name='tank1') 
        pipeline =  self.phys.add_component(Pipeline, 20, 40)
        tank2 = self.phys.add_component(Tank, 50, 30, 10, valve=False, name='tank2') 
        (tank1_out, pipeline_in) = self.phys.add_interaction(tank1, pipeline)
        (pipeline_out, tank2_in) = self.phys.add_interaction(pipeline, tank2)
        self.assertTrue(len(self.phys.links) == 2)

        self.phys.add_interaction(tank1, pipeline)
        self.assertTrue(len(self.phys.links) == 2)
        self.assertEquals(self.phys.links['tank1']['pipeline'], (0,0))

    def test_add_variable(self):
        p = Pipeline(self.store, 20, 30, name="test")
        self.phys.add_variable(p, "non_existing_var")
        self.assertTrue(len(self.phys.variables) == 0)

        tank = self.phys.add_component(Tank, 50, 30, 10)
        self.phys.add_variable(tank, self.tank1_lvl)
        self.assertTrue(len(self.phys.variables) == 1)
        

    # each test must start by test
    def test_name(self):
        pass

if __name__ == '__main__':
    unittest.main()
