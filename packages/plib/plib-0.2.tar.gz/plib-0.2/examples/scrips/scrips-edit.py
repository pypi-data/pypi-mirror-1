#!/usr/bin/env python
"""
SCRIPS-EDIT.PY
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Editor for scrips.dat file used to keep track of
prescription refills.
"""

import sys
import os
import datetime

from plib.gui import main as gui
from plib.gui import common
from plib.gui.defs import *

import scrips

# Monkeypatch common menu and toolbar items

common.actiondict[ACTION_EDIT][0] = common.actiondict[ACTION_OK][0]
common.actiondict[ACTION_EDIT][1] = "&Submit"
common.actiondict[ACTION_REFRESH][1] = "&Refill"

class ScripEditable(scrips.Scrip):
    
    init_name = "<Name>"
    init_rxnum = "<Rx#>"
    init_days = 30
    init_refills = 0
    init_submitted = False
    
    def __init__(self, tokens=None):
        if tokens is None:
            # The default of today's date takes care of the filldate field since
            # there's no init class field for it
            tokens = [str(getattr(self, 'init_%s' % name, datetime.date.today()))
                for name, _ in self.converters]
        scrips.Scrip.__init__(self, tokens)
    
    def submit(self):
        self.submitted = True
    
    def refill(self):
        self.filldate = datetime.date.today()
        self.refills -= 1
        self.submitted = False
    
    def outputline(self):
        return "".join([self[col].ljust(heading.chars)
            for col, heading in enumerate(headings)])

# This will cause scrips.scriplist() to return a list of ScripEditables
scrips.scripclass = ScripEditable

class ScripLabel(gui.PHeaderLabel):
    
    def __init__(self, text, chars, width=-1, align=ALIGN_LEFT, readonly=False):
        gui.PHeaderLabel.__init__(self, text, width, align, readonly)
        self.chars = chars
    
    def outputlabel(self, index):
        result = self.text
        if index == 0:
            result = "".join(["#", result])
        return result.ljust(self.chars)

headings = [ScripLabel("Drug", 16, 150),
    ScripLabel("Rx", 12, 100),
    ScripLabel("Last Filled", 16, 100),
    ScripLabel("Days", 8, 100),
    ScripLabel("Refills Left", 16, 100),
    ScripLabel("Submitted", 0, 100)]

class ScripList(gui.PTableEditor, gui.PTable):
    
    def __init__(self, parent):
        gui.PTable.__init__(self, parent, headings)
        gui.PTableEditor.__init__(self, data=scrips.scriplist())
        for row in range(len(self)):
            self.setcolors(row)
        self.editable = True
    
    def setcolors(self, row=None):
        if row is None:
            row = self.current_row()
        scrip = self.data[row]
        if scrip.due():
            if scrip.submitted:
                self.set_row_fgcolor(row, self.default_fgcolor())
            else:
                self.set_row_fgcolor(row, COLOR_RED)
            self.set_row_bkcolor(row, COLOR_YELLOW)
        else:
            self.set_row_fgcolor(row, self.default_fgcolor())
            self.set_row_bkcolor(row, self.default_bkcolor())
    
    def tablechanged(self, row, col):
        super(ScripList, self).tablechanged(row, col)
        self.setcolors(row)
    
    def _dosave(self):
        lines = self.outputlines()
        f = open(scrips.scripsdatfile(), 'w')
        f.writelines(lines)
        f.close()
    
    def _doupdate(self, row):
        self.control[row]._update(self.data[row])
        self.setcolors(row)
        self.modified = True
    
    def submitscrip(self):
        row = self.current_row()
        self.data[row].submit()
        self._doupdate(row)
    
    def refillscrip(self):
        row = self.current_row()
        self.data[row].refill()
        self._doupdate(row)
    
    def set_min_size(self, width, height):
        gui.PTable.set_min_size(self, width, height)
        if sys.platform != 'darwin':
            # FIXME: figure out why wx on OSX throws 'Bus error' on this -- it
            # appears to be in the GetSizeTuple call
            self._parent.sizetoclient(width, height)
    
    def addscrip(self):
        self.append(scrips.scripclass())
        self.set_min_size(self.minwidth(), self.minheight())
        self.modified = True
    
    def delscrip(self):
        msg = "Do you really want to delete %s?" % self.data[self.current_row()].name
        if self._parent.messagebox.query2("Delete Prescription", msg) == answerOK:
            del self[self.current_row()]
            self.set_min_size(self.minwidth(), self.minheight())
            self.modified = True
    
    def headerline(self):
        return "".join([heading.outputlabel(index) for index, heading in enumerate(headings)])
    
    def outputlines(self):
        return os.linesep.join([self.headerline()] + [scrip.outputline() for scrip in self.data])

ScripsAboutData = {
    'name': "ScripsEdit",
    'version': "0.2",
    'copyright': "Copyright (C) 2008",
    'license': "GNU General Public License (GPL) Version 2",
    'description': "Prescription Editor", 
    'developers': ["Peter Donis"],
    'website': "http://www.peterdonis.net",
    'icon': os.path.join(os.path.split(os.path.realpath(__file__))[0], "scrips.png") }

class ScripsWindow(gui.PMainWindow):
    
    aboutdata = ScripsAboutData
    actionflags = [ACTION_FILESAVE, ACTION_EDIT, ACTION_REFRESH, ACTION_ADD, ACTION_REMOVE,
        ACTION_ABOUT, ACTION_EXIT]
    defaultcaption = "Prescription List Editor"
    clientwidgetclass = ScripList
    editorclass = ScripList
    sized = False
    
    def __init__(self, app):
        gui.PMainWindow.__init__(self, app)
        self.connectaction(ACTION_EDIT, self.editor.submitscrip)
        self.connectaction(ACTION_REFRESH, self.editor.refillscrip)
        self.connectaction(ACTION_ADD, self.editor.addscrip)
        self.connectaction(ACTION_REMOVE, self.editor.delscrip)

if __name__ == "__main__":
    gui.runapp(ScripsWindow)
