# TODO: bootstrap needs to check for the metamake-bootstrap header
from __future__ import generators
import sys
from logging import getLogger, StreamHandler, INFO
from metamake._path import loggable_path as path
from metamake._bootstrap import serialize_metamake_to_makefile
from metamake._flags import Flag
from metamake._dependencies import Dependency
from metamake._shell import shell, ShellCommandFailedError
from metamake._namespaces import namespace, get_current_namespace

__all__ = [
    
    "task",
    "namespace",
    "shell"
    "path",
    "Flag",
    "Dependency",
    "ShellCommandFailedError",
    
    "list_tasks",
    "run_task",
    "run_default_task",
]

__version__ = "1.1.4"

_DEFAULT_STDERR_LOGS = ["metamake.filesystem", "metamake.shell"]
_all_tasks = {}
_ordered_task_keys = []
_first_task_name = None
_default_task_name = None
_did_setup_stderr_logging = False
_bootstrap_filename = None
_defined_flags = False

def bootstrap(bootstrap_filename):
    """call this function to set a bootstrap filename for
    serializing metamake to a Makefile for backwards-compat"""
    global _bootstrap_filename
    _bootstrap_filename = bootstrap_filename

def task(method=None, default=False):
    """this decorator should be used to mark Python functions
    in your Makefile.py as tasks that can be executed on
    the commandline.  You can specify 'default = True' if
    you want that task to be the default."""
    def decorate(method, default):

        global _first_task_name
        global _default_task_name
        
        if _first_task_name == None:
            _first_task_name = method.__name__
        
        if default == True:
            # TODO: how should we handle overwriting of the default task?
            _default_task_name = method.__name__
        
        # index under the function name and namespace
        namespace_list = get_current_namespace()
        if namespace_list:
            lookup_name = ":".join([x.__name__ for x in (namespace_list + [method])])
        else:
            lookup_name = method.__name__
        _all_tasks[lookup_name] = method
        _ordered_task_keys.append(lookup_name)
        
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
    _define_flags()
    _ensure_stderr_logs_are_active()
    if _bootstrap_filename:
        serialize_metamake_to_makefile(_bootstrap_filename)
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
                name=task_name,
                doc=shortdoc,
                optional_default_doc={_default_task_name: "(default) "}.get(task_name, ""),
            )
    if len(Flag._flag_explanation_lookup) > 0:
        print
        for flagname, explanation in Flag._flag_explanation_lookup.iteritems():
            print "[%(flagname)s=?] %(explanation)s" % locals()
    print

def run_task(task_name, from_makefile=False):
    """runs a task (by name)"""
    _define_flags()    
    _ensure_stderr_logs_are_active()
    if _bootstrap_filename:
        serialize_metamake_to_makefile(_bootstrap_filename)
    global _all_tasks
    if len(_all_tasks) is 0:
        print >> sys.stderr, "*** no tasks were defined (did you forget to define tasks in the 'Makefile.py' in your working directory?)"
        raise SystemExit(1)
    if task_name in _all_tasks:
        try:
            _all_tasks[task_name]()
        except Exception, e:
            
            # print the error
            print "*** error: %s, %s" % (e.__class__.__name__, str(e))
            
            # show a full traceback if desired
            # if Flag("tracebacks").given and Flag("tracebacks").value is True:
            if "--trace" in sys.argv or (Flag("mmtrace").given and Flag("mmtrace").value == True):
                print "================================"
                import traceback
                traceback.print_tb(sys.exc_info()[2])
            else:
                # tell the user they can get a traceback
                if from_makefile:
                    # use mmtrace=1 as detail flag
                    print "(use mmtrace=1 for more detail)"
                else:
                    # use --trace as detail flag
                    print "(use --trace for more detail)"
                    
            raise SystemExit(1)
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
        # by default, list all tasks if no other default task has been set
        list_tasks()

def _define_flags():
    """helper method to ensure that the global flags are set"""
    global _defined_flags
    if not _defined_flags:
        pass
        # Flag("tracebacks").explain("set to 'true' for full tracebacks on error", convert=bool, allow=[True, False])
        # _defined_flags = True

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
    import imp
    import metamake
    
    try:
        makefile_path = os.path.join(os.path.abspath(os.getcwd()), "Makefile.py")
        imp.load_module("Makefile", open(makefile_path, "r"), makefile_path, ('.py', 'U', 1))
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
    tasknames = [arg for arg in sys.argv[1:] if "=" not in arg and arg != "--trace"]
    
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
