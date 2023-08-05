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

from PROTOCOL import *

__doc__ = """
pyIrcServer Protocol
@author: Lethalman
@see: RFC 2813
@since: 02/12/2004
"""

__functions__ = []

def __init__(server):
    global __functions__
    __functions__ = [c_nick, c_notice, c_mode, c_topic,
    s_nick, s_quit, s_privmsg, s_join, s_mode, s_topic]
    for f in __functions__:
        if f.func_name[0] == 's':
            server.scommands[f.func_name[2:]] = f
        else:
            server.addcommand(f.func_name[2:], f)
    server.sock.sendall("""PASS: %s\r\nSERVER %s %d :%s %s\r\n""" %
                          (server.svrpass, server.s.common.config['server']['name'], 1, server.s.common.info.strictver, server.s.common.config['server']['netname']))

# Server commands, from remote to local
# (Auto called when reading the socket)
                          
@Args()
def c_nick(rbuf, server, args):
    """
    Let me know remote linked server users.
        - NICKv2 protocol
    @param rbuf: NICK <nickname> <hopcount> <username> <host> <servertoken> <umode> <realname>
    """
    @Args(10)
    def __nickv2(rbuf, server, args):
        """
        NICKv2 should be used only when a new user was registered
        """
        sclient = server.s.common.SClient()
        sclient.__dict__ = dict(zip(('nick', 'hops', 'time', 'user', 'raddr', 'server', 'servtime', 'modes', 'addr', 'info'), args[1:]))
        sclient.s = server
        if sclient.addr == '*': sclient.addr = sclient.raddr
        server.s.sclients.append(sclient)
        server.users.append(sclient)
        return 1
    if 'nickv2' in server.protoctl: return __nickv2(rbuf, server)

@Args(2)
def c_notice(rbuf, server, args, cfrom):
    """
    Receive a notice and route it to the specified user
    @param rbuf: NOTICE <msgtarget> <text>
    """
    nick = server.utils.generic.nick_exist(server.s.clients, args[1])
    snick = server.utils.generic.nick_exist(server.s.sclients, cfrom)
    if not nick or not snick: return 1
    snick.sendto(nick, rbuf)
    return 1
    
@Args(2)
def c_mode(rbuf, server, args, cfrom):
    """
    Change modes for a channel
    @param rbuf: MODE <channel> *( ( "-" / "+" ) *<modes> *<modeparams> )
    """
    nick = server.utils.generic.nick_exist(server.s.sclients, cfrom)
    if not nick: return 1
    chan = server.utils.generic.chan_exist(server.s.channels, args[1])
    if not chan: return 1
    chan.mode(args[2], nick)
    return 1
    
@Args(4)
def c_topic(rbuf, server, args, cfrom):
    """
    Change topic for a channel by a given nickname
    @param rbuf: TOPIC <channel> <nickname> 0 <topic>
    """
    chan = server.utils.generic.chan_exist(server.s.channels, args[1])
    if not chan: return 1
    nick = server.utils.generic.nick_exist(server.s.sclients, cfrom)
    if not nick: return 1
    chan.topic(nick, args[4])
    return 1
    
# Server commands, from local to remote
# (Manually called internally to send a message)
    
def s_nick(server, client):
    """
    Send a NICK message to the server
    @param server: Remote Server
    @param client: Local Client
    """
    if 'nickv2' in server.protoctl:
        server.send("NICK %s 1 %d %s %s %s 0 +%s %s :%s" % (client.nick, client.signon, client.user[0], client.raddr,
                    client.s.common.config['server']['name'], client.modes, client.addr, client.user[3]))
                
def s_quit(server, client, bye):
    """
    Notify the QUIT of the client
    @param client: Client which exits
    @param bye: Quit message
    """
    server.send(":"+client.nick+" QUIT :"+bye)

def s_privmsg(sender, to, msg):
    """
    Send a PRIVMSG to a server client
    @param sender: Sender which the message come from
    @param to: The message destination
    @param msg: Message
    """
    to.send(sender.nick, "PRIVMSG "+to.nick+" :"+msg)

def s_join(server, user, chan):
    """
    The user joins a channel
    @param user: User who joined the channel
    @param chan: The Channel joined by the user
    """
    server.send(":"+user.nick+" JOIN "+chan.name)
    
def s_mode(server, chan, modes, args, modestime, sfrom=""):
    """
    Change the user modes on the channel. If no source is specified,
    use the local server name
    @param chan: Channel
    @param modes: New modes for the channel
    @param args: Arguments for modes
    @param modestime: Timestamp of this event
    @param sfrom: Source which called MODE command
    """
    if not sfrom: sfrom = str(server.s.common.config['server']['name'])
    server.send(":%s MODE %s %s %s %s"
        % (sfrom, chan.name, modes, args, modestime))

def s_topic(server, user, chan):
    """
    Notify that the topic changed
    @param user: User who changed the topic
    @param chan: The Channel
    """
    server.send(":%s TOPIC %s %s 0 :%s" % (user.nick, chan.name, chan.topicby, chan.topicset))
