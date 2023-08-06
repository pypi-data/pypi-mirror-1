#!/usr/bin/env python
"""
Module ModuleProxy
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ModuleProxy class. For examples
of intended use cases for this class, check out:

(1) The __init__.py for the PLIB.CLASSES and PLIB.STDLIB
    sub-packages;

(2) The MAIN.PY module in the PLIB.GUI sub-package.

The docstrings and comments there give more information.
"""

import sys
import types

# Note that we subclass types.ModuleType in order to fool
# various introspection utilities (e.g., pydoc and the builtin
# 'help' command in the interpreter) into thinking ModuleProxy
# instances are actual modules. Among other things, this is
# necessary for the builtin 'help' command to properly display
# the info from the proxied module's docstring (setting the
# proxy's __doc__ to the actual module's __doc__ is *not*
# enough to do this by itself).

class ModuleProxy(types.ModuleType):
    
    def __init__(self, modname, names):
        types.ModuleType.__init__(self, modname)
        self._names = names
        
        # Monkeypatch sys.modules with the proxy object (make
        # sure we store a reference to the real module first!)
        self._mod = sys.modules[modname]
        sys.modules[modname] = self
        
        # Pass-through module's docstring (this attribute name
        # appears in both so __getattr__ below won't handle it);
        # as noted above, this in itself isn't enough to make
        # the 'help' builtin work right, but it is a necessary
        # part of doing so
        self.__doc__ = self._mod.__doc__
    
    def __repr__(self):
        return "<proxy of module '%s' from '%s'>" % (self._mod.__name__, self._mod.__file__)
    
    def __getattr__(self, name):
        try:
            # Remember we need to return the real module's attributes!
            result = getattr(self._mod, name)
            return result
        
        except AttributeError:
            names = self.__dict__['_names']
            try:
                result = names[name]
                
                # This hack allows features like 'lazy importing' to work;
                # a callable names dict entry allows arbitrary (and possibly
                # expensive) processing to take place only when the attribute
                # is first accessed, instead of when the module is initially
                # imported. Also, since we store the result in our __dict__,
                # the expensive function won't get called again, so we are
                # essentially memoizing the result.
                if hasattr(result, '__call__'):
                    result = result()
                
                setattr(self, name, result)
                del names[name]
                return result
            
            except KeyError:
                raise AttributeError, "%s object has no attribute %s" % (self, name)
