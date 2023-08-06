#!/usr/bin/env python
"""
Module KDEAPP -- Python KDE Application Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the KDE GUI application objects.
"""

import sys

import qt
import kdecore
import kdeui

from plib.gui.defs import *
from plib.gui._base import app

from _kdecommon import _PKDECommunicator

def _kdeparse(aboutdata):
    data = kdecore.KAboutData(aboutdata['name'], aboutdata['name'], aboutdata['version'])
    data.setCopyrightStatement(aboutdata['copyright'])
    data.setLicenseText(aboutdata['license'])
    data.setShortDescription(aboutdata['description'])
    for dev in aboutdata['developers']:
        data.addAuthor(dev)
    data.setHomepage(aboutdata['website'])
    # FIXME: wtf doesn't this work? Alternately, why doesn't setting the program
    # icon elsewhere cause it to display here?
    #data.setProgramLogo(qt.QPixmap(aboutdata['icon']))
    return data

class _PKDEMainMixin(kdeui.KMainWindow, _PKDECommunicator):
    """
    Mixin class for KDE top windows and main windows.
    """
    
    _closed = False # default for guard to trap close from system menu, see below
    
    def _init_icon(self):
        if (self.aboutdata is not None) and ('icon' in self.aboutdata):
            self.setIcon(qt.QPixmap(self.aboutdata['icon']))
    
    def _get_w(self):
        return self.width()
    w = property(_get_w)
    
    def _show_window(self):
        kdeui.KMainWindow.show(self)
    
    def _hide_window(self):
        kdeui.KMainWindow.hide(self)
    
    def set_caption(self, caption):
        self.setPlainCaption(caption)
    
    def sizetoscreen(self, maximized):
        if maximized:
            if self.shown:
                self.showMaximized()
            else:
                self._showMax = True
        else:
            desktop = self.app.desktop()
            self.resize(desktop.width() - self.sizeoffset, desktop.height() - self.sizeoffset)
    
    def sizetoclient(self, clientwidth, clientheight):
        self.resize(clientwidth, clientheight)
    
    def center(self):
        desktop = self.app.desktop()
        g = self.frameGeometry()
        x, y = g.width(), g.height()
        self.move((desktop.width() - x)/2, (desktop.height() - y)/2)
    
    def show_init(self):
        if hasattr(self, '_showMax'):
            self.showMaximized()
            del self._showMax
        else:
            kdeui.KMainWindow.show(self)
    
    def about(self):
        if self.aboutdata is not None:
            kaboutdata = _kdeparse(self.aboutdata)
            dlg = kdeui.KAboutApplication(kaboutdata)
            dlg # FIXME: wtf do we need this to prevent a segfault in the next line?
            dlg.exec_loop()
            #kdeui.KAboutApplication(kaboutdata).exec_loop()
    
    def exit(self):
        # Guard traps a close other than from this method, so we don't throw an
        # exception if this method gets called after we close but before shutdown
        # (?? Why isn't this necessary in Qt?)
        if not self._closed:
            self.close()
    
    def closeEvent(self, event):
        # 'automagic' code for SIGNAL_QUERYCLOSE
        if self.acceptclose():
            self._emit_event(SIGNAL_CLOSING)
            self._closed = True # set guard used above
            event.accept()
        else:
            event.ignore()
    
    def hideEvent(self, event):
        self._emit_event(SIGNAL_HIDDEN)

class PKDETopWindow(_PKDEMainMixin, app.PTopWindowBase):
    
    def __init__(self, parent, cls=None):
        _PKDEMainMixin.__init__(self)
        app.PTopWindowBase.__init__(self, parent, cls)
        self.setCentralWidget(self.clientwidget)
        # This has to be at the end so app.PTopWindowBase.__init__ has a chance
        # to read the about data from the client widget, if applicable
        self._init_icon()
    
    def show_init(self):
        app.PTopWindowBase.show_init(self)
        _PKDEMainMixin.show_init(self)

class PKDEApplication(kdecore.KApplication, app.PApplicationBase, _PKDECommunicator):
    """
    Customized KDE application class.
    """
    
    mainwidgetclass = PKDETopWindow
    
    def __init__(self, arglist=[], cls=None):
        if cls is None:
            klass = self.mainwidgetclass
        else:
            klass = cls
        if hasattr(klass, 'aboutdata') and (klass.aboutdata is not None):
            aboutdata = klass.aboutdata
        elif hasattr(klass, 'clientwidgetclass') and hasattr(klass.clientwidgetclass, 'aboutdata'):
            aboutdata = klass.clientwidgetclass.aboutdata
        else:
            aboutdata = None
        if aboutdata is not None:
            kaboutdata = _kdeparse(aboutdata)
        else:
            kaboutdata = kdecore.KAboutData('unnamed', 'unnamed', '0.0')
        kdecore.KCmdLineArgs.init(kaboutdata) # all the above because KDE requires this incantation first
        kdecore.KApplication.__init__(self)
        app.PApplicationBase.__init__(self, arglist, cls)
        self.mainwin = self.createMainWidget()
        self.setMainWidget(self.mainwin)
        
        # 'automagic' signal connection
        self.setup_notify(SIGNAL_BEFOREQUIT, self.before_quit)
    
    def _eventloop(self):
        self.exec_loop()
    
    def process_events(self):
        self.processEvents()
