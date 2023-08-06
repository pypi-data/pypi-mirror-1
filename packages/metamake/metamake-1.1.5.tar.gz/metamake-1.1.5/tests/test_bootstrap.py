from unittest import TestCase
import os
from tempfile import gettempdir
import metamake
from metamake._bootstrap import serialize_metamake_to_makefile, standalone_deserialize_metamake_from_makefile
from metamake._path import path

def _remove_bootstrap_dir():
    # warning: this depends on internal implementation
    bootstrap_dir = path(gettempdir()) / "metamake_bootstrap"
    bootstrap_dir.rmtree()


class BootstrapTestCase(TestCase):
    
    def tearDown(self):
        test_makefile = path("Makefile.test")
        if test_makefile.exists():
            test_makefile.remove()
            _remove_bootstrap_dir()
    
    def test_can_serialize_module_to_makefile(self):
        
        serialize_metamake_to_makefile("Makefile")
        standalone_deserialize_metamake_from_makefile("Makefile")
        path("Makefile").remove()
    
    def test_can_use_makefile_bootstrap_to_run_makefilepy(self):
        currentdir = os.path.dirname(__file__)
        serialize_metamake_to_makefile("Makefile")
        self.assert_("# version %s" % metamake.__version__ in open(path("Makefile")).readlines()[0], "first line should be the version")
        self.assert_(os.system("cd %(currentdir)s && make" % locals()) == 0)
        self.assert_(os.system("cd %(currentdir)s && make testA" % locals()) == 0)
        path("Makefile").remove()
    
    def test_makefile_bootstrap_is_generated(self):
        currentdir = os.path.dirname(__file__)
        # serialize to another makefile
        serialize_metamake_to_makefile("Makefile")
        
        # make with that
        self.assert_(os.system("cd %(currentdir)s && make" % locals()) == 0)
        self.assert_(os.system("cd %(currentdir)s && make testA" % locals()) == 0)
        
        # ensure that the test makefile was created as well
        self.assert_(os.path.exists(os.path.join(currentdir, "Makefile.test")))
        self.assert_(os.system("cd %(currentdir)s && make -f Makefile.test" % locals()) == 0)
        self.assert_(os.system("cd %(currentdir)s && make -f Makefile.test testA" % locals()) == 0)
        
        path("Makefile").remove()
