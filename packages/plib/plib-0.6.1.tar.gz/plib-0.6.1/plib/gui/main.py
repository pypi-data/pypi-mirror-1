#!/usr/bin/env python
"""
Module MAIN -- Top-Level GUI Module
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

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

import sys

from plib.stdlib import dotted_from_import
from plib.utils import ModuleProxy

from plib.gui.defs import GUI_KDE, GUI_QT, GUI_GTK, GUI_WX, GUI_QT4, GUI_KDE4
from plib.gui._gui import gui_test

if gui_test:
    gui_toolkit = 0
else:
    from plib.gui._gui import gui_toolkit

# Set the toolkit string
# TODO: modularize this so we only need to change one module for a new toolkit

if gui_toolkit == GUI_KDE:
    toolkit = 'KDE'

elif gui_toolkit == GUI_QT:
    toolkit = 'Qt'

elif gui_toolkit == GUI_GTK:
    toolkit = 'Gtk'

elif gui_toolkit == GUI_WX:
    toolkit = 'Wx'

elif gui_toolkit == GUI_QT4:
    toolkit = 'Qt4'

elif gui_toolkit == GUI_KDE4:
    toolkit = 'KDE4'

elif not gui_test:
    raise ValueError, "No GUI toolkit found; cannot run GUI application."

# Names dictionary that will be passed to ModuleProxy; we'll generate
# its entries below using data lists and helper functions that return
# callables which will load the required sub-modules dynamically on use

toolkit_dict = {}

if gui_test:
    # The _gui module should have been patched to include GUI classes
    del gui_toolkit, gui_test
    from plib.gui._gui import *
    gui_toolkit = 0

else:
    # Toolkit-specific entries for namespace dictionary
    
    def toolkit_helper(toolkit, modname, klassname):
        def f():
            return dotted_from_import(
                'plib.gui._toolkits._%s._%s%s' % (toolkit.lower(), toolkit.lower(), modname),
                'P%s%s' % (toolkit.rstrip('4'), klassname)) # hack for Qt/KDE 4 to avoid massive class renaming
        f.__name__ = '%s_%s_%s' % (toolkit, modname, klassname)
        return f
    
    # Got the hack, might as well use it...
    PApplication = toolkit_helper(toolkit, 'app', 'Application')()
    
    toolkit_list = [
        ('label', ['TextLabel']),
        ('display', ['TextDisplay']),
        ('button', ['Button', 'CheckBox']),
        ('combo', ['ComboBox']),
        ('editctrl', ['EditBox', 'EditControl']),
        ('groupbox', ['GroupBox']),
        ('table', ['TableLabels', 'Table']),
        ('listview', ['ListViewLabels', 'ListViewItem', 'ListView', 'ListBox']),
        ('tabwidget', ['TabWidget']),
        ('panel', ['Panel']),
        ('statusbar', ['StatusBar']),
        ('action', ['Menu', 'ToolBar', 'Action']),
        ('mainwin', ['MessageBox', 'FileDialog', 'MainWindow']),
        ('app', ['TopWindow']) ]
    
    # Some items are only present in certain toolkits
    if toolkit in ('KDE', 'KDE4', 'Qt', 'Qt4'):
        toolkit_list.append(
            ('notify', ['SocketNotifier']) )
    
    toolkit_dict.update([('P%s' % klassname, toolkit_helper(toolkit, modname, klassname))
        for modname, klassnames in toolkit_list for klassname in klassnames])
    
    del toolkit_helper, toolkit_list

# 'Mixin' entries for namespace dictionary

def mixin_helper(klassname, bases):
    def f():
        baselist = [ dotted_from_import('plib.gui.%s' % modname, basename)
            for modname, basename in bases ]
        result = type(klassname, tuple(baselist), {})
        
        # Hacks here to avoid even worse hacks elsewhere
        if klassname == 'PAutoPanel':
            result.baseclass = result
            result.panelclass = sys.modules[__name__].PPanel
        elif klassname in ('PAutoTabWidget', 'PAutoGroupBox'):
            result.panelclass = sys.modules[__name__].PAutoPanel
        
        return result
    f.__name__ = 'mixin_%s' % klassname
    return f

mixin_list = [
    ('PTableEditor', [('_mixins', 'PTableMixin'), ('main', 'PEditor')]),
    ('PTreeEditor', [('_mixins', 'PTreeMixin'), ('main', 'PEditor')]),
    ('PAutoPanel', [('_mixins', 'PPanelMixin'), ('main', 'PPanel')]),
    ('PAutoTabWidget', [('_mixins', 'PTabMixin'), ('main', 'PTabWidget')]),
    ('PAutoGroupBox', [('_mixins', 'PGroupMixin'), ('main', 'PGroupBox')]),
    ('PAutoStatusBar', [('_mixins', 'PStatusMixin'), ('main', 'PStatusBar')]) ]

if gui_test:
    # Remove the mixins that aren't supported in the test toolkit
    def is_widget(baseklass):
        # Hack to make sure 'non-widget' classes don't get removed; this will
        # need to be manually kept in sync with the non-widgets in mixin_list above
        return (baseklass != 'PEditor')
    removes = []
    for item in mixin_list:
        klassname, bases = item
        for modname, baseklass in bases:
            if (modname == 'main') and is_widget(baseklass) and not hasattr(sys.modules[__name__], baseklass):
                removes.append(item)
    for item in removes:
        mixin_list.remove(item)
    # Clean up the temporary names used
    del is_widget, removes, item, klassname, bases, modname, baseklass

toolkit_dict.update([(klassname, mixin_helper(klassname, bases))
    for klassname, bases in mixin_list])

# Generic 'widget' entries for namespace dictionary

def widget_helper(klassname, modname):
    def f():
        return dotted_from_import('plib.gui._widgets.%s' % modname, klassname)
    f.__name__ = 'widget_%s_%s' % (modname, klassname)
    return f

widget_list = [
    ('PTableRow', 'table'),
    ('PListViewItemCols', 'listview') ]

toolkit_dict.update([(klassname, widget_helper(klassname, modname))
    for klassname, modname in widget_list])

# Standalone class entries for namespace dictionary

def class_helper(modname, klassname):
    def f():
        return dotted_from_import('plib.gui.%s' % modname, klassname)
    f.__name__ = '%s_%s' % (modname.lstrip('_'), klassname)
    return f

class_list = [
    ('_classes', ['PHeaderLabel', 'PTextFile']),
    ('_dialogs', ['PDialogBase', 'PPrefsDialog']),
    ('_edit', ['PEditor', 'PFileEditor']),
    ('_panels', ['PMainPanel']) ]

toolkit_dict.update([(klassname, class_helper(modname, klassname))
    for modname, klassnames in class_list for klassname in klassnames])

# Now set up module proxy to 'lazy import' toolkit items as needed; note that
# we don't need to bind it to a variable in this module because it installs
# itself in sys.modules in our place (and that means we don't *want* to bind it
# to a variable here because that would create a circular reference)
ModuleProxy(__name__, toolkit_dict)

# Clean up namespace (and allow memory for helper items to be released,
# since they've done their job and we don't need them any more)
del ModuleProxy, widget_helper, class_helper, mixin_helper, \
    toolkit_dict, widget_list, class_list, mixin_list, \
    GUI_KDE, GUI_QT, GUI_GTK, GUI_WX, GUI_QT4

# Utility function for running application

default_appclass = [PApplication] # allows overriding if desired

def runapp(appclass=None, arglist=[]):
    """
    Runs application with args arglist:
    -- if appclass is None, run a 'bare' application (this is only useful for
       demo purposes, sort of like a "Hello World" app);
    -- if appclass is a subclass of PApplication, instantiates and runs it (this
       should be very rare as subclassing a widget will almost always suffice);
    -- otherwise, pass appclass to the default application, which will determine
       whether it is a main widget class (and then just instantiate it as the app's
       main widget) or a client widget class (which it will insert into an instance
       of its default main widget class).
    """
    
    if appclass is None:
        app = default_appclass[0](arglist)
    elif issubclass(appclass, PApplication):
        app = appclass(arglist)
    else:
        app = default_appclass[0](arglist, appclass)
    app.run()
