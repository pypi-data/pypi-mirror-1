#!/usr/bin/env python
"""
PYIDSERVER-GUI.PY
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

GUI for Python implementation of IDServer. See
PYIDSERVER.PY for more information about the basic
"engine" involved. This GUI overlay to the engine is
intended to demonstrate some key features of the
``plib.gui`` sub-package, as well as the general Unix
programming model of "build a base engine first, which
can be driven by a rudimentary command-line interface;
then build a GUI on top of it."

Key features:

  - The ``plib.gui.specs`` module is used to define
    the entire GUI in terms of Python lists and tuples.
    The only actual code involved is some setup after
    the GUI controls are instantiated, and the event
    handlers for the specific control events.
  
  - The event handlers themselves are "automagically"
    bound to their control event signals. This is done
    by making the name of the event handler bear a
    predictable relationship to the name of the control
    itself. The underlying code in the ``gui.PMainPanel``
    class then does the method lookups involved and
    binds the control signals to their targets. See the
    comments in the GUI spec definitions.
"""

import os

from plib import __version__

from plib.utils import version

from plib.gui import main as gui
from plib.gui import common
from plib.gui.defs import *

common.actiondict[ACTION_OK][1] = "&Go"

from plib.gui import specs
specs.mainwidth = 400
specs.mainheight = 300
del specs
from plib.gui.specs import *

import pyidserver

# Nested child lists for panels

IDServerPadding = [] # equates to an empty panel when processed

IDServerTopLeft = [
    # No event handler by default for an edit box, and the signal we want to
    # bind to (the Enter key) isn't the default signal anyway, so no event
    # handler here
    get_editbox('url') ]
IDServerTopRight = [
    # This action button has a non-standard name, so we have to specify it;
    # the ``go`` method of the main panel then becomes the target (buttons and
    # action buttons are the only spec controls that automatically assume they
    # have targets; this seems reasonable since that's what buttons are for)
    get_action_button(ACTION_OK, 'go') ]
IDServerTopPanel = [
    get_interior_panel(IDServerTopLeft, ALIGN_JUST, LAYOUT_HORIZONTAL, 'left'),
    get_interior_panel(IDServerTopRight, ALIGN_RIGHT, LAYOUT_HORIZONTAL, 'right') ]

IDServerMainControls = [
    # The empty string after each check box name means that the target event
    # handler method will be named ``<name>_check``, where ``<name>`` is the
    # base name of the control (the 2nd parameter)--note that in the specs code
    # the actual full name of the control will be ``checkbox_<name>``, to avoid
    # name collisions between controls of different types; for the combo box,
    # the handler method name will be ``<name>_selected``
    get_checkbox("DNS Only", 'dnsonly', ''),
    get_checkbox("Set Protocol", 'protocol', ''),
    get_combobox(sorted(pyidserver.protocols.iterkeys()), 'protocol', ''),
    get_checkbox("Set Port", 'portnum', ''),
    # No handler for the numedit, just need to keep it at a fixed size
    get_numeditbox('portnum', expand=False) ]
IDServerMainHeader = [
    get_toplevel_panel(IDServerMainControls, ALIGN_LEFT, LAYOUT_HORIZONTAL, 'controls'),
    get_padding('main') ]
IDServerMainBody = [
    # No event handler for the text control (since it's display-only anyway)
    get_textcontrol('output') ]
IDServerMainPanel = [
    get_midlevel_panel(IDServerMainHeader, ALIGN_TOP, LAYOUT_HORIZONTAL, 'header'),
    get_interior_panel(IDServerMainBody, ALIGN_JUST, LAYOUT_VERTICAL, 'body') ]

IDServerBottomPanel = [
    get_padding('bottom'),
    # These action buttons all have their standard names, so no additional
    # parameters are needed; each one's target will be the method with its
    # name: ``about``, ``about_toolkit``, and ``exit`` (note that the ``exit``
    # method is in the parent, which is the main window, not the main panel
    # itself; the automatic lookup method finds it by traversing the parent
    # tree if the method is not found in the panel)
    get_action_button(ACTION_ABOUT),
    get_action_button(ACTION_ABOUTTOOLKIT),
    get_action_button(ACTION_EXIT) ]

IDServerPanels = [
    get_toplevel_panel(IDServerTopPanel, ALIGN_TOP, LAYOUT_HORIZONTAL, 'top'),
    get_toplevel_panel(IDServerMainPanel, ALIGN_JUST, LAYOUT_VERTICAL, 'main'),
    get_toplevel_panel(IDServerBottomPanel, ALIGN_BOTTOM, LAYOUT_HORIZONTAL, 'bottom') ]

IDServerAboutData = {
    'name': "PyIDServer",
    'version': version.version_string(__version__),
    'copyright': "Copyright (C) 2008-2010 by Peter A. Donis",
    'license': "GNU General Public License (GPL) Version 2",
    'description': "A Python GUI for IDServer", 
    'developers': ["Peter Donis"],
    'website': "http://www.peterdonis.net",
    'icon': os.path.join(os.path.split(os.path.realpath(__file__))[0], "pyidserver.png") }

class IDServerFrame(gui.PMainPanel):
    
    aboutdata = IDServerAboutData
    defaultcaption = "PyIDServer"
    layout = LAYOUT_VERTICAL
    placement = (SIZE_CLIENTWRAP, MOVE_CENTER)
    
    childlist = IDServerPanels
    
    def _createpanels(self):
        # Create child widgets
        super(IDServerFrame, self)._createpanels()
        
        # The function we're wrapping with our GUI, and its default parameters
        self.func = pyidserver.run_main
        _, dns_only, protocol, portnum = self.func.func_defaults
        
        # Controls affected by the DNS Only checkbox
        self.dnsonly_controls = (
            (self.checkbox_protocol, self.combo_protocol),
            (self.checkbox_portnum, self.edit_portnum) )
        
        # Adjust some widget parameters that couldn't be set in constructors
        self.edit_url.setup_notify(SIGNAL_ENTER, self.go)
        
        self.checkbox_dnsonly.checked = dns_only
        self.dnsonly_check() # technically not necessary but put in for completeness
        
        if protocol == "":
            protocol = pyidserver.PROTO_DEFAULT
        self.combo_protocol.set_current_text(protocol)
        self.protocol_check()
        
        self.edit_portnum.edit_text = str(portnum)
        self.portnum_check()
        
        self.text_output.set_font("Courier New")
        
        # Set up output file-like object here for convenience
        self.outputfile = gui.PTextFile(self.text_output)
        
        # Set up a callback for the idserver async polling loop to keep the GUI running
        pyidserver.run_callback = self._parent.app.process_events
        
        # Start with keyboard focus in the URL text entry
        self.edit_url.set_focus()
    
    def dnsonly_check(self):
        """ Only enable protocol and port controls if not DNS only. """
        enable = not self.checkbox_dnsonly.checked
        for ctrl, subctrl in self.dnsonly_controls:
            ctrl.enabled = enable
            subctrl.enabled = enable and ctrl.checked
    
    def protocol_check(self):
        """ Sync protocol combo enable with check box """
        self.combo_protocol.enabled = self.checkbox_protocol.checked
    
    def protocol_selected(self, index):
        """ Protocol combo selection was made. """
        print index, self.combo_protocol[index] # this demonstrates the response to SIGNAL_SELECTED
    
    def portnum_check(self):
        """ Sync portnum edit enable with check box """
        self.edit_portnum.enabled = self.checkbox_portnum.checked
    
    def go(self):
        """ Go button was pushed or Enter key was pressed, execute query """
        
        # Clear output
        self.outputfile.truncate(0)
        
        # Check URL
        url = self.edit_url.edit_text
        if len(url) < 1:
            self.outputfile.write("Error: No URL entered.")
            self.outputfile.flush()
            return
        
        # Fill in arguments that user selected, if any
        dns_only = self.checkbox_dnsonly.checked
        if self.checkbox_protocol.checked:
            protocol = self.combo_protocol.current_text()
        else:
            protocol = self.func.func_defaults[2]
        if self.checkbox_portnum.checked:
            portnum = int(self.edit_portnum.edit_text)
        else:
            portnum = self.func.func_defaults[3]
        
        # Now execute
        self.func(self.outputfile, url,
            dns_only=dns_only, protocol=protocol, portnum=portnum)

if __name__ == "__main__":
    gui.runapp(IDServerFrame)
