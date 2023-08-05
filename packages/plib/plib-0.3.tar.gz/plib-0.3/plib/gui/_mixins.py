#!/usr/bin/env python
"""
Module MIXINS -- Mixin Classes for GUI
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines mixin classes to customize behavior of GUI objects.
"""

import types

from plib.gui.defs import *
from plib.gui import main

# Mixin classes to customize editor behavior for various types of widgets;
# note that these should appear *before* the editor class in the list of
# base classes.

class PTableMixin(object):
    """ Mixin class for editor with table widget. """
    
    _data_loaded = False
    modifysignals = { SIGNAL_TABLECHANGED: None }
    
    def tablechanged(self, row, col):
        """ Update data store with changed value from table cell. """
        self.data[row][col] = self.control[row][col]
    
    def _helperadd(self, index, value):
        """ Update data store with new row's value -- but only if data is already loaded. """
        if self._data_loaded:
            self.data.insert(index, value)
        super(PTableMixin, self)._helperadd(index, value)
    
    def _helperdel(self, index, item):
        """ Remove deleted item from data store. """
        super(PTableMixin, self)._helperdel(index, item)
        if self._data_loaded:
            del self.data[index]
    
    def _connect_control(self):
        """ Connect to table changed signal. """
        self.control.setup_notify(SIGNAL_TABLECHANGED, self.tablechanged)
    
    def _doload(self):
        """ Populate table widget from data. Assumes that data is a sequence of sequences;
        each top-level sequence item is a table row, each item within the row is data for a cell. """
        
        self.control.extend(self.data)
        # Since the widget wasn't initialized with data, we have to size it here
        self.control.set_min_size(self.control.minwidth(), self.control.minheight())
        # Update the loaded field so further row adds/deletes will update the data store
        self._data_loaded = True

class PTreeMixin(object):
    """ Mixin class for editor with tree-type widget. """
    
    def treechanged(self):
        """ Override to take action on new item selection in tree. """
        pass
    
    def _connect_control(self):
        """ Connect to list view changed signal. """
        self.control.setup_notify(SIGNAL_LISTVIEWCHANGED, self.treechanged)
    
    def _doload(self):
        """ Populate tree widget from data. Assume that data is a sequence of 2-tuples, with
        the first item being a sequence of item strings (to allow for multiple columns),
        and the second item being a sub-sequence of 2-tuples for child tree nodes. """
        self.control.extend(self.data)

# Mixin class for panel widgets to make child widget creation easier

class PPanelMixin(object):
    """
    Mixin class that provides an easier way to create child
    widgets for panels. The childlist class field is used
    to provide a list of 4-tuples (class, args, kwds, attrname)
    which is used to guide the creation of child widgets. The
    attrname field, if not None, tells what named attribute of
    the panel the created widget should be bound to.
    
    Note that this method requires that, if any of the child
    widgets are themselves panels, they will require their own
    classes to fill in their childlist fields. However, an
    alternative is provided: if the baseclass class field is
    filled in, then the 'class' member of the 4-tuples in
    childlist may instead be a sub-list of 4-tuples; the
    sub-list will then be used to create a panel class on
    the fly, subclassed from baseclass, and with the given
    list as its childlist. (As long as baseclass is derived
    from PPanelMixin, this process will work recursively.) 
    
    As an added feature, this class overrides __getattr__ to
    allow attributes of child panels to appear as attributes
    of the parent panel. This is mainly to allow easier access
    to controls defined in child panels (so you don't have to
    remember at which level of nested panels you inserted a
    control -- just treat it as part of the main panel).
    """
    
    baseclass = None
    childlist = []
    
    def _createpanels(self):
        """ Create child panels listed in class field """
        for klass, args, kwds, attrname in self.childlist:
            if not isinstance(klass, (type, types.ClassType)):
                # klass is a sub-list, create a class on the fly
                klass = type(self.baseclass)("%s_%s" % (self.__class__.__name__, attrname),
                    (self.baseclass,), {'baseclass': self.baseclass, 'childlist': klass})
            widget = klass(self, *args, **kwds)
            if not isinstance(widget, self.baseclass):
                self._addwidget(widget)
            if attrname is not None:
                setattr(self, attrname, widget)
    
    def __getattr__(self, name):
        """ Allow 'pass-through' access to attributes of child panels """
        try:
            # This is in case we're mixing in with a class that also
            # overrides __getattr__
            result = super(PPanelMixin, self).__getattr__(name)
            return result
        except AttributeError:
            # Now loop through child panels
            for panel in self.__dict__['_panels']:
                try:
                    result = getattr(panel, name)
                    return result
                except AttributeError:
                    pass
        # If we get here, nothing was found
        raise AttributeError, "%s object has no attribute '%s'" % (self.__class__.__name__, name)

# Mixin class for tab widgets to let them manage sub-panels using above

class PTabMixin(object):
    """
    Mixin class for tab widgets that 'expands' a list of panel specs
    into the actual panels and adds them as tabs.
    """
    
    panelclass = None
    
    def _get_panel(self, spec):
        """ Return a PAutoPanel with childlist = spec. """
        base = self.panelclass
        contents, args, kwds, attrname = spec
        if isinstance(self._parent, self.panelclass):
            basename = self._parent.__class__.__name__
        else:
            basename = 'tabs_'
        klass = type(base)("%s_%s" % (basename, attrname), (base,), {'childlist': contents})
        widget = klass(self, *args, **kwds)
        if isinstance(self._parent, self.panelclass):
            if attrname is not None:
                setattr(self._parent, attrname, widget)
            if isinstance(widget, self.panelclass):
                self._parent._panels.append(widget) # so finding controls by attr name works
        return widget
    
    def _createtabs(self, tabs):
        """
        Assumes that tabs is a sequence of 2-tuples containing
        (title, panelspec) for each tab.
        """
        
        # FIXME: The extend method doesn't take an iterator? (if it did,
        # we could just pass a generator expression to extend here instead
        # of the for loop with append, but that doesn't seem to work)
        for title, spec in tabs:
            self.append((title, self._get_panel(spec)))

# Mixin class for status bars to make sub-widget definition easier

def _widget_helper(wclassname, args, kwds, wname):
    def f():
        w = getattr(main, wclassname)(*args, **kwds)
        return (wname, w)
    f.__name__ = '%s_%s' % (wclassname, wname)
    return f

class PStatusMixin(object):
    """
    Mixin class to allow easier specification of status bar widgets.
    The widgetspecs class field should be filled in with a list of
    4-tuples similar to those used by PPanelMixin above; the tuples
    should contain (classname, args, kwds, attrname), where classname
    is the widget class name, which is assumed to be findable as an
    attribute in the plib.gui.main module, args and kwds are positional
    and keyword arguments to be passed to the class constructor, and
    attrname is the attribute name on the status bar to be used to
    hold a reference to the widget.
    """
    
    widgetspecs = None
    
    def _init_widgets(self, widgets):
        """ Override to allow reading widget specs from class field. """
        if (widgets is None):
            if self.widgetspecs is not None:
                widgetspecs = self.widgetspecs
            elif self._mainwin is not None:
                widgetspecs = self._mainwin.widgetspecs
            else:
                widgetspecs = None
            if widgetspecs:
                widgets = [_widget_helper(*spec) for spec in widgetspecs]
        super(PStatusMixin, self)._init_widgets(self, widgets)
