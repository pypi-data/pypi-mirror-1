#!/usr/bin/env python
"""
Module KDECOMMON -- Python KDE Common Objects
Sub-Package GUI.TOOLKITS.KDE of Package PLIB -- Python GUI Toolkits
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common KDE GUI objects for use by the other
KDE modules.
"""

import qt

from plib.gui.defs import *

_kdealignmap = {
    ALIGN_LEFT: qt.Qt.AlignLeft,
    ALIGN_CENTER: qt.Qt.AlignCenter,
    ALIGN_RIGHT: qt.Qt.AlignRight }

_kdecolormap = {
    COLOR_BLACK: qt.QColor('black'),
    COLOR_RED: qt.QColor('red'),
    COLOR_BLUE: qt.QColor('blue'),
    COLOR_GREEN: qt.QColor('green'),
    COLOR_YELLOW: qt.QColor('yellow'),
    COLOR_WHITE: qt.QColor('white') }

_kdemessagefuncs = {
    MBOX_INFO: qt.QMessageBox.information,
    MBOX_WARN: qt.QMessageBox.warning,
    MBOX_ERROR: qt.QMessageBox.critical,
    MBOX_QUERY: qt.QMessageBox.question }

_kdesignalmap = {
    SIGNAL_ACTIVATED: "activated()",
    SIGNAL_CLICKED: "clicked()",
    SIGNAL_TOGGLED: "clicked()",
    SIGNAL_SELECTED: "activated(int)",
    SIGNAL_LISTVIEWCHANGED: "currentChanged(QListViewItem*)",
    SIGNAL_TABLECHANGED: "valueChanged(int, int)",
    SIGNAL_TEXTCHANGED: "textChanged()",
    SIGNAL_EDITCHANGED: "textChanged(const QString&)",
    SIGNAL_ENTER: "returnPressed(const QString&)",
    SIGNAL_TABCHANGED: "currentChanged(QWidget*)",
    SIGNAL_BEFOREQUIT: "aboutToQuit()" }

_kdeeventmap = {
    SIGNAL_CLOSING: "closeEvent",
    SIGNAL_HIDDEN: "hideEvent" }

def _kdemap(signal):
    if signal in _kdesignalmap:
        return qt.SIGNAL(_kdesignalmap[signal])
    elif signal in _kdeeventmap:
        return qt.PYSIGNAL(_kdeeventmap[signal])
    else:
        return None

# NOTE: we don't need to define 'wrapper' methods here like we do under GTK and
# wxWidgets because Qt silently discards any extra parameters that are not
# accepted by a signal handler. (BTW, this is good because wrappers don't seem
# to work like they should in Qt -- see PEDIT.PY, PEditor._setup_signals.)

class _PKDECommunicator(object):
    """
    A mixin class to abstract signal/slot functionality in KDE.
    """
    
    def setup_notify(self, signal, target):
        if signal in _kdeeventmap:
            # hack to make KDE event methods look like signals
            if not hasattr(self, _kdeeventmap[signal]):
                return
            self.enabled_events[signal] = True
        qt.QObject.connect(self, _kdemap(signal), target)
    
    def do_notify(self, signal, *args):
        sig = _kdemap(signal)
        if sig is not None:
            self.emit(sig, args)
    
    # need the following for widget events that have to have an overridden
    # handler defined in the class (can't "substitute on the fly") so that
    # they can work like signals
    
    enabled_events = {}
    
    def _emit_event(self, signal):
        if signal in self.enabled_events:
            self.do_notify(signal)

class _PKDEWidgetBase(object):
    """ Mixin class to provide minimal KDE widget methods. """
    
    def preferred_width(self):
        return self.sizeHint().width()
    
    def preferred_height(self):
        return self.sizeHint().height()

class _PKDEClientWidget(_PKDECommunicator, _PKDEWidgetBase):
    """ Mixin class for KDE client widgets. """
    
    def get_font_name(self):
        return self.font().family()
    
    def get_font_size(self):
        return self.font().pointSize()
    
    def set_font(self, font_name, font_size=None):
        if font_size is None:
            font_size = default_font_size
        self.setFont(qt.QFont(font_name, font_size))

class _PKDEWidget(_PKDEClientWidget):
    """ Mixin class to provide some more 'standard' KDE widget methods. """
    
    def set_width(self, width):
        self.resize(width, self.height())
    
    def set_height(self, height):
        self.resize(self.width(), height)
    
    def set_position(self, left, top):
        if not (None in (left, top)):
            self.move(left, top)
    
    def _get_enabled(self):
        return self.isEnabled()
    
    def _set_enabled(self, value):
        self.setEnabled(value)
    
    enabled = property(_get_enabled, _set_enabled)
    
    def set_focus(self):
        self.setFocus()
