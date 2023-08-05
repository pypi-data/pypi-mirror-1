#!/usr/bin/env python
"""
PXMLVIEW.PY
Simple Read-Only XML File Viewer using the PLIB Python Library
Copyright (C) 2008 by Peter A. Donis
"""

import sys
import os

from plib.xml import classes as xmlclasses
from plib.xml import io as xmlio
from plib.gui import main as gui
from plib.gui import classes
from plib.gui import edit
from plib.gui.defs import *

class XMLCData(object):
    
    def __init__(self, text):
        self.text = text
    
    def __len__(self):
        """ This ensures no further recursion ('leaf' node). """
        return 0
    
    def cdata(self):
        return None
    
    def _get_cols(self):
        return [self.text, "CDATA"]
    
    cols = property(_get_cols)

block_elements = ["p"]

class XMLColsTag(xmlclasses.BaseElement):
    
    def tagtype(self):
        if self.tag in block_elements:
            return "markup block"
        return "element"
    
    def _get_cols(self):
        return [" ".join([self.tag] + ["%s='%s'" % (key, self.get(key)) for key in self.keys()]),
            self.tagtype()]
    
    cols = property(_get_cols)
    
    def cdata(self):
        """ Wrap CDATA text up to look like a minimal leaf subnode. """
        if (self.text is not None) and (len(self.text) > 0):
            return XMLCData(str(self.text))
        return None

class XMLListViewItem(gui.PListViewItem):
    
    def __init__(self, parent, index, node, after=None):
        """ Put data in the form that PListViewItem expects to see. """
        if (len(node) == 0) and (node.cdata() is not None):
            childlist = [node.cdata()]
        elif not isinstance(node, XMLCData):
            childlist = node
        else:
            childlist = None
        data = (node.cols, childlist)
        gui.PListViewItem.__init__(self, parent, index, data, after)
        self.expand()

class XMLListView(gui.PListView, edit.PFileEditor):
    
    itemclass = XMLListViewItem
    typesuffix = "Viewer"
    
    def __init__(self, parent):
        self._loaded = False
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        else:
            filename = ""
        edit.PFileEditor.__init__(self, parent, filename)
        if not hasattr(self, '_xml'):
            sys.exit("You must select an XML file to view.")
        gui.PListView.__init__(self, parent,
            [classes.PLabel("XML"), classes.PLabel("Node Type", 150)], [self._xml.getroot()])
        self._loaded = True
    
    def _gettype(self):
        return "XML File"
    
    def _doload(self):
        if self._loaded:
            self.clear()
        self._xml = xmlio.parseFile(self.filename, elem=XMLColsTag)
        if self._loaded:
            self.append(self._xml.getroot())

PXMLViewerAboutData = {
    'name': "PXMLViewer",
    'version': "0.1",
    'copyright': "Copyright (C) 2008",
    'license': "GNU General Public License (GPL) Version 2",
    'description': "XML File Viewer", 
    'developers': ["Peter Donis"],
    'website': "http://www.peterdonis.net",
    'icon': os.path.join(os.path.split(os.path.realpath(__file__))[0], "pxmlview.png") }

class PXMLViewer(gui.PMainWindow):
    
    aboutdata = PXMLViewerAboutData
    actionflags = [ACTION_FILEOPEN, ACTION_ABOUT, ACTION_EXIT]
    clientwidgetclass = editorclass = XMLListView
    maximized = True
    queryonexit = False

if __name__ == "__main__":
    gui.runapp(PXMLViewer)
