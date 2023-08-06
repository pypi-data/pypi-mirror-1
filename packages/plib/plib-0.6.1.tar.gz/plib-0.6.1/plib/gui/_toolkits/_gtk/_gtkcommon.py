#!/usr/bin/env python
"""
Module GTKCOMMON -- Python GTK Common Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the GTK common GUI objects.
"""

import pygtk
pygtk.require('2.0')
import gtk
import pango

from plib.gui.defs import *

_gtkalignmap = {
    ALIGN_LEFT: 0.0,
    ALIGN_CENTER: 0.5,
    ALIGN_RIGHT: 1.0 }

_gtkstockids = {
    ACTION_FILENEW: gtk.STOCK_NEW,
    ACTION_FILEOPEN: gtk.STOCK_OPEN,
    ACTION_FILESAVE: gtk.STOCK_SAVE,
    ACTION_FILESAVEAS: gtk.STOCK_SAVE_AS,
    ACTION_FILECLOSE: gtk.STOCK_CLOSE,
    ACTION_EDIT: gtk.STOCK_EDIT,
    ACTION_REFRESH: gtk.STOCK_REFRESH,
    ACTION_ADD: gtk.STOCK_ADD,
    ACTION_REMOVE: gtk.STOCK_REMOVE,
    ACTION_APPLY: gtk.STOCK_APPLY,
    ACTION_OK: gtk.STOCK_OK,
    ACTION_CANCEL: gtk.STOCK_CANCEL,
    ACTION_PREFS: gtk.STOCK_PREFERENCES,
    ACTION_ABOUT: gtk.STOCK_ABOUT,
    ACTION_EXIT: gtk.STOCK_QUIT }

_gtkicons = {
    MBOX_INFO: gtk.MESSAGE_INFO,
    MBOX_WARN: gtk.MESSAGE_WARNING,
    MBOX_ERROR: gtk.MESSAGE_ERROR,
    MBOX_QUERY: gtk.MESSAGE_QUESTION }

_stockidmap = {
    gtk.RESPONSE_YES: gtk.STOCK_YES,
    gtk.RESPONSE_NO: gtk.STOCK_NO,
    gtk.RESPONSE_CANCEL: gtk.STOCK_CANCEL,
    gtk.RESPONSE_OK: gtk.STOCK_OK }

_gtksignals = {
    SIGNAL_ACTIVATED: "activate",
    SIGNAL_CLICKED: "clicked",
    SIGNAL_TOGGLED: "toggled",
    SIGNAL_SELECTED: "selected",
    SIGNAL_FOCUS_IN: "focus_in_event",
    SIGNAL_FOCUS_OUT: "focus_out_event",
    SIGNAL_LISTVIEWCHANGED: "listview_changed",
    SIGNAL_TABLECHANGED: "table_changed",
    SIGNAL_TEXTCHANGED: "changed",
    SIGNAL_EDITCHANGED: "changed",
    SIGNAL_ENTER: "enter_pressed",
    SIGNAL_TABCHANGED: "tab_changed",
    SIGNAL_WIDGETCHANGED: "changed",
    SIGNAL_CLOSING: "window_closing",
    SIGNAL_HIDDEN: "destroy",
    SIGNAL_QUERYCLOSE: "delete_event",
    SIGNAL_BEFOREQUIT: "destroy" }

#_gtkfontfamilies = {
#    "Courier New": 'monospace',
#    "Times New Roman": 'serif',
#    "Arial": 'sans' }

# 'Wrapper' functions for certain signals to discard object parameter
# (since the way we're set up it will always be the same as self anyway)

_gtkwrappers = [SIGNAL_ACTIVATED, SIGNAL_CLICKED, SIGNAL_TOGGLED, SIGNAL_SELECTED,
    SIGNAL_LISTVIEWCHANGED, SIGNAL_TABLECHANGED,
    SIGNAL_TEXTCHANGED, SIGNAL_EDITCHANGED, SIGNAL_ENTER,
    SIGNAL_TABCHANGED]
_gtkplain = [SIGNAL_FOCUS_IN, SIGNAL_FOCUS_OUT,
    SIGNAL_QUERYCLOSE, SIGNAL_CLOSING, SIGNAL_HIDDEN, SIGNAL_BEFOREQUIT]

def _gtk_wrapper(target, plain=False):
    if plain:
        def wrapper(*args):
            target()
    else:
        def wrapper(obj, *args):
            target(*args)
    return wrapper

class _PGtkCommunicator(object):
    """
    A mixin class to abstract signal functionality in GTK.
    """
    
    def setup_notify(self, signal, target, wrap=True):
        if signal in _gtksignals:
            event = _gtksignals[signal]
            if wrap and (signal in _gtkwrappers):
                handler = _gtk_wrapper(target)
            elif signal in _gtkplain:
                handler = _gtk_wrapper(target, True)
            else:
                handler = target
            self.connect(event, handler)
    
    def do_notify(self, signal, *args):
        self.emit(_gtksignals[signal], *args)

class _PGtkWidgetBase(object):
    """ Mixin class to provide basic GTK widget methods. """
    
    def _widget(self):
        return self
    
    def update(self):
        self._widget().queue_draw()
    
    def preferred_width(self):
        return self._widget().get_size_request()[0]
    
    def preferred_height(self):
        return self._widget().get_size_request()[1]
    
    def set_width(self, width):
        height = self.get_size_request()[1]
        self.set_size_request(width, height)
    
    def set_height(self, height):
        width = self.get_size_request()[0]
        self.set_size_request(width, height)
    
    def set_position(self, left, top):
        if not (None in (left, top)):
            self._parent._move_widget(self, left, top)
    
    def set_foreground_color(self, color):
        pass # FIXME
    
    def _font_info(self, font_name, font_size=None):
        #if font_name in _gtkfontfamilies:
        #    font_name = _gtkfontfamilies[font_name]
        if font_size is None:
            font_size = default_font_size
        return font_name, font_size
    
    def _font_widget(self):
        # Some Gtk widgets, like buttons, actually are containers and a child
        # widget is the one we need to set the font on; hence this method is
        # factored out
        return self
    
    def get_font_name(self):
        return self._font_widget().get_pango_context().get_font_description().get_family()
    
    def get_font_size(self):
        return self._font_widget().get_pango_context().get_font_description().get_size()
    
    def set_font(self, font_name, font_size=None):
        font_name, font_size = self._font_info(font_name, font_size)
        self._font_widget().modify_font(pango.FontDescription("%s %s" % (font_name, font_size)))
    
    def _get_enabled(self):
        return self.get_sensitive()
    
    def _set_enabled(self, value):
        self.set_sensitive(value)
    
    enabled = property(_get_enabled, _set_enabled)
    
    def set_focus(self):
        self.grab_focus()

class _PGtkWidget_(_PGtkCommunicator, _PGtkWidgetBase):
    # Intermediate class so _PGtkClientWidget doesn't inherit the overridden __init__ method
    pass

class _PGtkWidget(_PGtkWidget_):
    """ Mixin class for GTK widgets that can send/receive signals. """
    
    def __init__(self, parent, align=ALIGN_LEFT):
        self._parent = parent
        self._align = align
        parent._add_widget(self)

class _PGtkClientWidget(_PGtkWidget_):
    """ Mixin class for GTK client widgets (i.e., can be used as client of main window). """
