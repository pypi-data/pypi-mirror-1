#!/usr/bin/env python
"""
PYIDSERVER.PY
Copyright (C) 2008 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Python implementation of IDServer, a
command-line tool to query an internet
server and return information about it.
"""

import sys
import socket

from plib.stdlib import coll, options, AsyncServer

def do_output(fileobj, s):
    fileobj.write(s)
    fileobj.flush()

run_callback = None # used by pyidserver-gui

class IDServerClient(AsyncServer.ClientCommunicator):
    """
    Communicates with server and writes results to fileobj.
    """
    
    def __init__(self, addr, fileobj, proto_items):
        self.connect_addr = addr
        self.fileobj = fileobj
        self.data_queue = coll.fifo(proto_items)
        self.replied = False
        self.chat_complete = False
        AsyncServer.ClientCommunicator.__init__(self)
    
    def run_client(self):
        self.do_connect(self.connect_addr)
        self.start(self.data_queue.next())
        self.do_loop(run_callback)
    
    def handle_connect(self):
        do_output(self.fileobj, "Connected ...\n")
    
    def process_data(self):
        if not self.replied:
            self.replied = True
            do_output(self.fileobj, "Server returned the following:\n")
        do_output(self.fileobj, self.read_data)
        if self.data_queue:
            self.start(self.data_queue.next())
        else:
            self.chat_complete = True
    
    def query_done(self):
        return self.chat_complete
    
    def handle_close(self):
        do_output(self.fileobj, "Connection closed.\n")

PROTO_DEFAULT = 'http'

quitmsgs = [None, "QUIT\r\n"]

protocols = {
    'ftp': (21, [None]),
    'http': (80, ["HEAD / HTTP/1.0\r\n\r\n"]),
    'imap': (143, [None, "A1 CAPABILITY\r\n", "A2 LOGOUT\r\n"]),
    'news': (119, quitmsgs),
    'pop': (110, quitmsgs),
    'smtp': (25, quitmsgs) }

def run_idserver(fileobj, arg, dns_only, protocol, portnum):
    """
    Query server and write results to fileobj.
    
    Server argument 'arg' should be a URL string, either an IP address
    or a host name. The URL may include a protocol specifier at the
    start (e.g., http://), and may include a port specifier at the
    end (e.g., :80). A trailing slash, '/', in the URL, and anything
    after it, are treated as a path specifier and ignored.
    
    If dns_only is true, only a DNS lookup is done; no connection is
    actually made to the server.
    
    The protocol should be one of the strings listed as keys in the
    protocols dictionary above.
    
    The port number should be an integer giving the port number on
    the server. (This parameter should only need to be used very
    rarely; almost always the port number is determined by the
    protocol as shown in the dictionary above.)
    
    The output file object 'fileobj' can be any file-like object
    that has a write and a flush method. See pyidserver-gui.py for
    an example of a file-like object that writes to a text control.
    """
    
    if '://' in arg:
        addrtype, arg = arg.split('://')
        if (addrtype in protocols):
            if protocol:
                do_output(fileobj,
                    "URL includes protocol %s, ignoring specified protocol %s.\n"
                    % (addrtype, protocol))
            protocol = addrtype
        elif addrtype:
            do_output(fileobj, "URL includes incorrect protocol %s, ignoring.\n"
                % addrtype)
    if '/' in arg:
        arg, path = arg.split('/')
        if path:
            do_output(fileobj, "URL includes path after host name/address, ignoring.\n")
    if ':' in arg:
        arg, portstr = arg.split(':')
        try:
            p = int(portstr)
            if p != portnum:
                if portnum != 0:
                    do_output(fileobj, "URL includes port %d, ignoring specified port %d.\n"
                        % (p, portnum))
                portnum = p
        except ValueError:
            do_output(fileobj, "URL includes invalid port %s, ignoring.\n" % portstr)
    
    if dns_only:
        do_output(fileobj, "Doing DNS lookup on %s ...\n" % arg)
    else:
        proto_msg = port_msg = ""
        if protocol == "":
            protocol = PROTO_DEFAULT
        else:
            protocol = protocol.lower()
            proto_msg = " using %s" % protocol
        if protocol in protocols:
            proto_port, proto_items = protocols[protocol]
            if portnum == 0:
                portnum = proto_port
            else:
                port_msg = " on port %i" % portnum
        else:
            raise ValueError, "Invalid protocol: %s.\n" % protocol
    
    ipaddr = socket.gethostbyname(arg)
    if ipaddr == arg:
        # URL was an IP address, reverse lookup
        url = socket.gethostbyaddr(ipaddr)[0]
        do_output(fileobj, "Domain name for %s is %s.\n" % (ipaddr, url))
    else:
        # URL was a domain name, normal lookup
        url = arg
        do_output(fileobj, "IP address for %s is %s.\n" % (url, ipaddr))
    
    if not dns_only:
        do_output(fileobj, "Contacting %s%s%s ...\n" % (arg, proto_msg, port_msg))
        IDServerClient((url, portnum), fileobj, proto_items).run_client()

def run_main(outfile, arg, errfile=None, dns_only=False, protocol="", portnum=0):
    if errfile is None:
        errfile = outfile
    try:
        run_idserver(outfile, arg, dns_only, protocol, portnum)
    except ValueError:
        errfile.write(str(sys.exc_info()[1]))
    except (socket.error, socket.herror, socket.gaierror, socket.timeout):
        exc_type, exc_value, _ = sys.exc_info()
        errfile.write("%s %s\n" % tuple(map(str, (exc_type, exc_value))))

if __name__ == '__main__':
    _, def_dns, def_proto, def_port = run_main.func_defaults
    optlist = (
        ("-l", "--lookup", { 'action': "store_true",
            'dest': "dns_only", 'default': def_dns,
            'help': "Only do DNS lookup, no server query" } ),
        ("-p", "--protocol", { 'action': "store", 'type': "string",
            'dest': "protocol", 'default': def_proto,
            'help': "Use the specified protocol to contact the server" } ),
        ("-r", "--port", { 'action': "store", 'type': "int",
            'dest': "portnum", 'default': def_port,
            'help': "Use the specified port number to contact the server" } )
        )
    arglist = ["URL"]
    
    opts, args = options.parse_options(optlist, arglist)
    run_main(sys.stdout, args[0], sys.stderr, opts.dns_only, opts.protocol, opts.portnum)
