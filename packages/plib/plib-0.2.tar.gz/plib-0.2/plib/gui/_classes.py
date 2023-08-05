#!/usr/bin/env python
"""
Module CLASSES -- Common GUI Classes
Sub-Package GUI of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines common classes that can be used with GUI objects.
"""

from plib.gui.defs import *

class PHeaderLabel(object):
    """ Encapsulates a header label for a table or list/tree view. """
    
    def __init__(self, text, width=-1, align=ALIGN_LEFT, readonly=False):
        self.text = text
        self.width = width
        self.align = align
        self.readonly = readonly
    
    def __str__(self):
        return self.text
