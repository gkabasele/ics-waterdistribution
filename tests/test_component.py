import unittest
import os 
import shutil
from pyics.component import *

class TestComponent(unittest.TestCase):

    # called before each case
    def setUp(self):
        self.store = "variable_store"
        t_height = 50
        t_diameter =30
        t_hole = 10


        self.tank1 = Tank(self.store,t_height, t_diameter, t_hole, level=10)
        self.tank1_in = ComponentQueue(1)
        self.tank1_out = ComponentQueue(1)
        self.tank1.add_inbuf(self.tank1_in)
        self.tank1.add_outbuf(self.tank1_out)

        self.tank2 = Tank(self.store,t_height, t_diameter, t_hole, level=10, valve=True)
        self.tank2_in = ComponentQueue(1)
        self.tank2_out = ComponentQueue(1)
        self.tank2.add_inbuf(self.tank2_in)
        self.tank2.add_outbuf(self.tank2_out)


    # called after each case
    def tearDown(self):
        if os.path.exists(self.store):
            shutil.rmtree(self.store)

    def test_tank_ctr(self):
        self.assertEquals(self.tank1.level, 10)
        self.assertFalse(self.tank1.valve)

    # each test must start by test
    def test_has_buf(self):
        self.assertTrue(self.tank1.has_inbuf())
        self.assertTrue(self.tank1.has_outbuf())

    def test_buf(self):
        self.tank1_in.put(5)
        self.assertEquals(self.tank1.read_buffer(0), 5)

    def test_sensor(self):
        self.tank1.set('level', 10)
        level = self.tank1.get('level', int)
        self.assertEquals(level, 10)
        self.tank1.set('valve', True)
        valve = self.tank1.get('valve', 'b')
        self.assertTrue(valve)
        self.tank1.set('valve', False)
        valve = self.tank1.get('valve', 'b')
        self.assertFalse(valve)

    def test_sensor_error(self):
        self.tank1.set('level', 10)
        with self.assertRaises(TypeError):
            self.tank1.get('level', 'b')

    def test_tank_computation(self):

        # Valve closed => increase of water
        tank1_lvl = "t1_level"
        tank1_vlv = "t1_valve"
        self.tank1_in.put(5) 
        self.tank1.computation(tank1_lvl, tank1_vlv, inbuf=0, outbuf=0)
        self.assertEquals(self.tank1_out.get(), 0)
        self.assertAlmostEquals(self.tank1.level, 10.007, places=3) 

        # Valve open => decrease of water
        tank2_lvl = "t2_level"
        tank2_vlv = "t2_valve"
        self.tank2_in.put(5)
        self.tank2.computation(tank2_lvl, tank2_vlv, inbuf=0, outbuf=0)
        self.assertAlmostEquals(self.tank2_out.get(), 1099.946, places=3)
        self.assertAlmostEquals(self.tank2.level, 8.4509, places=3)
        
if __name__== '__main__':
    unittest.main()

