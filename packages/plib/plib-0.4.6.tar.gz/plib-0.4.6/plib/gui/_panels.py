#!/usr/bin/env python
"""
Module PANELS -- Dialog Classes for GUI
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines panels for use with PLIB.GUI applications. The
PMainPanel class adds convenience items to PAutoPanel to
make it easier to use as the client widget of your GUI
application's main window.
"""

from plib.gui import main as gui
from plib.gui import specs
from plib.gui.defs import *

class PMainPanel(gui.PAutoPanel):
    
    baseclass = gui.PAutoPanel # so sub-panels will construct properly
    
    align=ALIGN_JUST
    layout = LAYOUT_NONE
    margin = specs.framemargin
    spacing = specs.panelspacing
    style=PANEL_NONE
    
    def __init__(self, parent):
        c_align = self.align
        c_layout = self.layout
        c_margin = self.margin
        c_spacing = self.spacing
        c_style = self.style
        gui.PAutoPanel.__init__(self, parent, layout=c_layout, style=c_style,
            align=c_align, margin=c_margin, spacing=c_spacing)
