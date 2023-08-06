from logging import getLogger
# from os import system
import subprocess


class ShellCommandFailedError(Exception):
    """raised whenever a shell command fails"""
    
    stdout = property(lambda self: self.__stdout)
    stderr = property(lambda self: self.__stderr)
    returncode = property(lambda self: self.__returncode)
    
    # TODO: deprecate
    retcode = property(lambda self: self.__returncode)
    
    def __init__(self, cmd, stdout, stderr, returncode):
        Exception.__init__(self, "command '%s' failed with status %s" % (cmd, returncode))
        self.__returncode = returncode
        self.__stdout = stdout
        self.__stderr = stderr


class Result(object):
    
    returncode = property(lambda self: self.__returncode)
    stdout = property(lambda self: self.__stdout)
    stderr = property(lambda self: self.__stderr)
    
    def __init__(self, stdout, stderr, returncode):
        self.__returncode = returncode
        self.__stdout = stdout
        self.__stderr = stderr


def shell(cmd, quiet=False, allow_failure=False):
    """runs a shell command, echoing output and raising
    a SystemExit if the command fails"""
    logger = getLogger("metamake.shell")
    if not quiet:
        logger.info(cmd)
    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = pipe.communicate()
    # TODO: do line-by-line output
    print stdout.strip()
    print stderr.strip()
    returncode = pipe.returncode
    if returncode is not 0 and not allow_failure:
        raise ShellCommandFailedError(cmd, stdout=stdout, stderr=stderr, returncode=returncode)
    return Result(stdout=stdout, stderr=stderr, returncode=returncode)