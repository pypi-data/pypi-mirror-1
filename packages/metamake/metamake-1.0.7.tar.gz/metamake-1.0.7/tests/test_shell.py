from unittest import TestCase
from metamake._shell import shell, ShellCommandFailedError


class CoreTestCase(TestCase):
    
    def test_shell_command_raises_exception_when_command_fails(self):
        
        self.assertRaises(ShellCommandFailedError, lambda: shell("bad_command_that_doesnt_exist"))
        