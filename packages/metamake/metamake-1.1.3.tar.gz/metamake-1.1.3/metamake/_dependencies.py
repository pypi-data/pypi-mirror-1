import platform
import warnings
from metamake._flags import Flag
from metamake._path import loggable_path
from metamake._shell import shell

def _make(target, path):
    """helper method for running make (tries to use nmake on windows)"""
    from metamake import shell
    if platform.system() == "Windows":
        makebin = "nmake"
    else:
        makebin = "make"
    shell("cd %(path)s && %(makebin)s %(target)s" % dict(
        path = path,
        makebin = makebin,
        target = target,
    ))


class Dependency(object):
    """represents an external dependency for your project.
    Given a URL, this object will figure out the type of version
    control and pull down the dependency into the requested path"""
    
    def __init__(self, url, path, build_cmd=None, clean_cmd=None):

        warnings.warn("Dependency objects are deprecated, please use your own custom dependency tracking", DeprecationWarning)
        
        self.__url = url
        self.__path = path

        if build_cmd:
            self.__build_cmd = build_cmd
        else:
            self.__build_cmd = lambda: _make("", self.__path)

        if clean_cmd:
            self.__clean_cmd = clean_cmd
        else:
            self.__clean_cmd = lambda: _make("clean", self.__path)
    
    def update(self):
        """updates this dependency from its version control"""
        
        if not Flag("noupdate").given or Flag("noupdate").value.lower() is not "true":
            
            # the 'noupdate' flag was not given, do an svn update
            if not loggable_path(self.__path).exists():
                
                # checkout did not exist yet, check it out first
                shell("svn co %(url)s %(path)s" % dict(
                    url = self.__url,
                    path = self.__path,
                ))
                
            else:
                
                # checkout existed, do an svn update
                shell("cd %(path)s && svn revert Makefile && svn up" % dict(
                    path = self.__path
                ))
        else:
            
            # the 'noupdate' flag was given on the commandline, don't do subversion updates
            print >> sys.stderr, "*** skipping Dependency Subversion updates"
    
    def build(self):
        """builds this dependency.  This will do an initial checkout
        if the project has not been checked out yet"""
        # if we haven't done a checkout yet, do it
        if not loggable_path(self.__path).exists():
            self.update()
        
        if isinstance(self.__build_cmd, basestring):
            
            # the command was a string, exec it on the commandline
            shell("cd %(path)s && %(build_cmd)s" % dict(
                path = self.__path,
                build_cmd = self.__build_cmd,
            ))
            
        else:
            
            # the command was a callback, use it
            self.__build_cmd()
    
    def clean(self):
        """cleans the build for the dependency"""
        
        # if we haven't done a checkout yet, do it
        if not loggable_path(self.__path).exists():
            self.update()
            
        if isinstance(self.__clean_cmd, basestring):

            # the command was a string, exec it on the commandline
            shell("cd %(path)s && %(clean_cmd)s" % dict(
                path = self.__path,
                clean_cmd = self.__clean_cmd,
            ))
            
        else:
            
            # the command was a callback, use it
            self.__clean_cmd()
