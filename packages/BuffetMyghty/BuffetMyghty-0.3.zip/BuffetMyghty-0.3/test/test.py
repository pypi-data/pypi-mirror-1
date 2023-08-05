import os
import sys
import unittest

sys.path.insert(0, os.path.split(os.getcwd())[0])

from buffetmyghty.myghtysupport import MyghtyTemplatePlugin


xtravars = lambda: {'myglobal': 'pass in custom globals!'}

# a couple config options
# component_root is required
# raise_error makes exceptions propagate down to lower levels
config = {'component_root': 'templates',
          'raise_error': True}

class Problem(object):
    def __str__(self):
        raise Exception

class TestBuffetMyghty(unittest.TestCase):
    
    def setUp(self):
        self.engine = MyghtyTemplatePlugin(xtravars, config)
    
    def test_01_basic(self):
        params = {'name': 'Bobo'}
        self.assertEqual(self.engine.render(info={}, template='myghty_test'),
                         '\nHello World!\n\n')
        self.assertEqual(self.engine.render(info=params, template='myghty_test'),
                         '\nHello Bobo!\n\n')
    
    def test_02_exceptions(self):
        params = {'name': Problem()}
        self.assertRaises(Exception,
                          self.engine.render,
                          info=params,
                          template='myghty_test')
    
    def test_03_extravars(self):
        self.assertEqual(self.engine.render(info={}, template='extra_vars'),
                         'pass in custom globals!\n')
        
if __name__ == '__main__':
    unittest.main()
