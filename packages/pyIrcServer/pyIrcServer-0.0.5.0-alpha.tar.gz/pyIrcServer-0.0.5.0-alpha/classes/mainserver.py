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

import socket, sys, os, thread, signal, time, select

__doc__ = """
This module contains the MainServer class.
It's the main class of the server.
@author: Lethalman
"""

class MainServer:
    """
    The MainServer class
    @ivar clients: List of connected clients
    @type clients: List
    @ivar channels: List of created channels
    @type channels: List
    @ivar servers: List of linked servers (still unused)
    @type servers: List
    @ivar services: List of connected services (still unusued)
    @type services: List
    @ivar sclients: List of server clients
    @type sclients: List
    @ivar rehashed: Has the server been rehashed?
    @type rehashed: Boolean
    @ivar startup: The startup time
    @type startup: String
    @ivar common: The saved common variable on init
    @type common: Common instance
    @ivar sockets: Server sockets
    @type sockets: Dict {fileno: socket}
    @ivar poll: Polling object of sockets
    @type poll: Polling object
    @ivar db: Database instance if requested
    @type db: Database instance
    @ivar kline: Kline database
    @type kline: Dict
    """
    
    def __init__(self, common):
        """
        Start the server and perform the following actions:
            1. Install signals
            2. Create the server socket
            3. Write the PID in the pid file
            4. Save the startup time
        @param common: The Common instance
        """
        global DEBUG, excDEBUG
        DEBUG, excDEBUG = common.DEBUG, common.excDEBUG
        self.common = common
        self.clients = []
        self.channels = []
        self.servers = []
        self.services = []
        self.sclients = []
        self.sockets = {}
        self.kline = {}
        self.poll = select.poll()
        try:
            if self.common.system != 'Windows':
                signal.signal(signal.SIGHUP, self.rehash)
                signal.signal(signal.SIGTERM, self.stop)
            for listen in self.common.config['server']['listen']:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((str(listen), listen.attrs['port']))
                sock.listen(self.common.config['server']['maxconnections'])
                self.sockets[sock.fileno()] = sock
                self.poll.register(sock)
            pid = file("pyis.pid", "w")
            pid.write(str(os.getpid()))
            pid.close()
            self.rehashed = False
        except:
            print sys.exc_value
            sys.exit()
        self.startup = time.ctime()
        sys.path.insert(0, '')
    
    def read(self):    
        """
        Wait for new connections then create a new Connection
        """
        if 'database' in self.common.config.data:
            self.db = self.common.Database(self)
            self.db.connect()
        else: self.db = None
        while(1):
            try:
                poll = self.poll.poll()
                for sock in poll:
                    if not sock[1] & select.POLLIN:
                        DEBUG("classes.mainserver.read", "Lost socket (fileno: %d)" % sock[0])
                        del self.sockets[sock[0]]
                        self.poll.unregister(sock[0])
                    else:
                        cs, ca = self.sockets[sock[0]].accept()
                        self.common.Connection(self, cs, ca).start()
            except:
                excDEBUG("classes.mainserver.read", sys.exc_info())
                try:
                    if self.rehashed:
                        self.rehashed = False
                        continue
                    sys.exit()
                except: sys.exit()

    def rehash(self, n=0, p=0):
        """
        Rehash the configuration file.
        It can be called remotely or by a SIGHUP signal
        """
        self.rehashed = True
        self.common.config = self.common.getConfig()
        
    def stop(self, n=0, p=0):
        """
        Stop the server.
        It's usually called from a SIGTERM signal
        """
        for sock in self.sockets.values(): sock.close()
        sys.exit()
        
    def notice(self, m, msg, exc=None):
        """
        Send a notice to every client which got a given mode
        @param m: User modes
        @param msg: Message to be sent
        """
        for c in self.clients:
            if c == exc: continue
            for mode in m:
                if m in c.modes: c.notice(msg)
            
    def sglobal(self, cmd, *args):
        """
        Call a command for each linked server
        @param cmd: Command name
        """
        for s in self.servers: s[cmd](s, *args)        
    
    def __delitem__(self, item):
        """
        Remove a Client, a Channel, a Server or a SClient
        @param item: Item to be removed
        """
        if isinstance(item, self.common.Client): d = self.clients
        elif isinstance(item, self.common.Channel): d = self.channels
        elif isinstance(item, self.common.Server):
            d = self.servers
            for sc in item.users:
                del(self.sclients[self.sclients.index(sc)])
        elif isinstance(item, self.common.SClient): d = self.sclients
        else: return
        try: del(d[d.index(item)])
        except: excDEBUG("classes.mainserver.__delitem__", sys.exc_info())
