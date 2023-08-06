#!/usr/bin/env python
"""
PYIDSERVER-GUI.PY
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

GUI for Python implementation of IDServer. See
PYIDSERVER.PY for more information.
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
    get_editbox('url') ]
IDServerTopRight = [
    get_action_button(ACTION_OK, 'go') ]
IDServerTopPanel = [
    get_interior_panel(IDServerTopLeft, ALIGN_JUST, LAYOUT_HORIZONTAL, 'left'),
    get_interior_panel(IDServerTopRight, ALIGN_RIGHT, LAYOUT_HORIZONTAL, 'right') ]

IDServerMainControls = [
    get_checkbox("DNS Only", 'dnsonly'),
    get_checkbox("Set Protocol", 'protocol'),
    get_combobox(sorted(pyidserver.protocols.iterkeys()), 'protocol'),
    get_checkbox("Set Port", 'portnum') ]
IDServerMainEdit = [
    get_numeditbox('portnum', False) ]
IDServerMainHeader = [
    get_toplevel_panel(IDServerMainControls, ALIGN_LEFT, LAYOUT_HORIZONTAL, 'controls'),
    get_interior_panel(IDServerMainEdit, ALIGN_LEFT, LAYOUT_HORIZONTAL, 'edit'),
    get_padding('main') ]
IDServerMainBody = [
    get_textdisplay('output') ]
IDServerMainPanel = [
    get_midlevel_panel(IDServerMainHeader, ALIGN_TOP, LAYOUT_HORIZONTAL, 'header'),
    get_interior_panel(IDServerMainBody, ALIGN_JUST, LAYOUT_VERTICAL, 'body') ]

IDServerBottomPanel = [
    get_action_button(ACTION_ABOUT, 'about'),
    get_action_button(ACTION_EXIT, 'quit'),
    get_padding('bottom') ]

# Helper function for patching frame event handlers into above gui specs
def _update_obj(klass, index, target):
    klass[index][2]['target'] = target

IDServerAboutData = {
    'name': "PyIDServer",
    'version': version.version_string(__version__),
    'copyright': "Copyright (C) 2008",
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
    
    childlist = [
        get_toplevel_panel(IDServerTopPanel, ALIGN_TOP, LAYOUT_HORIZONTAL, 'top'),
        get_toplevel_panel(IDServerMainPanel, ALIGN_JUST, LAYOUT_VERTICAL, 'main'),
        get_toplevel_panel(IDServerBottomPanel, ALIGN_BOTTOM, LAYOUT_HORIZONTAL, 'bottom') ]
    
    def _createpanels(self):
        # Monkey patch widget creation parameters with our events
        _update_obj(IDServerTopRight, 0, self.go)
        _update_obj(IDServerMainControls, 2, self.selected_protocol)
        _update_obj(IDServerBottomPanel, 0, self._parent.about)
        _update_obj(IDServerBottomPanel, 1, self._parent.exit)
        
        # Connect control signals for sync of user interface
        _update_obj(IDServerMainControls, 0, self.dns_check)
        _update_obj(IDServerMainControls, 1, self.protocol_check)
        _update_obj(IDServerMainControls, 3, self.portnum_check)
        
        # Create child widgets
        super(IDServerFrame, self)._createpanels()
        
        # Adjust some widget parameters that couldn't be set in constructors
        self.edit_url.setup_notify(SIGNAL_ENTER, self.go)
        _, dns_only, protocol, portnum = pyidserver.run_main.func_defaults
        self.checkbox_dnsonly.checked = dns_only
        if protocol == "":
            protocol = pyidserver.PROTO_DEFAULT
        self.combo_protocol.set_current_text(protocol)
        self.protocol_check()
        self.edit_portnum.edit_text = str(portnum)
        self.portnum_check()
        self.text_output.set_font("Courier New")
        #self.text_output.readonly = True
        
        # Set up output file-like object here for convenience
        self.outputfile = gui.PTextFile(self.text_output)
        
        # Set up a callback for the idserver async polling loop to keep the GUI running
        pyidserver.run_callback = self._parent.app.process_events
        
        # Start with keyboard focus in the URL text entry
        self.edit_url.set_focus()
    
    def dns_check(self):
        """ Only enable protocol and port controls if not DNS only. """
        enable = not self.checkbox_dnsonly.checked
        for ctrl, subctrl in ((self.checkbox_protocol, self.combo_protocol),
            (self.checkbox_portnum, self.edit_portnum)):
                ctrl.enabled = enable
                subctrl.enabled = enable and ctrl.checked
    
    def protocol_check(self):
        """ Sync protocol combo enable with check box """
        self.combo_protocol.enabled = self.checkbox_protocol.checked
    
    def portnum_check(self):
        """ Sync portnum edit enable with check box """
        self.edit_portnum.enabled = self.checkbox_portnum.checked
    
    def selected_protocol(self, index):
        """ Protocol combo selection was made. """
        print index, self.combo_protocol[index] # this demonstrates the response to SIGNAL_SELECTED
    
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
        
        # Hack to grab default values from function in pyidserver
        func = pyidserver.run_main
        _, dns_only, protocol, portnum = func.func_defaults
        
        # Fill in arguments that user selected, if any
        dns_only = self.checkbox_dnsonly.checked
        if self.checkbox_protocol.checked:
            protocol = self.combo_protocol.current_text()
        if self.checkbox_portnum.checked:
            portnum = int(self.edit_portnum.edit_text)
        
        # Now execute
        func(self.outputfile, url, **{'dns_only': dns_only, 'protocol': protocol, 'portnum': portnum})

if __name__ == "__main__":
    gui.runapp(IDServerFrame)
