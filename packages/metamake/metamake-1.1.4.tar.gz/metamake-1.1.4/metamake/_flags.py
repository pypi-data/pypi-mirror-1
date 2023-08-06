import sys
from os import environ

def _get_args_from_commandline():
    """helper method that gets the commandline arguments
    regardless of whether metamake was run as a standalone
    app or through a Makefile bootstrap"""
    
    if "MAKEFLAGS" in environ:
        
        # we were run via 'make', use the MAKEFLAGS
        # environment variable to see our flags
        makeflags = environ["MAKEFLAGS"].split()
        return [arg for arg in makeflags if "=" in arg]
        
    else:
        
        # we were run standalone, use any commandline
        # arguments that have an '=' in them
        return [arg for arg in sys.argv if "=" in arg]


class Flag(object):
    """represents a flag that can be given on the commandline
    to affect a build"""
    
    _flag_value_lookup = None
    _flag_explanation_lookup = {}
    _flag_type_lookup = {}
    _flag_allowablevals_lookup = {}
    
    def _get_value(self):
        if not self.given:
            return None
        else:
            value = Flag._flag_value_lookup[self.__flag_name]
            type_ = Flag._flag_type_lookup.get(self.__flag_name, None)
            allowable_values = Flag._flag_allowablevals_lookup.get(self.__flag_name, None)
            def _raise_value_error():
                raise ValueError("invalid value %s for flag '%s')" % (repr(value), self.__flag_name))
            if type_ is not None:
                if issubclass(type_, bool):
                    # we treat boolean differently to ensure that it maps properly
                    if value.lower() in ["true", "1", "t", "yes", "y", "on"]:
                        value = True
                    elif value.lower() in ["false", "0", "f", "no", "n", "off"]:
                        value = False
                    else:
                        _raise_value_error()
                else:
                    # all other values can be converted properly
                    value = type_(value)
            if allowable_values is not None:
                if value not in allowable_values:
                    _raise_value_error()
            return value
    
    given = property(lambda self: bool(self.__flag_name in Flag._flag_value_lookup))
    """returns true if the Flag has been given on the commandline (regardless of value)"""
    
    value = property(_get_value)
    """returns the actual value of the Flag (if given)"""
    
    explanation = property(lambda self: Flag._flag_explanation_lookup.get(self.__flag_name, None))
    """return a human-readable explanation of this Flag's affect"""
    
    def explain(self, explanation, convert=None, allow=None):
        """this method is used to explain a flag in plain
        language so that the 'ls' task will display it"""

        if self.__flag_name in Flag._flag_explanation_lookup.keys():
        
            # this Flag was already explained once, don't allow re-explanation
            print >> sys.stderr, "*** the Flag '%(flagname)s' is already being used for '%(explanation)s" % dict(
                flagname = self.__flag_name,
                explanation = Flag._flag_explanation_lookup[self.__flag_name],
            )
            raise SystemExit(1)
        
        else:
            
            # no conflicts, set the explanation
            Flag._flag_explanation_lookup[self.__flag_name] = explanation
            if convert is not None:
                Flag._flag_type_lookup[self.__flag_name] = convert
            if allow is not None:
                Flag._flag_allowablevals_lookup[self.__flag_name] = allow

        
        # return the Flag object to allow chaining
        return self

    def __init__(self, flag_name):
        
        # lazy-parse the makeflags
        if Flag._flag_value_lookup == None:
            Flag._flag_value_lookup = {}
            for key_and_value in _get_args_from_commandline():
                key,value = key_and_value.split("=", 1)
                Flag._flag_value_lookup[key] = value
        
        # keep information about this flag
        self.__flag_name = flag_name
