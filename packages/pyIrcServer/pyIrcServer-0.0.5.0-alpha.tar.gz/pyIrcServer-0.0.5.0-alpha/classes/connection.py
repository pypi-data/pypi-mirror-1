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
#    Free Software Foundation, Inc.,                 #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

__doc__ = """
This module contains the Connection class.
@author: Lethalman
@since: 28/11/2004
"""

import thread, sys, time
from CLASS import *

class Connection:
    """
    The Connection class.
    It's used by the MainServer class to handle a new connection.
    @ivar s: The Server instance itself
    @type s: Server instance
    @ivar utils: Complex of utils of pyIS
    @type utils: Util instance
    @ivar msg: It contains standard messages for the IRC protocol
    @type msg: pyIS Util
    @ivar sock: The client socket
    @type sock: Socket
    @ivar taddr: The original client address
    @type taddr: Tuple
    @ivar raddr: The client ip
    @type raddr: String
    @ivar user: User data set by the USER command
    @type user: Tuple
    @ivar logged: Is the client logged or not?
    @type logged: Boolean
    @ivar connected: Is the client connected or not?
    @type connected: Boolean
    @ivar svrpass: Connection password set by the client
    @type svrpass: String
    @ivar protoctl: Protocols set by the PROTOCTL command
    @type protoctl: List
    """

    def __init__(self, s, sock, taddr):
        """
        This function is called by the MainServer instance to handle a new Connection
        @param s: the MainServer instance itself
        @param sock: the socket
        @param taddr: the address of the incoming connection
        @group Messages: error error_closelink
        """
        global DEBUG, excDEBUG
        DEBUG, excDEBUG = s.common.DEBUG, s.common.excDEBUG
        self.s = s
        self.utils = self.s.common.utils
        self.generic = self.utils.generic
        self.msg = self.utils.msg
        self.sock = sock
        self.taddr = taddr
        self.raddr = taddr[0]
        self.user = ()
        self.server = ()
        self.nick = ""
        self.logged = False
        self.connected = True
        self.svrpass = ""
        self.protoctl = []
        if 'connect' in self.s.common.config['log']['internals'].value:
            self.s.common.log.write(("Connect", self.raddr+" connected to the server"))

    def start(self):
        """
        Start reading data from socket.
        Log the connection as Client or Server.
        """
        thread.start_new_thread(self.read, ())
        if float(self.s.common.config['client']['timeout']): thread.start_new_thread(self.ping, ())

    def ping(self):
        """
        Ping the client.
        Everytime the sleep ends, it can perform three kinds of operation:
            1. If i didn't ping the client, ping it and remember i've done it
            2. If the client didn't pong, disconnect it for "Ping timeout"
            2. If the client did pong, reset the ping status then restart sleeping
        """
        self.pong = 1
        while(self.connected):
            time.sleep(self.s.common.config['client']['timeout'])
            if not self.connected: return
            if self.pong:
                try: self.sock.sendall("PING :%s\r\n" % self.s.common.config['server']['name'])
                finally: self.pong = 0
            else:
                self.bye("Ping timeout", "(Ping timeout)")

    def svrsend(self, msg):
        """
        Send a message from server
        @param msg: Message to be sent
        """
        try: self.sock.sendall(":%s %s\r\n" % (self.s.common.config['server']['name'], msg))
        except: self.bye()
        
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
        self.error("Closing Link: "+self.nick+"["+self.raddr+"] (%s)" % m)
        
    def bye(self, bye="", extra=""):
        """
        Close the connection
        @param bye: Set the message of the quit
        """
        if not self.connected: return
        self.connected = False
        self.error_closelink(bye)
        try: self.sock.close()
        except: pass

    def login(self, cl):
        """
        Check if the connection has been enstablished with a Client or a Server.
        After call the real login and start reading from socket.
        @param cl: Client or Server
        """
        try:
            self.connected = False
            client = cl(self)
            if cl == self.s.common.Client: self.s.clients.append(client)
            elif cl == self.s.common.Server: self.s.servers.append(client)
            if client.login(): client.start()
        except: excDEBUG("classes.connection.login", sys.exc_info())
        
    param = lambda self, o: self.svrsend("461 "+self.nick+" "+o.upper()+" :Not enough parameters")
    
    @sockread
    def read(self, rbuf):
        """
        Let's handle data readed from the socket
        @param rbuf: Raw buffer
        """
        try:
            amainopt = mainopt = rbuf.split(' ')[0].lower()
            for i in self.s.common.config['alias']:
                if mainopt in i.value:
                    amainopt = i.attrs['cmd']
                    rbuf = amainopt+rbuf[len(mainopt):]
                    amainopt = amainopt.split(' ')[0].lower()
                    break
            if not amainopt in self.s.common.commands:
                self.svrsend(self.msg.ERR_UNKNOWNCOMMAND(self, mainopt))
                return
            if amainopt in self.s.common.config['log']['commands'].value:
                self.s.common.log.write(("Command: "+mainopt, self.nick+"("+self.raddr+") sent: "+rbuf))
            for f in self.s.common.commands[amainopt]:
                if not f(rbuf, self): break
        except: excDEBUG("classes.connection.read", sys.exc_info())
