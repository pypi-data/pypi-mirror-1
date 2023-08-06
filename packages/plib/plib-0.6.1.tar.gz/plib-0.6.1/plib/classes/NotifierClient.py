#!/usr/bin/env python
"""
Module NotifierClient
Sub-Package CLASSES of Package PLIB
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the NotifierClient class. This is
a mixin class designed to allow an async socket I/O class
to multiplex its event loop with a GUI event loop. Due to
limitations in some GUI toolkits, this functionality is
implemented in two different ways, depending on the toolkit
in use:

- For Qt, Qt 4, and KDE, the PSocketNotifier class is present,
  and its functionality is used to allow the GUI event loop to
  respond to socket events. This is the desired approach.

- For GTK and wxWidgets, there is no straightforward way to
  make the GUI event loop "see" socket events; there are possible
  approaches involving threading, but these are complex and prone
  to brittleness. Instead, the kludgy but workable approach is
  taken of making the asnyc socket I/O ``select loop the "primary"
  one, and using the GUI application's ``process_events`` method
  to pump its events based on a ``select`` timeout.
"""

from plib.gui import main as gui

if hasattr(gui, 'PSocketNotifier'): # Qt, Qt 4, and KDE
    
    import asyncore
    
    from plib.gui.defs import *
    
    notify_methods = {
        NOTIFY_READ: ('readable', 'read'),
        NOTIFY_WRITE: ('writable', 'write') }
    
    class NotifierClient(object):
        
        notifier_class = gui.PSocketNotifier
        notifiers = None
        
        def get_notifier(self, notify_type):
            sfn, nfn = notify_methods[notify_type]
            result = self.notifier_class(self, notify_type, getattr(self, sfn), getattr(asyncore, nfn))
            result.auto_enable = False # we'll take care of the re-enable ourselves
            return result
        
        def check_notifiers(self):
            if self.notifiers:
                for notifier in self.notifiers:
                    notifier.set_enabled(notifier.select_fn())
        
        def do_connect(self, addr):
            super(NotifierClient, self).do_connect(addr)
            if self.connected or self.connect_pending:
                self.notifiers = [self.get_notifier(t) for t in (NOTIFY_READ, NOTIFY_WRITE)]
                self.check_notifiers()
        
        def start(self, data):
            super(NotifierClient, self).start(data)
            self.check_notifiers()
        
        def handle_write(self):
            super(NotifierClient, self).handle_write()
            self.check_notifiers()
        
        def handle_read(self):
            super(NotifierClient, self).handle_read()
            self.check_notifiers()
        
        def handle_close(self):
            if self.notifiers:
                del self.notifiers[:]
            super(NotifierClient, self).handle_close()

else: # GTK and wxWidgets
    
    app_obj = None
    
    class NotifierClient(object):
        
        poll_timeout = 0.1
        
        def do_connect(self, addr):
            super(NotifierClient, self).do_connect(addr)
            if self.connected or self.connect_pending:
                app_obj.notifier_client = self
        
        def handle_close(self):
            app_obj.notifier_client = None
            super(NotifierClient, self).handle_close()
    
    class NotifierApplication(gui.PApplication):
        
        notifier_client = None
        
        def createMainWidget(self):
            """
            Store pointer to self in the NotifierClient class. Note that the client
            object *must* be instantiated before our event loop is called, or no
            socket I/O events will be processed.
            """
            
            global app_obj
            app_obj = self
            return super(NotifierApplication, self).createMainWidget()
        
        def _eventloop(self):
            """
            Override app to use the network I/O client as the 'main' loop, not the GUI;
            the GUI event pump will be called by the async loop each timeout.
            """
            
            if self.notifier_client is not None:
                self.process_events() # start with a clean slate
                self.notifier_client.do_loop(self.process_events)
                self.process_events() # make sure we clear all events before exiting
            else:
                super(NotifierApplication, self)._eventloop()
    
    gui.default_appclass[0] = NotifierApplication
