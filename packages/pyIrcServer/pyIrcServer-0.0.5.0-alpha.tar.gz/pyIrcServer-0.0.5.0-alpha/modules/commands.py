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

import sys, re, time
from MODULE import *

__doc__ = """
Generic IRC commands' parser
@author: Lethalman
@see: RFC 2812
@note: Many functions are still incomplete for one of the following reasons:
    - Link to servers still unimplemented
    - Bad documentation about the command
"""

__functions__ = []

def __init__(common):
    global __functions__, DEBUG, excDEBUG
    DEBUG, excDEBUG = common.DEBUG, common.excDEBUG
    __functions__ = [c_quit, c_user, c_nick, c_join, c_part, c_pong, c_kick,
            c_mode, c_names, c_invite, c_topic, c_who, c_motd, c_ison,
            c_ping, c_list, c_pass, c_whois, c_away, c_whowas, c_lusers,
            c_admin, c_version, c_time, c_info, c_userhost, c_server, c_protoctl]
    add = common.addcommand
    for f in __functions__:
        add(f.func_name[2:], f)
    __functions__.append(c_msg)
    add("privmsg", c_msg)
    add("notice", c_msg)
    
@Args(1, 0)
def c_quit(rbuf, client, args):
    """
    A client session is terminated with a quit message.  The server
    acknowledges this by sending an ERROR message to the client.
    @param rbuf: QUIT [ <Quit Message> ]
    """
    try: bye = "Quit: "+args[1]
    except: bye = ""
    client.bye(bye, '('+bye+')')
    return 1

@Args(4)
@NoLogged
def c_user(rbuf, client, args):
    """
    The USER command is used at the beginning of connection to specify
    the username, hostname and realname of a new user
    @param rbuf: USER <user> <mode> <unused> <realname>
    """
    client.user = args[1], args[2], args[3], args[4]
    if client.nick: client.login(client.s.common.Client)
    return 1

@Args(1,0)
def c_nick(rbuf, client, args):
    """
    NICK command is used to give user a nickname or change the existing one
    @param rbuf: NICK <nickname>
    """
    try:
        if len(args) < 2:
            client.svrsend(client.msg.ERR_NONICKNAMEGIVEN(client))
            return 1
        args[1] = args[1][:int(client.s.common.config['client']['maxlength'])]
        for r in client.s.common.config['client']['badformats'].value:
            if re.match(r, args[1]):
                client.svrsend(client.msg.ERR_ERRONEOUSNICKNAME(client, args[1]))
                return 1
        if client.nick == args[1]: return 1
        if client.utils.generic.nick_exist(client.s.clients, args[1]):
            client.svrsend(client.msg.ERR_NICKNAMEINUSE(client, args[1]))
        else:
            if client.logged:
                client.send("NICK "+args[1])
                for c in client.joined:
                    for u in c.users:
                        if u == client: continue
                        client.sendto(u, "NICK "+args[1])
                client.whowas()
            client.nick = args[1]
            if client.user and not client.logged: client.login(client.s.common.Client)
    except: excDEBUG("modules.commands.c_nick", sys.exc_info())
    return 1

@Args(2,1)
@Logged
def c_join(rbuf, client, args):
    """
    The JOIN command is used by a user to request to start listening to
    the specific channel.
    Note that this message accepts a special argument ("0"), which is
    a special request to leave all channels the user is currently a member of
    @param rbuf: JOIN ( <channel> *( "," <channel> ) [ <key> *( "," <key> ) ] ) / "0"
    """
    if len(args) > 2: key = args[2]
    else: key = ""
    chans = filter(lambda x: len(x)>0, args[1].split(','))
    keys = filter(lambda x: len(x)>0, key.split(','))
    for cc in range(len(chans)):
        curchan = chans[cc]
        try: curkey = keys[cc]
        except: curkey = ""
        curchan = curchan[:int(client.s.common.config['channel']['maxlength'])+1]
        if curchan == '0':
            l = len(client.joined)
            for j in range(l):
                c_part("PART "+client.joined[0].name+" :Left all channels", client)
            continue
        if curchan[0] != "#":
            client.nochan(curchan)
            return 1
        chan = client.utils.generic.chan_exist(client.s.channels, curchan)
        if chan:
            r = chan.join(client, curkey)
            if r: 
                chan.viewtopic(client)
                chan.names(client)
        else:
            for r in client.s.common.config['channel']['badformats'].value:
                if re.match(r, curchan):
                    client.svrsend(client.msg.ERR_ERRONEOUSCHANNELNAME(client, curchan))
                    return 1
            chan = client.s.common.Channel(client.s, curchan)
            if chan.join(client, curkey):
                client.s.channels.append(chan)
                chan.names(client)
                chan.perform(client, client.s.common.config['channel']['perform'].value)
    return 1

@Args(2,1)
@Logged
def c_part(rbuf, client, args):
    """
    The PART command causes the user sending the message to be removed
    from the list of active members for all given channels listed in the
    parameter string
    @param rbuf: PART <channel> *( "," <channel> ) [ <Part Message> ]
    """
    chans = filter(lambda x: len(x)>0, args[1].split(','))
    for cc in chans:
        chan = client.utils.generic.chan_exist(client.s.channels, cc)
        if not chan:
            client.nochan(cc)
            continue
        if not client.utils.generic.nick_exist(chan.users, client.nick):
            client.svrsend(client.msg.ERR_NOTONCHANNEL(client, chan))
            continue
        try: opt = " :"+args[2]
        except: opt = ""
        for u in chan.users: client.sendto(u, "PART "+cc+opt)
        del(chan[client])
    return 1
    
@Args(2, 0)
@Logged
def c_msg(rbuf, client, args):
    """
    This function handles PRIVMSG and NOTICE commands
    @param rbuf: The buffer depends on the type of the command
        - PRIVMSG is used to send private messages between users, as well as to
        send messages to channels.  <msgtarget> is usually the nickname of
        the recipient of the message, or a channel name
            - PRIVMSG <msgtarget> <text to be sent>
        - The NOTICE command is used similarly to PRIVMSG.  The difference
        between NOTICE and PRIVMSG is that automatic replies MUST NEVER be
        sent in response to a NOTICE message
            - NOTICE <msgtarget> <text>
    """
    args[0] = args[0].upper()
    try: args[1]
    except:
        client.svrsend(client.msg.ERR_NORECIPIENT(client, args[0].upper()))
        return 1
    try: args[2]
    except:
        client.svrsend(client.msg.ERR_NOTEXTTOSEND(client))
        return 1
    if args[1][0] == "#":
        chan = client.utils.generic.chan_exist(client.s.channels, args[1])
        if not chan:
            client.no(args[1])
            return 1
        if client.utils.generic.isbanned(client, chan):
            client.svrsend(client.msg.ERR_CANNOTSENDTOCHAN(client, chan, 'b'))
            return 1
        if 'n' in chan.modes and client not in chan.users:
            client.svrsend(client.msg.ERR_CANNOTSENDTOCHAN(client, chan, 'n'))
            return
        if 'm' in chan.modes:
            cancommands = client.utils.generic.permit(
                    client.s.common.config['channel']['hierarchy'].attrs['value'],
                    client.utils.generic.makecontext(
                            client.s.common.config['channel']['hierarchy'], 'mode', 'commands'
                    ), chan.users[client])
            if args[0].lower() not in client.utils.generic.lowlist(cancommands):
                client.svrsend(client.msg.ERR_CANNOTSENDTOCHAN(client, chan, 'm'))
                return 1
        if 'c' in chan.modes and args[0] == "PRIVMSG" and '\x03' in args[2]:
            client.svrsend(client.msg.ERR_CANNOTSENDTOCHAN(client, chan, 'c'))
            return 1
        if 'G' in chan.modes and args[0] == "PRIVMSG":
            args[2] = client.utils.generic.stripbadwords(args[2], client.s.common.config['channel']['badwords'])
        for i in chan.users:
            if i != client: client.sendto(i, args[0]+" "+args[1]+" :"+args[2])
    else:
        nick = client.utils.generic.nick_exist(client.s.clients, args[1])
        if not nick:
            snick = client.utils.generic.nick_exist(client.s.sclients, args[1])
            if snick: snick.s[args[0].lower()](client, snick, args[2])
            else: client.no(args[1])
        else:
            if nick.away: client.svrsend(client.msg.RPL_AWAY(client, nick))
            if 'G' in nick.modes and args[0] == "PRIVMSG":
                args[2] = client.utils.generic.stripbadwords(args[2], client.s.common.config['client']['badwords'])
            client.sendto(nick, args[0]+" "+args[1]+" :"+args[2])
    return 1

@Args(1,0)
def c_pong(rbuf, client, args):
    """
    Handle PONG command
    @param rbuf: PONG <server>
    """
    if len(args) > 1:
        if args[1].lower() == str(client.s.common.config['server']['name']).lower(): client.pong = 1
    else:
        client.svrsend(client.msg.ERR_NOORIGIN(client))
    return 1

@Args(3,2)
@Logged
def c_kick(rbuf, client, args):
    """
    Kick an user from a channel
    @param rbuf: KICK <nick> <channel> :<message>
    """
    chan = client.utils.generic.chan_exist(client.s.channels, args[1])
    if not chan:
        client.nochan(args[1])
        return 1
    if client not in chan.users:
        client.svrsend(client.msg.ERR_NOTONCHANNEL(client, chan))
        return 1
    cancommands = client.utils.generic.permit(
            client.s.common.config['channel']['hierarchy'].attrs['value'],
            client.utils.generic.makecontext(
                    client.s.common.config['channel']['hierarchy'], 'mode', 'commands'
            ), chan.users[client])
    if 'kick' not in cancommands:
        client.svrsend(client.msg.ERR_CHANOPRIVSNEEDED(client, chan))
        return 1
    nick = client.utils.generic.nick_exist(chan.users, args[2])
    if not nick:
        client.no(args[2])
        return 1
    if 'Q' in chan.modes:
        client.notice("You cannot kick people on "+args[1])
        client.svrsend(client.msg.ERR_RESTRICTED(client))
        return 1
    try: reason = " :"+args[3]
    except: reason = ""
    for u in chan.users:
        client.sendto(u, "KICK "+args[1]+" "+args[2]+reason)
    del(chan[nick])
    return 1

@Args(2,1)
@Logged
def c_mode(rbuf, client, args):
    """
    This function handles two kinds of MODE
    @param rbuf: The buffer depends on the type of mode
        - The user MODE's are typically changes which affect either how the
        client is seen by others or what 'extra' messages the client is sent
            - MODE <nickname> *( ( "+" / "-" ) *<modes> )
        - The MODE command is provided so that users may query and change the
        characteristics of a channel
            - MODE <channel> *( ( "-" / "+" ) *<modes> *<modeparams> )
    """
    if args[1][0] == "#":
        chan = client.utils.generic.chan_exist(client.s.channels, args[1])
        if not chan:
            client.no(args[1])
            return 1
        try:
            if args[2] == 'b' or args[2] == '+b' or args[2] == '-b':
                for b in chan.ban: client.svrsend(client.msg.RPL_BANLIST(client, chan, b))
                client.svrsend(client.msg.RPL_ENDOFBANLIST(client, chan))
                return 1
            if args[2] == 'e' or args[2] == '+e' or args[2] == '-e':
                for e in chan.exc: client.svrsend(client.msg.RPL_EXCEPTLIST(client, chan, e))
                client.svrsend(client.msg.RPL_ENDOFEXCEPTLIST(client, chan))
                return 1
        except: pass
        try: chan.mode(args[2], client)
        except:
            opts = ""
            for m in chan.modes:
                if m == 'k': opts += " "+chan.key
                if m == 'l': opts += " "+str(chan.maxusers)
            client.svrsend("324 "+client.nick+" "+args[1]+" +"+chan.modes+opts)
            client.svrsend("329 "+client.nick+" "+args[1]+" "+str(int(time.time())))
    else:
        nick = client.utils.generic.nick_exist(client.s.clients, args[1])
        if not nick:
            client.no(args[1])
            return 1
        if nick.nick != client.nick:
            client.svrsend(client.msg.ERR_USERSDONTMATCH(client))
            return 1
        try: nick.mode(args[2])
        except: client.svrsend(client.msg.RPL_UMODEIS(client))
    return 1

@Args(1)
@Logged
def c_names(rbuf, client, args):
    """
    By using the NAMES command, a user can list all nicknames that are 
    visible to him on a specified channel
    @param rbuf: NAMES <channel>
    """
    chan = client.utils.generic.chan_exist(client.s.channels, args[1])
    if chan: chan.names(client)
    else: client.nochan(args[1])
    return 1

@Args(2)
@Logged
def c_invite(rbuf, client, args):
    """
    The INVITE command is used to invite a user to a channel.
    @param rbuf: INVITE <nickname> <channel>
    """
    nick = client.utils.generic.nick_exist(client.s.clients, args[1])
    if not nick:
        client.no(args[1])
        return 1
    chan = client.utils.generic.chan_exist(client.s.channels, args[2])
    if not chan:
        client.nochan(args[2])
        return 1
    if client not in chan.users:
        client.svrsend(client.msg.ERR_NOTONCHANNEL(client, chan))
        return 1
    if 'V' in chan.modes:
        client.svrsend(client.msg.ERR_NOINVITE(client, chan))
        return 1
    chan.invite(client, nick)
    return 1

@Args(2,1)
@Logged
def c_topic(rbuf, client, args):
    """
    The TOPIC command is used to change or view the topic of a channel.
    The topic for channel <channel> is returned if there is no <topic> given
    @param rbuf: TOPIC <channel> [ <topic> ]
    """
    chan = client.utils.generic.chan_exist(client.s.channels, args[1])
    if not chan:
        client.nochan(args[1])
        return 1
    if len(args) > 2:
        chan.topic(client, args[2])
    else:
        if not chan.topicset: client.svrsend(client.msg.RPL_NOTOPIC(client, chan))
        else: chan.viewtopic(client)
    return 1
        
@Args(3,0)
@Logged
def c_who(rbuf, client, args):
    """
    The WHO command is used by a client to generate a query which returns
    a list of information which 'matches' the <mask> parameter given by
    the client.  In the absence of the <mask> parameter, all visible
    (users who aren't invisible (user mode +i) and who don't have a
    common channel with the requesting client) are listed.
    @param rbuf: WHO [ <mask> [ "o" ] ]
    """
    try:
        if len(args) > 1: pattern = args[1]
        else: pattern = "*"
        if len(args) > 2: o = args[2] == 'o'
        else: o = False
        if pattern[0] != "#":
            cpattern = re.compile("^"+pattern.replace("*", ".*?").lower()+"$")
            for c in client.s.clients:
                if cpattern.match(c.nick.lower()):
                    if c.joined == []: chan = "*"
                    else: chan = c.joined[len(c.joined)-1]
                    try: m = client.utils.generic.getprefix(client.s.common.config['channel']['hierarchy'], chan.users[c])
                    except: m = ""
                    if chan != "*": chan = chan.name
                    client.svrsend(client.msg.RPL_WHOREPLY(client, chan, c, m))
        else:
            chan = client.utils.generic.chan_exist(client.s.channels, pattern)
            if chan:
                for c in chan.users:
                    if 'i' not in c.modes or client in chan.users:
                        try: m = client.utils.generic.getprefix(client.s.common.config['channel']['hierarchy'], chan.users[c])
                        except: m = ""
                        client.svrsend(client.msg.RPL_WHOREPLY(client, chan.name, c, m))
        client.svrsend(client.msg.RPL_ENDOFWHO(client, pattern))
    except: excDEBUG("modules->commands->c_who", sys.exc_info())
    return 1
                  
@Args(0)
@Logged
def c_motd(rbuf, client, args):
    """
    The MOTD command is used to get the "Message Of The Day" of the current server
    @param rbuf: MOTD
    """
    client.motd()
    return 1

@Args(req=1)
@Logged
def c_ison(rbuf, client, args):
    """
    The ISON command was implemented to provide a quick and efficient
    means to get a response about whether a given nickname was currently on IRC.
        @param rbuf: ISON <nickname> *( SPACE <nickname> )
    """
    del(args[0])
    r = ""
    for c in args:
        if client.utils.generic.nick_exist(client.s.clients, c): r += c+" "
    client.svrsend(client.msg.RPL_ISON(client, r))
    return 1

@Args(3,0)
def c_ping(rbuf, client, args):
    """
    The PING command is used to test the presence of an active client or
    server at the other end of the connection
    @param rbuf: PING <server1> [ <server2> ]
    """
    if len(args) < 2:
        client.svrsend(client.msg.ERR_NOORIGIN(client))
        return 1
    elif len(args) > 2:
        if args[2].lower() == str(client.s.common.config['server']['name']).lower(): client.svrsend("PONG "+args[2]+" :"+args[1])
        else: client.svrsend(client.msg.ERR_NOSUCHSERVER(client, args[2]))
    else:
        client.svrsend("PONG %s :%s" % (client.s.common.config['server']['name'], args[1]))
    return 1

@Args()
@Logged
def c_list(rbuf, client, args):
    """
    The list command is used to list channels and their topics.  If the
    <channel> parameter is used, only the status of that channel is displayed.
    @param rbuf: LIST [ <channel> *( "," <channel> ) ]
    """
    client.svrsend(client.msg.RPL_LISTSTART(client))
    def list_modes(chan):
        modes = ""
        if 's' in chan.modes: modes += 's'
        if modes: return "[+"+modes+"]"
        else: return ""
    try:
        args[1]
        del(args[0])
        for c in args:
            for chan in client.s.channels:
                if re.match("^"+c.replace("*", ".*?")+"$", chan.name):
                    if 's' in chan.modes and client not in chan.users: continue
                    client.svrsend(client.msg.RPL_LIST(client, chan, list_modes(chan)))
    except:
        for chan in client.s.channels:
            if 's' in chan.modes and client not in chan.users: continue
            client.svrsend(client.msg.RPL_LIST(client, chan, list_modes(chan)))
    client.svrsend(client.msg.RPL_LISTEND(client))
    return 1
        
@Args(1)
@NoLogged
def c_pass(rbuf, client, args):
    """
    The PASS command is used to set a 'connection password'
    @param rbuf: PASS <password>
    """
    client.svrpass = args[1]
    return 1

@Args()
@Logged
def c_whois(rbuf, client, args):
    """
    This command is used to query information about particular user
    @param rbuf: WHOIS <nickname>
    """
    try:
        nick = 0
        try: nick = client.utils.generic.nick_exist(client.s.clients, args[1])
        except:
            client.svrsend(client.msg.ERR_NONICKNAMEGIVEN(client))
            return 1
        if not nick:
            client.svrsend(client.msg.ERR_NOSUCHNICK(client, args[1]))
            return 1
        if client.oper: addr = nick.raddr
        else: addr = nick.addr
        client.svrsend(client.msg.RPL_WHOISUSER(client, nick, addr))
        if (client.joined):
            channels = ""
            for chan in client.joined:
                channels += client.utils.generic.getprefix(client.s.common.config['channel']['hierarchy'], chan.users[client])+chan.name+" "
            client.svrsend(client.msg.RPL_WHOISCHANNELS(client, nick, channels))
        client.svrsend(client.msg.RPL_WHOISSERVER(client, nick, client.s.common.config['server']))
        if nick.oper: client.svrsend(client.msg.RPL_WHOISOPERATOR(client, nick))
        if nick.away: client.svrsend(client.msg.RPL_AWAY(client, nick))
        client.svrsend(client.msg.RPL_WHOISIDLE(client, nick))
        client.svrsend(client.msg.RPL_ENDOFWHOIS(client, nick))
    except: excDEBUG("modules.commands.whois", sys.exc_info())
    return 1

@Args(1,0)
@Logged
def c_away(rbuf, client, args):
    """
    With the AWAY command, clients can set an automatic reply string for
    any PRIVMSG commands directed at them (not to a channel they are on).
    The AWAY command is used either with one parameter, to set an AWAY
    message, or with no parameters, to remove the AWAY message.
    @param rbuf: AWAY [ <text> ]
    """
    try:
        client.away = args[1]
        client.svrsend(client.msg.RPL_NOWAWAY(client))
    except:
        client.away = ""
        client.svrsend(client.msg.RPL_UNAWAY(client))
    return 1
    
@Args(2,0)
@Logged
def c_whowas(rbuf, client, args):
    """
    Whowas asks for information about a nickname which no longer exists.
    This may either be due to a nickname change or the user leaving IRC.
    In response to this query, the server searches through its nickname
    history, looking for any nicks which are lexically the same
    (no wildcard matching here).
    @param rbuf: WHOWAS <nickname> *( "," <nickname> ) [ <count> ]
    """
    s = args[1].lower()
    t = client.utils.generic.lowdict(client.s.common.whowas)
    if len(args) <= 1:
        client.svrsend(client.msg.ERR_NONICKNAMEGIVEN(client))
        return 1
    if not s in t:
        client.svrsend(client.msg.ERR_WASNOSUCHNICK(client, args[1]))
    else:
        for ww in t[s]:
            client.svrsend(client.msg.RPL_WHOWASUSER(client, args[1], ww[0]))
            client.svrsend(client.msg.RPL_WHOWASSERVER(client, args[1], ww[1]))
    client.svrsend(client.msg.RPL_ENDOFWHOWAS(client, args[1]))
    return 1
        
@Args(0)
@Logged
def c_lusers(rbuf, client, args):
    """
    The LUSERS command is used to get statistics about the size of the
    IRC network
    @param rbuf: LUSERS
    """
    try:
        client.svrsend(client.msg.RPL_LUSERCLIENT(client, len(client.s.clients)+len(client.s.sclients), len(client.s.services), len(client.s.servers)))
        i = 0
        for c in client.s.clients:
            for h in str(client.s.common.config['client']['hierarchy'].attrs['value'])[:-1]:
                if h in c.modes:
                    i += 1
                    break
        client.svrsend(client.msg.RPL_LUSEROP(client, i))
        client.svrsend(client.msg.RPL_LUSERCHANNELS(client, len(client.s.channels)))
    except: excDEBUG("modules.commands.c_lusers", sys.exc_info())
    return 1
    
@Args(0)
@Logged
def c_admin(rbuf, client, args):
    """
    The admin command is used to find information about the administrator
    @param rbuf: ADMIN
    """
    client.svrsend(client.msg.RPL_ADMINME(client))
    client.svrsend(client.msg.RPL_ADMINLOC1(client))
    client.svrsend(client.msg.RPL_ADMINLOC2(client))
    client.svrsend(client.msg.RPL_ADMINEMAIL(client))
    return 1

@Args(0)
@Logged
def c_version(rbuf, client, args):
    """
    The VERSION command is used to query the version of the server program
    @param rbuf: VERSION
    """
    client.svrsend(client.msg.RPL_VERSION(client))
    return 1

@Args(0)
@Logged
def c_time(rbuf, client, args):
    """
    The time command is used to query local time from the specified server
    @param rbuf: TIME
    """
    client.svrsend(client.msg.RPL_TIME(client))
    return 1

@Args(0)
@Logged
def c_info(rbuf, client, args):
    """
    The INFO command is REQUIRED to return information describing the
    server: its version, when it was compiled, the patchlevel, when it
    was started, and any other miscellaneous information which may be
    considered to be relevant
    @param rbuf: INFO
    """
    info = lambda s: client.svrsend(client.msg.RPL_INFO(client, s))
    info("*:: "+client.s.common.info.version+" ::*")
    info("-- HEAD CODERS")
    info("- * Lethalman\t<lethalman@iosn.it>")
    info("-")
    info("-- CONTRIBUTORS")
    info("- * aengel\t\t<amiciangeli@amiciangeli.net>")
    info("- * Fr4nkir\t\t<frankir87@msn.com>")
    info("- * Fred1\t\t<Fred_weasley@libero.it>")
    info("-")
    info("-- THANKS TO")
    info("- * FyreBird\t<http://www.fyrebird.net>")
    info("- * Esploratori\t\t<http://www.esploratori.org>")
    info("-")
    info("- If you find any bugs, please mail")
    info("- lethalman@iosn.it")
    info("-")
    info("-- ONLINE SINCE")
    info("- "+client.s.startup)
    client.svrsend(client.msg.RPL_ENDOFINFO(client))
    return 1
    
@Args(req=1)
@Logged
def c_userhost(rbuf, client, args):
    """
    The USERHOST command takes a list of nicknames, each
    separated by a space character and returns a list of information
    about each nickname that it found.
    @param rbuf: USERHOST <nickname> *( SPACE <nickname> )
    """
    del(args[0])
    buf = ""
    for o in args:
        nick = client.utils.generic.nick_exist(client.s.clients, o)
        if not nick: continue
        buf += nick.nick
        if nick.oper: buf += "*"
        buf += "="
        if nick.away: buf += "-"
        else: buf += "+"
        buf += nick.user[0]+"@"
        if nick == client: buf += nick.raddr
        else: buf += nick.addr
        buf += " "
    client.svrsend(client.msg.RPL_USERHOST(client, buf))
    return 1

@Args(3)
@NoLogged
def c_server(rbuf, client, args):
    """
    The SERVER command is used to register a new server. A new connection
    introduces itself as a server to its peer.  This message is also used
    to pass server data over whole net.
    @param rbuf: SERVER <servername> <token> <info>
    """
    client.server = args[1:]
    client.login(client.s.common.Server)
    return 1

@Args()
def c_protoctl(rbuf, client, args):
    """
    This command is used to set protocols between the servers.
    @param rbuf: PROTOCTL <protocol> *( SPACE <protocol> )
    """
    client.protoctl = client.utils.generic.lowlist(args[1:])
    return 1
