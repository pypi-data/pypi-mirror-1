#!/usr/bin/env python
"""
Module LABEL -- GUI Text Label Widgets
Sub-Package GUI.WIDGETS of Package PLIB -- Python GUI Framework
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the widget classes for text label widgets.
"""

class PTextLabelBase(object):
    """
    Base class for a widget that just displays text.
    """
    
    def __init__(self, text=None):
        if text is not None:
            self.set_text(text)
    
    def get_text(self):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
    
    def set_text(self, value):
        """ Placeholder for derived classes to implement. """
        raise NotImplementedError
