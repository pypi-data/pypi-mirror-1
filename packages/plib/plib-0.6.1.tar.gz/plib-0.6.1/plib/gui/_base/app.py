#!/usr/bin/env python
"""
Module APP -- GUI Application Classes
Sub-Package GUI.BASE of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the classes that form the basic GUI application framework.
"""

from plib.gui.defs import *

class PAboutDialogBase(object):
    """
    Base class for about dialogs; allows mapping of standard fields
    in about data to methods of about dialog that will process the
    data, by hacking __getattribute__ to substitute attribute names
    on the fly.
    """
    
    attrmap = {}
    
    def __init__(self, parent):
        self.mainwidget = parent
    
    def __getattribute__(self, name):
        # Monkeypatch attribute name if necessary
        attrmap = super(PAboutDialogBase, self).__getattribute__('attrmap')
        if name in attrmap:
            name = attrmap[name]
        return super(PAboutDialogBase, self).__getattribute__(name)

class PTopWindowBase(object):
    """
    Base class for 'top window' widgets.
    
    A top window is a 'plain' main application window; it has no
    frills like menus, toolbars, status bars, etc. built in (if
    you want those frills, use PMainWindow instead). It does have
    some basic functionality, however, using the following class
    fields:
    
    aboutdialogclass -- gives the class to be used to display the 'about' dialog
    box. This class is normally set internally to PLIB and should not need to be
    overridden by the user.
    
    clientwidgetclass -- gives the class of the client widget (actually it can
    be any callable with the right signature that returns a widget); if None,
    no client widget is created automatically (but widgets can still be created
    manually in user code). The callable must take one argument, which will be
    the PTopWindow instance creating it.
    
    Note that all the rest of the options below can be read from a client
    widget class, so the need to set them by subclassing PTopWindow directly
    should be rare:
    
    defaultcaption -- gives the caption if no editor object is found
    
    sizeoffset -- how many pixels from the edge of the screen this window should
    be sized
    
    centered -- whether this window should be centered in the screen if it's the
    main widget of the app (centering can also be done manually by calling the
    center method)
    
    sized -- whether this window should be sized using sizeoffset if it's the
    main widget of the app (sizing can also be done manually by calling the
    sizetoscreen method)
    
    maximized -- whether this window should be maximized
    
    clientwrap -- whether this window should be sized just large enough to wrap
    its client widget
    
    aboutdata -- gives data for display in the 'about' dialog.
    """
    
    aboutdata = None
    defaultcaption = "Top Window"
    clientwidgetclass = None
    aboutdialogclass = None
    placement = (SIZE_NONE, MOVE_NONE)
    sizeoffset = 160
    
    _clientattrs = ('aboutdata', 'defaultcaption', 'sizeoffset', 'placement')
    
    def __init__(self, parent, cls=None):
        self.shown = False
        
        # Figure out if parent is another window or the application
        if hasattr(parent, 'app'):
            self.app = parent.app
            self._parent = parent
        elif isinstance(parent, PApplicationBase):
            self.app = parent
            self._parent = None
        else:
            # This shouldn't happen, but just in case...
            self.app = None
            self._parent = None
        
        self._set_client_class(cls)
        
        self.set_caption(self.defaultcaption)
        self.clientwidget = self.createclient()
    
    def _set_client_class(self, cls):
        if cls is not None:
            self.clientwidgetclass = cls
        if self.clientwidgetclass is not None:
            cls = self.clientwidgetclass
            for attrname in self._clientattrs:
                if hasattr(cls, attrname):
                    setattr(self, attrname, getattr(cls, attrname))
                elif not hasattr(self, attrname):
                    setattr(self, attrname, None)
    
    def set_caption(self, caption):
        """ Placeholder for derived classes to implement. """
        pass
    
    def createclient(self):
        """ Create the client widget if its class is given """
        
        if self.clientwidgetclass is not None:
            return self.clientwidgetclass(self)
        else:
            return None
    
    def sizetoscreen(self, maximized):
        """ Size the window to be sizeoffset pixels from each screen edge --
        placeholder for derived classes """
        pass
    
    def sizetoclient(self, clientwidth, clientheight):
        """ Size the window to fit the given client size -- placeholder for
        derived classes """
        pass
    
    def center(self):
        """ Center the window in the primary screen -- placeholder for derived classes """
        pass
    
    def show_init(self):
        """ Should always call from derived classes to ensure proper setup """
        if not self.shown:
            # Do placement just before showing for first time
            size, pos = self.placement
            if size == SIZE_CLIENTWRAP:
                c = self.clientwidget
                self.sizetoclient(c.preferred_width(), c.preferred_height())
            elif size in (SIZE_MAXIMIZED, SIZE_OFFSET):
                self.sizetoscreen(size == SIZE_MAXIMIZED)
            if (pos == MOVE_CENTER) and (size != SIZE_MAXIMIZED):
                self.center()
            self.shown = True
    
    def about(self):
        if (self.aboutdata is not None) and (self.aboutdialogclass is not None):
            dialog = self.aboutdialogclass(self)
            for key, item in self.aboutdata.iteritems():
                getattr(dialog, key)(item)
            dialog.display()
    
    def acceptclose(self):
        """ Return False if window should not close based on current state. """
        return True
    
    def exit(self):
        """ Placeholder for derived classes to implement. """
        pass

class PApplicationBase(object):
    """
    Base class for GUI application.
    
    Automatically sizes the main widget and centers it in
    the primary screen if the widget's class flags are set
    appropriately (see PTopWindow).
    
    Descendant app classes should set the class variable
    mainwidgetclass to the appropriate class object. If this
    is the only customization you want to do, however, you do
    not need to subclass this class--just pass your main window
    class derived from PTopWindow to the runapp function;
    see that function's docstring. The only time you should need
    to subclass PApplication is to override createMainWidget (to
    alter the parameters passed to the main widget, or do other
    processing after it's created but before the rest of __init__)
    or to provide other functionality that has to be at the
    application level rather than in the main widget (but this
    should be extremely rare).
    """
    
    mainwidgetclass = PTopWindowBase
    
    def __init__(self, arglist=[], cls=None):
        self.arglist = arglist
        self.mainwin = None
        
        # set up main widget class
        if cls is not None:
            self.mainwinclass = cls
        else:
            self.mainwinclass = self.mainwidgetclass
    
    def createMainWidget(self):
        """ Create the main widget and return it """
        
        if issubclass(self.mainwinclass, PTopWindowBase):
            result = self.mainwinclass(self)
        else:
            result = self.mainwidgetclass(self, self.mainwinclass)
        return result
    
    def _eventloop(self):
        """ Placeholder for derived classes for main event loop """
        pass
    
    def run(self):
        """ Show the main widget and run the main event loop """
        
        self.mainwin.show_init()
        self._eventloop()
    
    def before_quit(self):
        """ Placeholder for derived classes to do destructor-type processing """
        pass
