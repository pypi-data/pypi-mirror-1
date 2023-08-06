#!/usr/bin/env python
"""
Sub-Package CLASSES of Package PLIB -- Python Class Objects
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This sub-package contains a variety of useful classes. We
use the ModuleProxy class in this sub-package to have all
of the classes appear as attributes of the sub-package,
while only actually importing their modules when used. This
means that you can write:

    from plib.classes import AClass

instead of having to write:

    from plib.classes.AClass import AClass

as you would under the normal Python import mechanics; but
under the hood, each class lives in its own module that is
only imported if you actually use it (which would not be
the case if they were all statically imported here).

Note that, although this seems like a lot of black magic for
what is actually not all that much gain (none of the modules
in this sub-package use *that* much memory), the real reason
for doing it is to improve maintainability of the code. With
normal static importing in Python, every time a class module
was added to this sub-package, I would have to manually add
an import for it here; not only is that repetitive work, but
it adds the potential for error because now the import name
and the module file name must be kept in sync. With the
ModuleProxy class, once I add the module file to the
directory for this sub-package, everything else happens
automatically--less work and no error. And while that may
not be all that much gain for this simple sub-package, more
elaborate sub-package layouts (such as the one in the
PLIB.GUI sub-package) can make the gain much greater.
"""

import os
import glob

from plib.utils import ModuleProxy

# We define these here because after the ModuleProxy they
# wouldn't be directly importable from StateMachine.py

class StateMachineException(Exception): pass

class InvalidState(StateMachineException): pass
class InvalidInput(StateMachineException): pass
class RecursiveTransition(StateMachineException): pass

# Helper function to actually do the import when the
# module attribute is accessed; note that it assumes
# that the function returns the actual class defined
# in the module, not the module itself, and it assumes
# that the class will have the same name as the module

def module_helper(modname):
    def f():
        result = __import__(modname, globals(), locals())
        return getattr(result, modname)
    f.__name__ = "%s_helper" % modname
    return f

# Generate a dictionary of module names and classes
# in our sub-package

module_dict = {}
for pathname in __path__:
    for filename in glob.glob(os.path.join(pathname, "*.py")):
        modname = os.path.splitext(os.path.basename(filename))[0]
        if modname != "__init__": # don't include ourselves!
            module_dict[modname] = module_helper(modname)

# Now do the module proxy; it installs itself in sys.modules
# in place of this module, and stores a reference to this
# module, so we don't need to bind it to a name in our
# namespace (nor do we want to, as that would create a
# circular reference!)

ModuleProxy(__name__, module_dict)

# Now clean up our namespace
del os, glob, ModuleProxy, module_helper, module_dict, \
    pathname, filename, modname
