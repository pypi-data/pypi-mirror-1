#!/usr/bin/env python
"""
SETUPUTILS.PY
Post-install script utilities
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains common utility routines for the
PLIB post-install scripts.
"""

import sys
import os
import compiler

def write_setup_file(modname, module_vars, outpath, outfilename, descr):
    
    fullpath = os.path.join(outpath, outfilename)
    thismod = sys.modules[modname]
    vars = [(varname, getattr(thismod, varname)) for varname in module_vars]
    for varname, value in vars:
        print "%s: %s" % (varname, value)
    
    print "Writing module %s..." % fullpath
    
    lines = [
        "#!/usr/bin/env python",
        "# %s -- PLIB.%s Setup Module" % (outfilename.upper(), descr),
        "# *** This module is automatically generated; do not edit. ***",
        "" ]
    
    lines.extend(('%s = "%s"' % (varname, value) for varname, value in vars))
    
    outfile = open(fullpath, 'w')
    outfile.writelines(line + os.linesep for line in lines)
    outfile.close()
    
    print "Byte-compiling %s..." % fullpath
    compiler.compileFile(fullpath)
