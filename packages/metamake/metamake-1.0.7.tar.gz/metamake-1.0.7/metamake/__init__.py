# TODO: bootstrap needs to check for the metamake-bootstrap header
from __future__ import generators
import sys
from logging import getLogger, StreamHandler, INFO
from metamake._path import loggable_path as path
from metamake._bootstrap import serialize_metamake_to_makefile
from metamake._flags import Flag
from metamake._dependencies import Dependency
from metamake._shell import shell

__all__ = [
    
    "task",
    "shell"
    "path",
    "Flag",
    "Dependency",
    
    "list_tasks",
    "run_task",
    "run_default_task",
]

_DEFAULT_STDERR_LOGS = ["metamake.filesystem", "metamake.shell"]
_all_tasks = {}
_ordered_task_keys = []
_first_task_name = None
_default_task_name = None
_did_setup_stderr_logging = False
_bootstrap_filename = None

def bootstrap(bootstrap_filename):
    """call this function to set a bootstrap filename for
    serializing metamake to a Makefile for backwards-compat"""
    global _bootstrap_filename
    _bootstrap_filename = bootstrap_filename

def task(method=None, default=False):
    """this decorator should be used to mark Python functions
    in your Makefile.py as tasks that can be executed on
    the commandline.  You can specify 'default = True' if
    you want that task to be the default"""
    def decorate(method, default):

        global _first_task_name
        global _default_task_name
        
        if _first_task_name == None:
            _first_task_name = method.__name__
        
        if default == True:
            _default_task_name = method.__name__
        
        _all_tasks[method.__name__] = method
        _ordered_task_keys.append(method.__name__)
        return method
        
    if method == None:
        def subdecorator(method):
            return decorate(method, default)
        return subdecorator
    else:
        return decorate(method, default)

def list_tasks():
    """lists all tasks that have been defined in your
    Makefile.py file"""
    _ensure_stderr_logs_are_active()
    if _bootstrap_filename:
        serialize_metamake_to_makefile(_bootstrap_filename)
    Flag("noupdate").explain("set to 'true' if you want to disable automatic Dependency version control updates")
    print
    if len(_all_tasks) is 0:
        print "(no tasks defined)"
    else:
        for task_name in _ordered_task_keys:
            task = _all_tasks[task_name]
            shortdoc = task.__doc__
            if not shortdoc:
                shortdoc = "(no documentation)"
            if "\n" in shortdoc:
                shortdoc = shortdoc.split("\n")[0] + "..."
            format_string = "%%(name)-%ss # %%(optional_default_doc)s%%(doc)s" % max([len(name)+1 for name in _all_tasks.keys()])
            print format_string % dict(
                name = task.__name__,
                doc = shortdoc,
                optional_default_doc = {_default_task_name: "(default) "}.get(task_name, ""),
            )
    print
    for flagname, explanation in Flag._flag_explanation_lookup.iteritems():
        print "[%(flagname)s=?] %(explanation)s" % locals()
    print

def run_task(task_name):
    """runs a task (by name)"""
    _ensure_stderr_logs_are_active()
    if _bootstrap_filename:
        serialize_metamake_to_makefile(_bootstrap_filename)
    global _all_tasks
    if len(_all_tasks) is 0:
        print >> sys.stderr, "*** no tasks were defined (did you forget to define tasks in the 'Makefile.py' in your working directory?)"
        raise SystemExit(1)
    if task_name in _all_tasks:
        _all_tasks[task_name]()
    else:
        print >> sys.stderr, "*** there is no task with the name '%s'" % task_name
        raise SystemExit(1)

def run_default_task():
    """runs the task marked as default (using '@task(default=True)')"""
    global _first_task_name
    global _default_task_name
    
    if _default_task_name:
        run_task(_default_task_name)
    
    else:
        run_task(_first_task_name)

def _ensure_stderr_logs_are_active():
    """helper method to ensure that file system actions
    are written to stderr"""
    global _did_setup_stderr_logging
    if not _did_setup_stderr_logging:
        stderr_logging_handler = StreamHandler(sys.stderr)
        for logger_name in _DEFAULT_STDERR_LOGS:
            logger = getLogger(logger_name)
            logger.setLevel(INFO)
            logger.addHandler(stderr_logging_handler)
        _did_setup_stderr_logging = True

def metamake_bin():
    """the actual metamake commandline tool (main function)"""
    
    import sys
    
    # allow help from the commandline
    if "--help" in sys.argv:
        print >> sys.stderr, "latest metamake documentation can be found at http://pypi.python.org/pypi/metamake/"
        raise SystemExit(0)

    # the user didn't want help, they are actually trying to exec metamake
    import os
    sys.path.insert(0, os.getcwd())
    import metamake
    
    try:
        import Makefile
    except ImportError, e:
        
        errmsg = str(e)
        if "Makefile" in errmsg:
            # this was probably unable to find Makefile.py
            print >> sys.stderr, "*** Makefile.py could not be loaded.  It appears that you have not defined one."
        else:
            # this was probably due to an import from within Makefile.py
            print >> sys.stderr, "*** Makefile.py could not be loaded.  It appears that one of your imports is failing: '%s'." % errmsg
        
        # fail with nonzero error code
        raise SystemExit(1)
    
    # any commandline argument without a '=' in it is a task that we want to run
    tasknames = [arg for arg in sys.argv[1:] if "=" not in arg]
    
    # decide what task(s) to run
    if len(tasknames) is 0:
        
        # no tasknames means we should run the default one
        run_default_task()
        
    elif "ls" in tasknames:
        
        # the 'ls' task is a special task that lists all other tasks
        list_tasks()
    else:
        
        # otherwise, iterate through all task names and run them
        for taskname in tasknames:
            run_task(taskname)
