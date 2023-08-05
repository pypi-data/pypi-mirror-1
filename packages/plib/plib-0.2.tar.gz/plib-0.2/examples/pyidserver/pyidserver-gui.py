#!/usr/bin/env python
"""
PYIDSERVER-GUI.PY
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

GUI for Python implementation of IDServer.
See PYIDSERVER.PY for more information.
"""

import os

from plib.gui import main as gui
from plib.gui import common
from plib.gui.defs import *

import pyidserver

offset = 4
combowidth = 90
buttonwidth = 110
outputheight = 400

framemargin = 10
panelspacing = 10

class IDServerOutputFile(object):
    """
    File-like object to redirect output to text control. Note
    that 'file-like' is used very loosely; this object only
    implements the minimum necessary to work with idserver.
    """
    
    def __init__(self, control):
        self.control = control
    
    def write(self, data):
        data = "".join([self.control.edit_text, data])
        self.control.edit_text = data
    
    def flush(self):
        self.control.update()

# Monkey patch common definitions

common.actiondict[ACTION_OK][1] = "&Go"

# Nested child lists for panels

button_geometry = (None, None, buttonwidth, None)
combo_geometry = (None, None, combowidth, None)
output_geometry = (None, None, None, outputheight)

IDServerPadding = [] # equates to an empty panel when processed

IDServerTopLeft = [
    (gui.PEditBox, (), {}, 'edit_url') ]
IDServerTopRight = [ (gui.PButton, (ACTION_OK, ""), {'geometry': button_geometry}, 'button_go') ] 
IDServerTopPanel = [ 
    (IDServerTopLeft, (), {'align': ALIGN_JUST, 'layout': LAYOUT_HORIZONTAL},
        'panel_left'),
    (IDServerTopRight, (), {'align': ALIGN_RIGHT, 'layout': LAYOUT_HORIZONTAL,
        'margin': offset}, 'panel_right') ]

IDServerMainControls = [
    (gui.PCheckBox, ("DNS Only",), {}, 'checkbox_dnsonly'),
    (gui.PCheckBox, ("Set Protocol",), {}, 'checkbox_protocol'),
    (gui.PComboBox, (sorted(pyidserver.protocols.keys()),), {'geometry': combo_geometry},
        'combo_protocol'),
    (gui.PCheckBox, ("Set Port",), {}, 'checkbox_portnum') ]
IDServerMainEdit = [
    (gui.PEditBox, (), {'expand': False}, 'edit_portnum') ]
IDServerMainHeader = [
    (IDServerMainControls, (), {'align': ALIGN_LEFT, 'layout': LAYOUT_HORIZONTAL,
        'margin': offset, 'spacing': panelspacing}, 'panel_controls'),
    (IDServerMainEdit, (), {'align': ALIGN_LEFT, 'layout': LAYOUT_HORIZONTAL},
        'panel_edit'),
    (IDServerPadding, (), {}, 'padding_main') ]
IDServerMainBody = [
    (gui.PEditControl, (), {'geometry': output_geometry, 'scrolling': True}, 'text_output') ]
IDServerMainPanel = [ 
    (IDServerMainHeader, (), {'align': ALIGN_TOP, 'layout': LAYOUT_HORIZONTAL,
        'spacing': panelspacing}, 'panel_header'),
    (IDServerMainBody, (), {'align': ALIGN_JUST, 'layout': LAYOUT_VERTICAL}, 'panel_body') ]

IDServerBottomPanel = [
    (gui.PButton, (ACTION_ABOUT, ""), {'geometry': button_geometry}, 'button_about'), # 
    (gui.PButton, (ACTION_EXIT, ""), {'geometry': button_geometry}, 'button_quit'),
    (IDServerPadding, (), {}, 'padding_bottom') ]

# Helper function for patching frame event handlers into above gui specs
def _update_obj(klass, index, target):
    klass[index][2].update({'target': target})

IDServerAboutData = {
    'name': "PyIDServer",
    'version': "0.2",
    'copyright': "Copyright (C) 2008",
    'license': "GNU General Public License (GPL) Version 2",
    'description': "A Python GUI for IDServer", 
    'developers': ["Peter Donis"],
    'website': "http://www.peterdonis.net",
    'icon': os.path.join(os.path.split(os.path.realpath(__file__))[0], "pyidserver.png") }

class IDServerFrame(gui.PAutoPanel):
    
    aboutdata = IDServerAboutData
    defaultcaption = "PyIDServer"
    
    childlist = [ 
        (IDServerTopPanel, (), {'align': ALIGN_TOP, 'layout': LAYOUT_HORIZONTAL,
            'spacing': panelspacing}, 'panel_top'),
        (IDServerMainPanel, (), {'align': ALIGN_JUST, 'layout': LAYOUT_VERTICAL,
            'spacing': panelspacing}, 'panel_main'),
        (IDServerBottomPanel, (), {'align': ALIGN_BOTTOM, 'layout': LAYOUT_HORIZONTAL,
            'margin': offset, 'spacing': panelspacing}, 'panel_bottom') ]
    
    def __init__(self, parent):
        gui.PAutoPanel.__init__(self, parent, layout=LAYOUT_VERTICAL,
            margin=framemargin, spacing=panelspacing)
    
    def _createpanels(self):
        # Monkey patch widget creation parameters with our events
        _update_obj(IDServerTopRight, 0, self.go)
        _update_obj(IDServerMainControls, 2, self.selected_protocol)
        _update_obj(IDServerBottomPanel, 0, self._parent.about)
        _update_obj(IDServerBottomPanel, 1, self._parent.exit)
        
        # Connect control signals for sync of user interface
        _update_obj(IDServerMainControls, 1, self.protocol_check)
        _update_obj(IDServerMainControls, 3, self.portnum_check)
        
        # Create child widgets
        super(gui.PAutoPanel, self)._createpanels()
        
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
        self.text_output.readonly = True
        
        # Set up output file-like object here for convenience
        self.outputfile = IDServerOutputFile(self.text_output)
        
        # Start with keyboard focus in the URL text entry
        self.edit_url.set_focus()
    
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
        self.text_output.edit_text = ""
        
        # Check URL
        url = self.edit_url.edit_text
        if len(url) < 1:
            self.text_output.edit_text = "Error: No URL entered."
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
