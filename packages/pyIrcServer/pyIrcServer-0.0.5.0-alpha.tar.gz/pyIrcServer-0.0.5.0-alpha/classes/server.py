############################################################################
#    Copyright (C) 2004 by Lethalman                                       #
#    lethalman@fyrebird.net                                                #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

__doc__ = """
This module contains the Server object.
It will be a Common instance - Server(Common)
@author: Lethalman
@since: 28/11/2004
"""

import thread, sys
from CLASS import *

class Server(object):
    """
    The Server class.
    It's used to handle server which should be linked to the main server.
    @ivar s: The Server instance itself
    @type s: Server instance
    @ivar utils: Complex of utils of pyIS
    @type utils: Util instance
    @ivar sock: The client socket
    @type sock: Socket
    @ivar taddr: The original client address
    @type taddr: Tuple
    @ivar addr: The real address of the client
    @type addr: String
    @ivar server: Server informations set by the SERVER command
    @type server: Tuple
    @ivar connected: Is the client connected or not?
    @type connected: Boolean
    @ivar svrpass: Connection password set by the client
    @type svrpass: String
    @ivar signon: Signon time
    @type signon: Integer
    @ivar protoctl: Protocols set by the PROTOCTL command
    @type protoctl: List
    @ivar users: List of users registered by the server
    @type users: List
    @ivar commands: Dict of commands. Each command can be handled by many functions and they're set by protocols
    @type commands: Dict
    @ivar scommands: Dict of commands used internally.
    @type scommands: Dict
    @group Messages:  error error_closelink
    """

    def __new__(cls, c=None):
        """
        Return an instance of the same class which inherits the Common class
        """
        if not c: return object.__new__(cls)
        class Server(cls, c.s.common.__class__): pass
        return Server()
    
    def __init__(self, c=None):
        """
        Initialize a Server connection.
        @param c: The Connection instance
        """
        if not c: return
        global DEBUG, excDEBUG
        DEBUG, excDEBUG = c.s.common.DEBUG, c.s.common.excDEBUG
        self.s = c.s
        self.utils = self.s.common.utils
        self.generic = self.utils.generic
        self.sock = c.sock
        self.taddr = c.taddr
        self.addr = c.raddr
        self.server = c.server
        self.connected = True
        self.svrpass = c.svrpass
        self.signon = 0
        self.protoctl = c.protoctl
        self.users = []
        self.commands = {}
        self.scommands = {}

    def error(self, m):
        """
        Send an error message to the client
        @param m: Message to be sent
        """
        try: self.sock.sendall("ERROR :"+m+"\r\n")
        except: pass

    def error_closelink(self, m):
        """
        Call self.error with a standard closing link error message
        @param m: Message to be sent
        """
        self.error("Closing Link: ["+self.addr+"] (%s)" % m)

    def login(self):
        """
        Register the new server.
            1. Check the password
            2. Filter the address
            3. Check if it exists
            4. Check for duplicated server connection
        """
        try:
            server = None
            for s in self.s.common.config['link']:
                if self.server[0].lower() == s.attrs['name']:
                    server = s
                    break
            if not server:
                self.bye("Unknown server name", "Unknown server name (%s)" % self.server[0])
                return 0
            if str(server['password']):
                if not self.svrpass:
                    self.bye("Missing password", "Missing password")
                    return 0
                if server['password'].attrs['crypt'].lower() == 'yes': check = self.utils.crypt.digest(self.svrpass)
                else: check = self.svrpass
                if str(server['password']) != check:
                    self.bye("(Link denied (Authorization failed))", "Link denied (Authorization failed) [@%s.%d]" % (self.addr, self.taddr[1]))
                    return 0
            mod = getattr(__import__("protocols."+str(server['protocol'])), str(server['protocol']))
            mod.__init__(self)
            for c in self.s.clients: self.scommands['nick'](self, c)
            for c in self.s.channels:
                for u in c.users:
                    self.scommands['join'](self, u, c)
                    self.scommands['mode'](self, c, c.modes, '', c.modestime)
        except: excDEBUG("classes.server.login", sys.exc_info())
        return 1

    def start(self):
        """
        Start thread to read the socket
        """
        thread.start_new_thread(self.read, ())

    def __getitem__(self, cmd):
        """
        Return the requested server command based on its protocol
        """
        return self.scommands[cmd]
        
    def bye(self, bye="", err=""):
        """
        Close the connection
        @param bye: Set the message of the quit
        @param err: Write an extra error if required
        """
        if not self.connected: return
        self.connected = False
        if err: self.error(err)
        self.error_closelink(bye)
        try: self.sock.close()
        except: pass
        del(self.s[self])

    def send(self, msg):
        """
        Send a simple message
        @param msg: The message to be sent
        """
        try: self.sock.sendall(msg+"\r\n")
        except: self.bye()

    @sockread
    def read(self, rbuf):
        """
        Let's handle data readed from the socket
        @param rbuf: Raw buffer
        """
        print rbuf
        opts = self.utils.generic.getopt(rbuf, 3)
        if rbuf[0] != ":": mainopt = opts[0].lower()
        else: mainopt = opts[1].lower()
        if not mainopt in self.commands: return
        for f in self.commands[mainopt]:
            if not f(rbuf, self): break
