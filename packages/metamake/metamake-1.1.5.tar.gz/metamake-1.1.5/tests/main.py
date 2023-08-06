import sys
import unittest
import logging

class _UnittestLogHandler(object):
    """acts as a StreamHandler on stdout (does some additional formatting)"""

    def write(self, msg):
        sys.stdout.write("%s" % msg)
    
    def __getattr__(self, name):
        return getattr(sys.stdout, name)

def monitor_log(log_name):
    """monitors a log for unit tests"""
    logger = logging.getLogger( log_name )
    logger.addHandler( logging.StreamHandler( _UnittestLogHandler() ) )
    logger.setLevel( logging.INFO )


###############################################################################
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

COVERAGE = [
    '--with-coverage',
    '--cover-package=metamake',
]

FLAGS = ["-v"]

# monitor_log("metamake.filesystem")

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
###############################################################################

if __name__ == "__main__":

    import sys
    import os
    import nose

    # prepend pytoss source to the search path to ensure that all pytoss
    # imports happen from the source directory
    sys.path.insert( 0, os.path.join( os.path.dirname(__file__), ".." ) )

    # run nosetests
    nose.core.TestProgram(defaultTest = "tests", argv = (sys.argv + FLAGS))

