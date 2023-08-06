from logging import getLogger
from os import system


class ShellCommandFailedError(Exception):
    """raised whenever a shell command fails"""
    
    retcode = property(lambda self: self.__retcode)
    
    def __init__(self, cmd, retcode):
        Exception.__init__(self, "command '%s' failed with status %s" % (cmd, retcode))
        self.__retcode = retcode


def shell(cmd, quiet=False, allow_failure = False):
    """runs a shell command, echoing output and raising
    a SystemExit if the command fails"""
    logger = getLogger("metamake.shell")
    if not quiet:
        logger.info(cmd)
    retcode = system(cmd)
    if retcode is not 0 and not allow_failure:
        raise ShellCommandFailedError(cmd, retcode)