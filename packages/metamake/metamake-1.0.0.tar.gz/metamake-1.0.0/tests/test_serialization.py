from unittest import TestCase
import os
from metamake._bootstrap import serialize_metamake_to_makefile, standalone_deserialize_metamake_from_makefile
from metamake._path import path

class BootstrapTestCase(TestCase):
    
    def test_can_serialize_module_to_makefile(self):
        
        serialize_metamake_to_makefile("Makefile")
        standalone_deserialize_metamake_from_makefile("Makefile")
        path("Makefile").remove()
    
    def test_can_use_makefile_bootstrap_to_run_makefilepy(self):
        currentdir = os.path.dirname(__file__)
        serialize_metamake_to_makefile("Makefile")
        self.assert_(os.system("cd %(currentdir)s && make" % locals()) == 0)
        self.assert_(os.system("cd %(currentdir)s && make testA" % locals()) == 0)
        path("Makefile").remove()
