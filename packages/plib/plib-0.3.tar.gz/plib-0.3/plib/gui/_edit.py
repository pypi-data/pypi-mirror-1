#!/usr/bin/env python
"""
Module EDIT -- Python Editor Objects
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Implements common 'editor' functionality for use as mixin
classes by various editing widgets.
"""

import os

from plib.gui.defs import *
from plib.gui._gui import gui_toolkit

if gui_toolkit != GUI_QT:
    def _editor_wrapper(target):
        def wrapper(*args, **kwargs):
            target()
        return wrapper

class PEditor(object):
    """
    A base class to provide 'editor' type methods.
    
    Can be used as a mixin or as a helper class; constructor sets up
    mainwidget field to point to appropriate widget for UI interface
    (expected to be a PMainWindow or derived class).
    
    Constructor can be passed a main widget (expected to be a PMainWindow
    or derived class so it has the appropriate methods); if not, it checks
    to see if it has a parent widget, and assumes that to be the main widget
    (for use when this is a mixin class for the client widget); otherwise it
    points to itself as the main widget (for use when this is a mixin class
    for the main widget -- note that subclasses should call this __init__
    *after* the main widget __init__).
    
    This class will work with the main widget's toolbar if it is a PToolbar,
    to keep the button enable/disable states up to date based on the current
    editing state. The 'state' includes:
    
    -- whether or not the editor is currently active ('editable')
    -- whether or not there are changes pending which have not been committed
    -- whether or not the editor has been modified but not saved
    
    The separation of 'pending' and 'modified' allows support of both
    transaction-based and file-based models in the same application.
    
    This class will update the caption of the main widget to reflect the
    'name' of the object being edited (which must be provided by overriding
    the _getname method--it does not have to be a system file name, but can
    be any string identifying the object) and the object type (which must be
    provided by overriding the _gettype method).
    """
    
    typesuffix = "Editor"
    captionformat = "%s %s - %s"
    
    signalmaps = {
        'loadsignals': 'load',
        'editsignals': 'edit',
        'changesignals': 'changed',
        'commitsignals': 'commit',
        'cancelsignals': 'cancel',
        'modifysignals': 'modify',
        'savesignals': 'save' }
    
    def __init__(self, mainwidget=None, control=None, data=None):
        if mainwidget is not None:
            self.mainwidget = mainwidget
        elif hasattr(self, '_parent') and (self._parent is not None):
            self.mainwidget = self._parent
        else:
            self.mainwidget = self
        if (self.mainwidget is not None):
            # This will serve for now to make sure main widget is
            # a main window instance
            if not hasattr(self.mainwidget, 'connectaction'):
                self.mainwidget = None
        
        if control is not None:
            self.control = control
        else:
            self.control = self
        self.data = data
        
        # flags to track state for button enable/disable
        self._editable = False
        self._pending = False
        self._modified = False
        
        # get pointer to toolbar update method
        if self.mainwidget is not None:
            self._updatefunc = self.mainwidget.updateactions
        else:
            self._updatefunc = None
        
        # connect to mapped signals
        for mapname, targetname in self.signalmaps.iteritems():
            self._setup_signals(mapname, targetname)
        
        # connect main widget actions to our methods
        if self.mainwidget is not None:
            self.mainwidget.connectaction(ACTION_FILESAVE, self.save)
            self.mainwidget.connectaction(ACTION_EDIT, self.edit)
            self.mainwidget.connectaction(ACTION_OK, self.commit)
            self.mainwidget.connectaction(ACTION_CANCEL, self.cancel)
        
        # connect control actions to our methods; note that this must
        # be separate from the signal mapping above because here we
        # need to preserve the signature of the control callback
        if self.control is not None:
            self._connect_control()
        
        # if we have a control and data, load data and populate control
        if (self.control is not None) and (self.data is not None):
            self.load()
    
    def _setup_signals(self, mapname, targetname):
        signalmap = getattr(self, mapname, None)
        target = getattr(self, targetname, None)
        if (signalmap is not None) and (target is not None):
            for signal, attrname in signalmap.iteritems():
                if attrname is not None:
                    source = getattr(self, attrname)
                else:
                    source = self
                
                # TODO: Get rid of this ugly hack by figuring out why the
                # wrapper doesn't get called in Qt/KDE like it should
                if gui_toolkit not in (GUI_QT, GUI_KDE):
                    source.setup_notify(signal, _editor_wrapper(target))
                else:
                    source.setup_notify(signal, target)
    
    def _connect_control(self):
        """ Override in derived classes to connect to appropriate control signals. """
        pass
    
    def _gettype(self):
        """ Override in derived classes to customize file type name for display """
        return "Object"
    
    def _getname(self):
        """ Override in derived classes to customize file name for display """
        return ""
    
    def _update(self):
        if self._updatefunc is not None:
            self._updatefunc()
    
    def _get_editable(self):
        return self._editable
    
    def _set_editable(self, value):
        if self._editable != value:
            self._editable = value
            self._update()
    
    def _get_pending(self):
        return self._pending
    
    def _set_pending(self, value):
        if self._pending != value:
            self._pending = value
            self._update()
    
    def _get_modified(self):
        return self._modified
    
    def _set_modified(self, value):
        if self._modified != value:
            self._modified = value
            self._update()
    
    editable = property(_get_editable, _set_editable)
    pending = property(_get_pending, _set_pending)
    modified = property(_get_modified, _set_modified)
    
    def _doload(self):
        """ override in derived classes to populate widget with file data """
        pass
    
    def _doedit(self):
        """ override in derived classes to activate editor """
        pass
    
    def _docommit(self):
        """ override in derived classes to commit transaction """
        pass
    
    def _docancel(self):
        """ override in derived classes to cancel transaction """
        pass
    
    def _domodify(self):
        """ override in derived classes to modify data """
        pass
    
    def _dosave(self):
        """ override in derived classes to save data from widget """
        pass
    
    def _format_caption(self):
        return self.captionformat % (self._gettype(), self.typesuffix, self._getname())
    
    def switchname(self):
        """ Call this method to update UI for new name """
        if self.mainwidget is not None:
            self.mainwidget.set_caption(self._format_caption())
    
    def load(self):
        """ Call this method to open the editor and load data """
        self._doload()
        self.pending = False
        self.modified = False
    
    def edit(self):
        """ Call this method to put editor into edit mode """
        if self.editable:
            self._doedit()
    
    def changed(self):
        """ Call this method when a transaction starts """
        if self.editable:
            self.pending = True
    
    def commit(self):
        """ Call this method to commit a transaction """
        self._docommit()
        self.pending = False
        self.modified = True
    
    def cancel(self):
        """ Call this method to cancel a transaction """
        self._docancel()
        self.pending = False
    
    def modify(self):
        """ Call this method when the data is modified outside a transaction """
        self._domodify()
        self.modified = True
    
    def save(self):
        """ Call this method to save changes to storage """
        self._dosave()
        self.modified = False
    
    def querycommit(self):
        """ ask user whether to commit uncommitted changes """
        result = self.mainwidget.messagebox.query3("Pending Changes",
            "There are uncommitted changes. Commit them?")
        if result == answerYes:
            self.commit()
        elif result == answerNo:
            self.cancel()
        return result
    
    def querysave(self):
        """ ask user whether to save unsaved files """
        result = self.mainwidget.messagebox.query3("Unsaved Data",
            "There is unsaved data. Save data?")
        if result == answerYes:
            self.save()
        return result
    
    def canclose(self):
        return ( ((not self.pending) or (self.querycommit() != answerCancel))
            and ((not self.modified) or (self.querysave() != answerCancel)) )

class PFileEditor(PEditor):
    """
    An editor class with richer file management capabilities.
    
    Constructor can be passed a file path (typical use expected to be as a
    helper class for a subwindow for file editing), or if not and this is
    the main widget (for use as mixin class), will open a file name dialog
    to let the user choose a file name (class constant can be changed to
    disable this behavior). The main widget's caption will show the
    pathname of the file.
    """
    
    captionformat = "%s %s [%s]"
    getfilename = True
    
    def __init__(self, mainwidget=None, filename="", control=None, data=None):
        PEditor.__init__(self, mainwidget, control, data)
        
        # connect more main widget actions
        if self.mainwidget is not None:
            self.mainwidget.connectaction(ACTION_FILEOPEN, self.openfile)
            self.mainwidget.connectaction(ACTION_FILESAVEAS, self.savefileas)
        
        # open file
        self.filename = filename
        if (self.filename == "") and self.getfilename:
            self.openfile()
        elif self.filename != "":
            self._dofileopen()
    
    def _getname(self):
        return self.filename
    
    def _dofileopen(self):
        if self.filename != "":
            self.load()
            self.switchname()
    
    def openfile(self):
        """ Select file name and open file """
        fname = self.mainwidget.getfiledialog()
        if len(fname) > 0:
            self.filename = str(fname)
        self._dofileopen()
    
    def _dofilesaveas(self):
        if self.filename != "":
            self.save()
            self.switchname()
    
    def savefileas(self):
        """ select new file name and save file """
        startpath, startfilter = os.path.splitext(self.filename)
        startpath = os.path.dirname(startpath)
        startfilter = "*" + startfilter
        fname = self.mainwidget.getfiledialog(startpath, startfilter, ACTION_FILESAVE)
        if len(fname) > 0:
            self.filename = str(fname)
        self._dofilesaveas()
