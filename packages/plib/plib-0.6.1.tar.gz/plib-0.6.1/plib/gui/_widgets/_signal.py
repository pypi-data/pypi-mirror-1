#!/usr/bin/env python
"""
Module SIGNAL -- Base for GUI Signal Emitting Controls
Sub-Package GUI.BASE of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2009 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines an abstract base class for all signal-emitting control widgets.
"""

from plib.gui.common import *
from plib.gui._base import _notify

class _PNotifyControl(_notify._PNotifyBase):
    """
    Base class for controls that will be passed a signal target in
    the constructor.
    """
    
    def __init__(self, target=None):
        if target is not None:
            self.connect_to(target)
