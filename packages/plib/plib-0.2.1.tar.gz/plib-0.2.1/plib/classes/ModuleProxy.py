#!/usr/bin/env python
"""
Module ModuleProxy
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ModuleProxy class. For examples
of intended use cases for this class, check out:

(1) The __init__.py for this sub-package and the STDLIB
    sub-package;

(2) The MAIN.PY module in the PLIB.GUI sub-package.

The docstrings and comments there give more information.
"""

import sys

class ModuleProxy(object):
    
    def __init__(self, modname, names):
        self._names = names
        
        # Monkeypatch sys.modules with the proxy object (make
        # sure we store a reference to the real module first!)
        self._mod = sys.modules[modname]
        sys.modules[modname] = self
        
        # Pass-through module's docstring (this attribute name
        # appears in both so __getattr__ below won't handle it)
        self.__doc__ = self._mod.__doc__
    
    def __getattr__(self, name):
        try:
            # Remember we need to return the real module's attributes!
            result = getattr(self._mod, name)
            return result
        
        except AttributeError:
            names = self.__dict__['_names']
            if name in names:
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
                
                # After the first access, the name will be in our __dict__
                setattr(self, name, result)
                
                # Now that it's in our __dict__, we can remove it from names
                del names[name]
                
                # And return it
                return result
        
        # If we get here, nothing was found
        raise AttributeError, "%s object has no attribute %s" % (self._mod, name)
