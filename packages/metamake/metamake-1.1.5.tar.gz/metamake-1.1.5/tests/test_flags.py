from unittest import TestCase
import sys
from metamake._flags import Flag


def _reset_flag_parser():
    # warning: this uses internal implementation, and will need
    # to be updated accordingly when the implementation changes
    Flag._flag_value_lookup = None
    Flag._flag_explanation_lookup = {}
    Flag._flag_type_lookup = {}
    Flag._flag_allowablevals_lookup = {}

def _add_flag(argstr):
    sys.argv.append(argstr)


class FlagTestCase(TestCase):
    
    def setUp(self):
        _reset_flag_parser()
    
    def tearDown(self):
        _reset_flag_parser()
    
    def test_boolean_flag_detects_true_value(self):
        for value in ["True", "T", "TRUE", "true", "t", "1", "y", "yes", "on"]:
            _reset_flag_parser()
            _add_flag("boolean_flag=%s" % value)
            f = Flag("boolean_flag").explain("blah", convert=bool)
            self.assertEqual(f.value, True)
    
    def test_boolean_flag_detects_false_value(self):
        for value in ["False", "F", "FALSE", "false", "f", "0", "n", "no", "off"]:
            _reset_flag_parser()
            _add_flag("boolean_flag=%s" % value)
            f = Flag("boolean_flag").explain("blah", convert=bool)
            self.assertEqual(f.value, False)
    
    def test_integer_flag_gets_converted_properly(self):
        _add_flag("integer_flag=5")
        f = Flag("integer_flag").explain("blah", convert=int)
        self.assertEqual(f.value, 5)    