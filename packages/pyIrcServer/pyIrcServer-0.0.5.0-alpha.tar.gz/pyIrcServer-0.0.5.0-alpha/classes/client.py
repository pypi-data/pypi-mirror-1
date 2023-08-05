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

import thread, sys, time
from CLASS import *

__doc__ = """
Client class needed by pyIS used for client instance
@author: Lethalman
"""

class Client:
    """
    The Client class
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
    @ivar addr: The virtual address of the client
    @type addr: String
    @ivar user: User data set by the USER command
    @type user: Tuple
    @ivar logged: Is the client logged or not?
    @type logged: Boolean
    @ivar joined: List of joined channels
    @type joined: List
    @ivar connected: Is the client connected or not?
    @type connected: Boolean
    @ivar svrpass: Connection password set by the client
    @type svrpass: String
    @ivar signon: Signon time
    @type signon: Integer
    @ivar oper: The oper username used for the OPER command
    @type oper: String
    @ivar opname: The oper name to be shown on whois
    @type opname: String
    @ivar away: The away message
    @type away: String
    @group Messages:  error motd svrsend send sendto no nochan notice param
    """
    
    def __init__(self, c):
        """
        This function is called by a Connection instance to get a Client one
        @param c: The Connection instance
        """
        global DEBUG, excDEBUG
        DEBUG, excDEBUG = c.s.common.DEBUG, c.s.common.excDEBUG
        try:
            self.s = c.s
            self.utils = self.s.common.utils
            self.generic = self.utils.generic
            self.msg = self.utils.msg
            self.sock = c.sock
            self.taddr = c.taddr
            self.raddr = c.raddr
            self.addr = self.utils.vhost.makevhost(self.raddr, str(self.s.common.config['client']['virtualhost']))
            self.user = c.user
            self.nick = c.nick
            self.modes = ""
            self.logged = False
            self.joined = []
            self.connected = True
            self.svrpass = c.svrpass
            self.signon = 0
            self.oper = ""
            self.opname = ""
            self.away = ""
        except: excDEBUG("classes.client.__init__", sys.exc_info())

    def start(self):
        """
        1. Start reading data from socket
        2. Start the ping timeout feature (if wanted)
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

    def error(self, m):
        """
        Send an error message to the client
        @param m: Message to be sent
        """
        try: self.sock.sendall("ERROR :Closing Link: "+self.nick+"["+self.raddr+"] %s\r\n" % m)
        except: pass
                
    def banned(self):
        for mask, kline in self.s.kline.items():
            if self.utils.generic.ismask(mask, self.myself()):
                self.rnotice("*** You are permanently banned from %s (%s)" %
                        (self.s.common.config['server']['name'], kline['reason']))
                quit = "User is permanently banned (%s)" % kline['reason']
                self.bye(quit, quit)
                return 1
                
    def login(self):
        """
        The client can try login into IRC
        The function will
            - check the connection password (if set)
            - set some variables
            - log the login (if wanted)
            - notice operators of the new connection
            - say welcome to the client
            - perform standard actions
        """
        try:
            server = self.s.common.config['server']
            if 'password' in server.data:
                if str(server['password'].attrs['crypt']).lower() == "yes": check = self.utils.crypt.digest(self.svrpass)
                else: check = self.svrpass
                if str(server['password']) != check:
                    self.error("(Password mismatch)")
                    self.sock.close()
                    del(self.s[self])
                    self.connected = False
                    return 1
            if self.banned(): return
            self.logged = True
            self.signon = int(time.time())
            self.idle = int(time.time())
            if 'register' in self.s.common.config['log']['internals'].value:
                self.s.common.log.write(("Register", self.raddr+" logged into the server as \""+self.nick+"\""))
            self.s.notice('o', "Client connecting: "+self.nick+" ("+self.myrself2()+")")
            self.svrsend(self.utils.msg.RPL_WELCOME(self))
            self.s.sglobal('nick', self)
            for pcmd in self.s.common.config['client']['perform'].value:
                pcmd = pcmd.replace('%nick', self.nick)
                cmd = pcmd.split(' ', 1)[0]
                if cmd in self.s.common.commands:
                    for f in self.s.common.commands[cmd]:
                        if not f(pcmd, self): break
        except: excDEBUG("classes.client.login", sys.exc_info())
        return 1
                
    def motd(self):
        """
        Let's write the message of the day to the client
        """
        try:
            motdfile = open(str(self.s.common.config['server']['motd']), 'r')
            motd = motdfile.readlines()
            motdfile.close()
            self.svrsend(self.msg.RPL_MOTDSTART(self))
            for m in motd: self.svrsend(self.msg.RPL_MOTD(self, m.strip()))
            self.svrsend(self.msg.RPL_ENDOFMOTD(self))
        except:
            excDEBUG('classes.client.motd', sys.exc_info())
            self.svrsend(self.msg.ERR_NOMOTD(self))

    myself = lambda self: self.nick+"!"+self.user[0]+"@"+self.addr
    myrself = lambda self: self.nick+"!"+self.user[0]+"@"+self.raddr
    myrself2 = lambda self: self.user[0]+"@"+self.raddr
    rnotice = lambda self, s: self.svrsend("NOTICE "+self.nick+" :"+s)
    notice = lambda self, s: self.rnotice("*** Notice -- "+s)
    nochan = lambda self, o: self.svrsend(self.msg.ERR_NOSUCHCHANNEL(self, o))
    no = lambda self, o: self.svrsend(self.msg.ERR_NOSUCHNICK(self, o))
    param = lambda self, o: self.svrsend("461 "+self.nick+" "+o.upper()+" :Not enough parameters")
    
    def svrsend(self, msg):
        """
        Send a message from server
        @param msg: Message to be sent
        """
        try: self.sock.sendall(":%s %s\r\n" % (self.s.common.config['server']['name'], msg))
        except: self.bye()

    def send(self, msg):
        """
        Send a message from myself to myself
        @param msg: Message to be sent
        """
        try: self.sock.sendall(":"+self.myself()+" "+msg+"\r\n")
        except: self.bye()

    def sendto(self, u, msg):
        """
        Send a message from myself to the specified user
        @param u: The destination client
        @param msg: Message to be sent
        """
        try: u.sock.sendall(":"+self.myself()+" "+msg+"\r\n")
        except: self.bye()

    def mode(self, buf):
        """
        This is the user mode command
        @param buf: Contains the modes sent by the client
        """
        add = -1
        modes = ""
        canmodes = self.utils.generic.permit(
                self.s.common.config['client']['hierarchy'].attrs['value'],
                self.utils.generic.makecontext(
                        self.s.common.config['client']['hierarchy'], 'mode', 'modes'
                ), self.modes)
        for c in buf:
            if c == '+':
                if add == 0 or add == -1: changed = 1
                add = 1
                continue
            elif c == '-':
                if add == 1 or add == -1: changed = 1
                add = 0
                continue
            elif add == -1 and c != '+' and c != '-':
                changed = 1
                add = 1
            if c not in str(self.s.common.config['client']['hierarchy']['allmodes']):
                self.svrsend(self.msg.ERR_UMODEUNKNOWNFLAG(self))
                continue
            if c not in canmodes: continue
            if add and c not in self.modes:
                self.modes += c
                if changed:
                    modes += "+"+c
                    changed = 0
                else: modes += c
            elif not add and c in self.modes:
                self.modes = self.modes.replace(c, "")
                if changed:
                    modes += "-"+c
                    changed = 0
                else: modes += c
        if modes:
            self.send("MODE "+self.nick+" "+modes)

    def whowas(self):
        """
        Save the client in the whowas history for future calls
        """
        if not self.logged: return
        whowas = [self.user[0]+" "+self.addr+" * :"+self.user[3], str(self.s.common.config['server']['name'])+" :"+time.ctime()]
        if not self.nick in self.s.common.whowas:
            self.s.common.whowas[self.nick] = []			
        self.s.common.whowas[self.nick].insert(0, whowas)
            
    def bye(self, bye="Connection reset by peer.", err=""):
        """
        Disconnect the client
        @param bye: Set the message of the quit
        @param err: Message for the error command (used if not empty)
        """
        if not self.connected: return
        self.connected = False
        try: self.s.notice('o', "Client exiting: "+self.nick+" ("+self.myrself2()+") ["+bye+"]", self)
        except: pass
        try: 
            if err: self.error(err)
        except: pass
        try: self.sock.close()
        except: pass
        while self.joined:
            i = self.joined[0]
            del(i[self])
            for u in i.users:
                self.sendto(u, "QUIT :"+bye)
        self.s.sglobal('quit', self, bye)
        del(self.s[self])
        self.whowas()
            
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
            cancommands = self.utils.generic.permit(
                    self.s.common.config['client']['hierarchy'].attrs['value'],
                    self.utils.generic.makecontext(
                            self.s.common.config['client']['hierarchy'], 'mode', 'commands'
                    ), self.modes, 0)
            if amainopt not in cancommands:
                self.svrsend(self.msg.ERR_NOPERMFORHOST(self))
                return
            if amainopt in self.utils.generic.lowlist(self.s.common.config['client']['idle'].value): self.idle = int(time.time())
            for f in self.s.common.commands[amainopt]:
                if not f(rbuf, self): break
        except: excDEBUG("classes.client.read", sys.exc_info())
