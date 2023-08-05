#!/usr/bin/env python
"""
Module GTKEDITCTRL -- Python GTK Editing Widgets
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

This module contains the GTK GUI objects for edit controls.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gobject

from plib.gui._widgets import editctrl
from plib.gui.defs import *

from _gtkcommon import _PGtkWidget, _gtksignals

class _PGtkEditMixin(object):
    
    def _get_readonly(self):
        return not self._edit.get_editable()
    
    def _set_readonly(self, value):
        self._edit.set_editable(not value)
    
    readonly = property(_get_readonly, _set_readonly)

class PGtkEditBox(gtk.Entry, _PGtkWidget, editctrl.PEditControlBase, _PGtkEditMixin):
    
    # Need to define the 'enter' signal for Entry
    __gsignals__ = { _gtksignals[SIGNAL_ENTER]:
        (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, ()) }
    
    def __init__(self, parent, target=None, geometry=None, expand=True):
        self._edit = self
        gtk.Entry.__init__(self)
        if expand:
            align = ALIGN_JUST
        else:
            align = ALIGN_LEFT
        _PGtkWidget.__init__(self, parent, align)
        # Connect to key pressed signal to catch Enter key
        self.connect("key_press_event", self.keypressed)
        editctrl.PEditControlBase.__init__(self, target, geometry)
    
    def keypressed(self, widget, event):
        if event.keyval == gtk.keysyms.Return:
            self.do_notify(SIGNAL_ENTER)
            return True
        return False
    
    def _get_text(self):
        return self.get_text()
    
    def _set_text(self, value):
        self.set_text(value)
    
    edit_text = property(_get_text, _set_text)

class PGtkEditControl(gtk.ScrolledWindow, _PGtkWidget, editctrl.PEditControlBase, _PGtkEditMixin):
    
    # Need to define the 'changed' signal for TextView so it can pass it on
    __gsignals__ = { _gtksignals[SIGNAL_TEXTCHANGED]:
        (gobject.SIGNAL_RUN_LAST,
        gobject.TYPE_NONE, ()) }
    
    def __init__(self, parent, target=None, geometry=None, scrolling=False):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        _PGtkWidget.__init__(self, parent, ALIGN_JUST)
        editctrl.PEditControlBase.__init__(self, target, geometry)
        self._edit = gtk.TextView()
        if scrolling:
            self._edit.set_wrap_mode(gtk.WRAP_NONE)
        else:
            self._edit.set_wrap_mode(gtk.WRAP_WORD)
        self._edit.get_buffer().connect("changed", self.textchanged)
        self.add(self._edit)
        self._edit.show()
    
    def _font_widget(self):
        return self._edit
    
    def textchanged(self, buf):
        if buf is self._edit.get_buffer():
            # Pass on text buffer changed signal
            self.do_notify(SIGNAL_TEXTCHANGED)
    
    def _get_text(self):
        buffer = self._edit.get_buffer()
        return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
    
    def _set_text(self, value):
        self._edit.get_buffer().set_text(value)
    
    edit_text = property(_get_text, _set_text)
