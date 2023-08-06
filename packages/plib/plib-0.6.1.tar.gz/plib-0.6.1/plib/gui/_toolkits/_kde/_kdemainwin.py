#!/usr/bin/env python
"""
Module KDEMAINWIN -- Python KDE Main Window Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI main window objects.
"""

import sys

import qt
import kdecore
import kdeui

from plib.gui.defs import *
from plib.gui._base import mainwin

from _kdecommon import _kdemessagefuncs
from _kdeapp import _PKDEMainMixin
from _kdeaction import PKDEMenu, PKDEToolBar, PKDEAction
from _kdestatusbar import PKDEStatusBar

def _int(button):
    if button is not None:
        return button
    else:
        return 0

class PKDEMessageBox(mainwin.PMessageBoxBase):
    """ Customized KDE message box. """
    
    questionmap = {
        answerYes: qt.QMessageBox.Yes,
        answerNo: qt.QMessageBox.No,
        answerCancel: qt.QMessageBox.Cancel,
        answerOK: qt.QMessageBox.Ok }
    
    def _messagebox(self, type, caption, text, button1, button2=None, button3=None):
        return _kdemessagefuncs[type](self._parent, caption, text,
            _int(button1), _int(button2), _int(button3))

class PKDEFileDialog(mainwin.PFileDialogBase):
    
    def openfiledialog(self, path, filter):
        return qt.QFileDialog.getOpenFileName(path, filter)
    
    def savefiledialog(self, path, filter):
        return qt.QFileDialog.getSaveFileName(path, filter)

class PKDEMainWindow(_PKDEMainMixin, mainwin.PMainWindowBase):
    """
    A customized KDE main window class.
    """
    
    menuclass = PKDEMenu
    toolbarclass = PKDEToolBar
    statusbarclass = PKDEStatusBar
    actionclass = PKDEAction
    messageboxclass = PKDEMessageBox
    filedialogclass = PKDEFileDialog
    
    def __init__(self, parent, cls=None):
        _PKDEMainMixin.__init__(self)
        mainwin.PMainWindowBase.__init__(self, parent, cls)
        self.setCentralWidget(self.clientwidget)
        if self.toolbar is not None:
            vmajor = qt.qVersion()[0]
            if vmajor == "2":
                self.setToolBarsMovable(False)
            elif vmajor == "3":
                self.setDockWindowsMovable(False)
            self.setDockMenuEnabled(False)
        self._init_icon()
    
    def show_init(self):
        mainwin.PMainWindowBase.show_init(self)
        _PKDEMainMixin.show_init(self)
