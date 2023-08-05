#!/usr/bin/env python
"""
Module MAIN -- Top-Level GUI Module
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

This is the main module for the GUI sub-package; its
namespace contains all the GUI classes and constants
and the runapp() function which should be the main function
of a GUI application. It can be imported as follows:

import plib.gui.main
- or -
from plib.gui import main

Note that this module uses the ModuleProxy class to avoid
importing *all* of the widget modules at once; instead that
class allows 'lazy' importing of the modules only when they
are first used. (Note also that this means from plib.gui.main
import * will *not* work.)

BTW, for those who think I'm doing this because I simply
can't help using black magic instead of ordinary code,
you're absolutely right. :) However, there actually are
other good reasons to do it, which are explained in the
docstring for the PLIB.CLASSES sub-package.
"""

from plib.classes import ModuleProxy

from plib.gui.defs import GUI_KDE, GUI_QT, GUI_GTK, GUI_WX
from plib.gui._gui import gui_toolkit

# Set the toolkit string and import stuff that we'll always use

if gui_toolkit == GUI_KDE:
    toolkit = 'KDE'
    from _toolkits._kde._kdeapp import PKDETopWindow as PTopWindow, \
        PKDEApplication as PApplication

elif gui_toolkit == GUI_QT:
    toolkit = 'Qt'
    from _toolkits._qt._qtapp import PQtTopWindow as PTopWindow, \
        PQtApplication as PApplication

elif gui_toolkit == GUI_GTK:
    toolkit = 'Gtk'
    from _toolkits._gtk._gtkapp import PGtkTopWindow as PTopWindow, \
        PGtkApplication as PApplication

elif gui_toolkit == GUI_WX:
    toolkit = 'Wx'
    from _toolkits._wx._wxapp import PWxTopWindow as PTopWindow, \
        PWxApplication as PApplication

else:
    raise ValueError, "%s is an invalid value for GUI toolkit." % gui_toolkit

# Names dictionary that will be passed to ModuleProxy; we'll generate
# its entries below using data lists and helper functions that return
# callables which will load the required sub-modules dynamically on use

toolkit_dict = {}

# Toolkit-specific entries for namespace dictionary

def toolkit_helper(toolkit, modname, klassname):
    def f():
        return getattr(getattr(getattr(getattr(getattr(
            __import__('plib.gui._toolkits._%s._%s%s' % (toolkit.lower(), toolkit.lower(), modname)),
            'gui'), '_toolkits'), '_%s' % toolkit.lower()), '_%s%s' % (toolkit.lower(), modname)),
            'P%s%s' % (toolkit, klassname))
    f.__name__ = '%s_%s_%s' % (toolkit, modname, klassname)
    return f

toolkit_list = [
    ('button', ['Button', 'CheckBox']),
    ('combo', ['ComboBox']),
    ('editctrl', ['EditBox', 'EditControl']),
    ('table', ['TableLabels', 'Table']),
    ('listview', ['ListViewLabels', 'ListViewItem', 'ListView']),
    ('tabwidget', ['TabWidget']),
    ('panel', ['Panel']),
    ('action', ['Menu', 'ToolBar', 'Action']),
    ('mainwin', ['MessageBox', 'FileDialog', 'MainWindow']) ]

toolkit_dict.update(('P%s' % klassname, toolkit_helper(toolkit, modname, klassname))
    for modname, klassnames in toolkit_list for klassname in klassnames)

# Generic 'widget' entries for namespace dictionary

def widget_helper(klassname, modname):
    def f():
        return getattr(getattr(getattr(getattr(
            __import__('plib.gui._widgets.%s' % modname), 'gui'), '_widgets'), modname), klassname)
    f.__name__ = 'widget_%s_%s' % (modname, klassname)
    return f

widget_list = [
    ('PTableRow', 'table'),
    ('PListViewItemCols', 'listview') ]

toolkit_dict.update((klassname, widget_helper(klassname, modname)) for klassname, modname in widget_list)

# 'Mixin' entries for namespace dictionary

def mixin_helper(klassname, bases):
    def f():
        baselist = [ getattr(getattr(getattr(__import__('plib.gui.%s' % modname), 'gui'), modname), basename)
            for modname, basename in bases ]
        result = type(klassname, tuple(baselist), {})
        
        # Hack here to avoid even worse hacks elsewhere
        if klassname == 'PAutoPanel':
            result.baseclass = result
        
        return result
    f.__name__ = 'mixin_%s' % klassname
    return f

mixin_list = [
    ('PTableEditor', [('_mixins', 'PTableMixin'), ('edit', 'PEditor')]),
    ('PAutoPanel', [('_mixins', 'PPanelMixin'), ('main', 'PPanel')]) ]

toolkit_dict.update((klassname, mixin_helper(klassname, bases)) for klassname, bases in mixin_list)

# Now set up module proxy to 'lazy import' toolkit items as needed; note that
# we don't need to bind it to a variable in this module because it installs
# itself in sys.modules in our place (and that means we don't *want* to bind it
# to a variable here because that would create a circular reference)
ModuleProxy(__name__, toolkit_dict)

# Clean up namespace (and allow memory for helper items to be released,
# since they've done their job and we don't need them any more)
del ModuleProxy, toolkit_helper, widget_helper, mixin_helper, \
    widget_list, mixin_list, toolkit_list, toolkit_dict, \
    GUI_KDE, GUI_QT, GUI_GTK, GUI_WX

# Utility function for running application

def runapp(appclass=None, arglist=[]):
    """
    Runs application with args arglist:
    -- if appclass is None, run a 'bare' PApplication (this is only useful for
       demo purposes, sort of like a "Hello World" app);
    -- if appclass is a subclass of PApplication, instantiates and runs it (this
       should be very rare as subclassing a widget will almost always suffice);
    -- otherwise, pass appclass to PApplication, which will determine whether it
       is a main widget class (and then just instantiate it as the app's main
       widget) or a client widget class (which it will insert into an instance
       of its default main widget class).
    """
    
    if appclass is None:
        app = PApplication(arglist)
    elif issubclass(appclass, PApplication):
        app = appclass(arglist)
    else:
        app = PApplication(arglist, appclass)
    app.run()
