#!/usr/bin/env python
"""
SCRIPS-EDIT.PY
Copyright (C) 2008-2010 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Editor for scrips.dat file used to keep track of
prescription refills.
"""

import sys
import os
import datetime

from plib import __version__
from plib.utils import version

from plib.gui import main as gui

# Monkeypatch common menu and toolbar items

from plib.gui import defs

defs.ACTION_SUBMIT = 543
defs.ACTION_REFILL = 544

from plib.gui import common

common.ACTIONS_ACTION.insert(0, defs.ACTION_SUBMIT)
common.ACTIONS_ACTION.insert(1, defs.ACTION_REFILL)

common.actiondict[defs.ACTION_SUBMIT] = [common.actiondict[defs.ACTION_OK][0], "&Submit"]
common.actiondict[defs.ACTION_REFILL] = [common.actiondict[defs.ACTION_REFRESH][0], "&Refill"]

common.actionkeylist = sorted(common.actiondict.keys())

import scrips

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
    
    def __init__(self, text, chars, width=-1, align=defs.ALIGN_LEFT, readonly=False):
        gui.PHeaderLabel.__init__(self, text, width, align, readonly)
        self.chars = chars
    
    def outputlabel(self, index):
        result = self.text
        if index == 0:
            result = "".join(["#", result])
        return result.ljust(self.chars)

headings = [
    ScripLabel("Drug", 16, 150),
    ScripLabel("Rx", 12, 100),
    ScripLabel("Last Filled", 16, 100, defs.ALIGN_CENTER),
    ScripLabel("Days", 8, 100, defs.ALIGN_CENTER),
    ScripLabel("Refills Left", 16, 100, defs.ALIGN_CENTER),
    ScripLabel("Submitted", 0, 100) ]

class ScripList(gui.PTableEditor, gui.PTable):
    
    def __init__(self, parent):
        gui.PTable.__init__(self, parent, headings)
        if sys.platform == 'darwin':
            fontsize = 16
        else:
            fontsize = 12
        self.set_font("Arial", fontsize)
        self.set_header_font("Arial", fontsize, bold=True)
        gui.PTableEditor.__init__(self, data=scrips.scriplist())
        for row in range(len(self)):
            self.setcolors(row)
        self.editable = True
    
    # FIXME: Figure out a way to have the editor classes automatically detect this
    if hasattr(gui.PTable, 'edit'):
        
        def edit(self, *args):
            # Distinguish between edit method of PTableEditor and edit method of PTable
            if len(args) > 0:
                return gui.PTable.edit(self, *args)
            return gui.PTableEditor.edit(self)
    
    def setcolors(self, row=None):
        if row is None:
            row = self.current_row()
        scrip = self.data[row]
        if scrip.due():
            if scrip.submitted:
                self.set_row_fgcolor(row, self.default_fgcolor())
            else:
                self.set_row_fgcolor(row, defs.COLOR_RED)
            self.set_row_bkcolor(row, defs.COLOR_YELLOW)
        else:
            self.set_row_fgcolor(row, self.default_fgcolor())
            self.set_row_bkcolor(row, self.default_bkcolor())
    
    def _on_tablechanged(self, row, col):
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
    
    def set_min_size(self, width, height, from_code=False):
        gui.PTable.set_min_size(self, width, height)
        if from_code: # and sys.platform != 'darwin':
            # FIXME: figure out why wx on OSX throws 'Bus error' on this -- it
            # appears to be in the GetSizeTuple call
            self._parent.sizetoclient(width, height)
    
    def addscrip(self):
        self.append(scrips.scripclass())
        self.set_min_size(self.minwidth(), self.minheight(), True)
        self.modified = True
    
    def delscrip(self):
        msg = "Do you really want to delete %s?" % self.data[self.current_row()].name
        if self._parent.messagebox.query2("Delete Prescription", msg) == defs.answerOK:
            del self[self.current_row()]
            self.set_min_size(self.minwidth(), self.minheight(), True)
            self.modified = True
    
    def headerline(self):
        return "".join([heading.outputlabel(index) for index, heading in enumerate(headings)])
    
    def outputlines(self):
        return os.linesep.join([self.headerline()] + [scrip.outputline() for scrip in self.data])

ScripsIniLabels = {
    "email": "E-Mail Fields",
    "email_fromaddr": "From",
    "email_toaddr": "To",
    "email_typestr": "MIME Type",
    "email_charsetstr": "Character Set",
    "email_serverstr": "Server Hostname",
    "email_portnum": "Server Port",
    "email_username": "User Name",
    "email_password": "Password",
    "headers": "E-Mail Headers",
    "headers_dict": "Python Dictionary",
    "pharmacy": "Pharmacy",
    "pharmacy_name": "Name" }

ScripsAboutData = {
    'name': "ScripsEdit",
    'version': version.version_string(__version__),
    'copyright': "Copyright (C) 2008",
    'license': "GNU General Public License (GPL) Version 2",
    'description': "Prescription Editor", 
    'developers': ["Peter Donis"],
    'website': "http://www.peterdonis.net",
    'icon': os.path.join(os.path.split(os.path.realpath(__file__))[0], "scrips.png") }

class ScripsWindow(gui.PMainWindow):
    
    aboutdata = ScripsAboutData
    actionflags = [
        defs.ACTION_FILESAVE,
        defs.ACTION_SUBMIT, defs.ACTION_REFILL, defs.ACTION_ADD, defs.ACTION_REMOVE,
        defs.ACTION_PREFS, defs.ACTION_ABOUT, defs.ACTION_ABOUTTOOLKIT, defs.ACTION_EXIT ]
    defaultcaption = "Prescription List Editor"
    clientwidgetclass = ScripList
    editorclass = ScripList
    placement = (defs.SIZE_CLIENTWRAP, defs.MOVE_CENTER)
    large_icons = True
    show_labels = True
    
    def __init__(self, app):
        gui.PMainWindow.__init__(self, app)
        
        self.statusbar.set_text("Editing prescription info.")
        
        self.prefsdialog = gui.PPrefsDialog(self, scrips.inifile, ScripsIniLabels,
            defs.SECTION_GROUPBOX)
        
        self.connectaction(defs.ACTION_FILESAVE, self.editor.save) # not built into PEditor
        self.connectaction(defs.ACTION_SUBMIT, self.editor.submitscrip)
        self.connectaction(defs.ACTION_REFILL, self.editor.refillscrip)
        self.connectaction(defs.ACTION_ADD, self.editor.addscrip)
        self.connectaction(defs.ACTION_REMOVE, self.editor.delscrip)

if __name__ == "__main__":
    gui.runapp(ScripsWindow)
