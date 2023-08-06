import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(__file__+"../../../pybus"))
from pybus_core import PyBus

class PyBusTestBase (unittest.TestCase):

    def setUp(self):
        self.bus = PyBus()

