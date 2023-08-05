#!/usr/bin/env python
"""
Module GTKCOMMON -- Python GTK Common Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

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
    ACTION_OK: gtk.STOCK_OK,
    ACTION_CANCEL: gtk.STOCK_CANCEL,
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
    #SIGNAL_LISTVIEWCHANGED: "listview_changed",
    SIGNAL_TABLECHANGED: "table_changed",
    SIGNAL_TEXTCHANGED: "changed",
    SIGNAL_ENTER: "enter_pressed",
    SIGNAL_WIDGETCHANGED: "changed",
    SIGNAL_QUERYCLOSE: "delete_event",
    SIGNAL_HIDDEN: "destroy",
    SIGNAL_BEFOREQUIT: "destroy" }

#_gtkfontfamilies = {
#    "Courier New": 'monospace',
#    "Times New Roman": 'serif',
#    "Arial": 'sans' }

# 'Wrapper' functions for certain signals to discard object parameter
# (since the way we're set up it will always be the same as self anyway)

_gtkwrappers = [SIGNAL_ACTIVATED, SIGNAL_CLICKED, SIGNAL_TOGGLED, SIGNAL_TABLECHANGED,
    SIGNAL_TEXTCHANGED, SIGNAL_ENTER]
_gtkplain = [SIGNAL_QUERYCLOSE, SIGNAL_HIDDEN, SIGNAL_BEFOREQUIT]

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

class _PGtkWidget(_PGtkCommunicator):
    """ Mixin class with 'standard' GTK widget methods. """
    
    def __init__(self, parent, align=ALIGN_LEFT):
        self._parent = parent
        self._align = align
        parent._add_widget(self)
    
    def update(self):
        self.queue_draw()
    
    def set_geometry(self, left, top, width, height):
        self.set_size_request(width, height)
        self._parent._move_widget(self, left, top)
    
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
