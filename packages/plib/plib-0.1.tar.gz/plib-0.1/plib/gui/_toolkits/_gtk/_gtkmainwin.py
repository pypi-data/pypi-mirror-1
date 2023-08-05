#!/usr/bin/env python
"""
Module GTKMAINWIN -- Python GTK Main Window Objects
Sub-Package GUI.TOOLKITS.GTK of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

This module contains the GTK GUI main window objects.
"""

import pygtk
pygtk.require('2.0')
import gtk
import gtk.gdk

from plib.gui.defs import *
from plib.gui._base import mainwin

from _gtkcommon import _gtkicons, _stockidmap
from _gtkapp import _PGtkMainMixin
from _gtkaction import PGtkMenu, PGtkToolBar, PGtkAction

_defaultmenuheight = 25

class PGtkMessageBox(mainwin.PMessageBoxBase):
    """ Customized GTK message box. """
    
    questionmap = {
        answerYes: gtk.RESPONSE_YES,
        answerNo: gtk.RESPONSE_NO,
        answerCancel: gtk.RESPONSE_CANCEL,
        answerOK: gtk.RESPONSE_OK }
    
    def _messagebox(self, type, caption, text, button1, button2=None, button3=None):
        dlg = gtk.MessageDialog(self._parent, gtk.DIALOG_MODAL,
            _gtkicons[type], gtk.BUTTONS_NONE, text)
        dlg.set_title(caption)
        dlg.add_button(_stockidmap[button1], button1)
        if button2 is not None:
            dlg.add_button(_stockidmap[button2], button2)
        if button3 is not None:
            dlg.add_button(_stockidmap[button3], button3)
        result = dlg.run()
        dlg.destroy()
        return result

class PGtkFileDialog(mainwin.PFileDialogBase):
    
    def _gtkfiledialog(self, title, path, filter, action):
        dlg = gtk.FileChooserDialog(title, self, action)
        if len(path) > 0:
            dlg.set_current_folder(path)
        if len(filter) > 0:
            flt = gtk.FileFilter()
            flt.add_pattern(filter)
            dlg.set_filter(flt)
        result = dlg.run()
        if result == gtk.RESPONSE_OK:
            retval = dlg.get_filename()
        else:
            retval = ""
        dlg.destroy()
        return retval
    
    def openfiledialog(self, path, filter):
        return self._gtkfiledialog("Select file to open", path, filter, gtk.FILE_CHOOSER_ACTION_OPEN)
    
    def savefiledialog(self, path, filter):
        return self._gtkfiledialog("Select file to save", path, filter, gtk.FILE_CHOOSER_ACTION_SAVE)

class PGtkMainWindow(_PGtkMainMixin, mainwin.PMainWindowBase):
    """
    A customized GTK main window class.
    """
    
    menuclass = PGtkMenu
    toolbarclass = PGtkToolBar
    actionclass = PGtkAction
    messageboxclass = PGtkMessageBox
    filedialogclass = PGtkFileDialog
    
    def __init__(self, parent):
        _PGtkMainMixin.__init__(self)
        mainwin.PMainWindowBase.__init__(self, parent)
        self._add_frame_widget(self.menu, False, False)
        self._add_frame_widget(self.toolbar, False, False)
        self._add_frame_widget(self.clientwidget, True, True)
        if self.clientwidget is None:
            self.layout = gtk.Layout()
            self._add_frame_widget(self.layout, True, True)
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PGtkMainMixin.show_init(self)
