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

import sys, time, info

__doc__ = """
This module contains a set of IRCd messages, both RPL and ERR.
Each message is a lambda function, which returns the message by giving it the requested arguments
@author: Lethalman
@see: RFC 2812
@var common: The Common instance
@type common: Common instance
"""

common = None

RPL_WELCOME = lambda u: "001 "+u.nick+" :Welcome to the %s IRC Network %s" % (common.config['server']['netname'], u.myself())
RPL_YOURHOST = lambda u: "002 "+u.nick+" :Your host is %s, running version %s" % (common.config['server']['name'], info.version)
RPL_CREATED = lambda u: "003 "+u.nick+" :This server was created "+info.built
RPL_MYINFO = lambda u: "004 "+u.nick+" :%s %s %s %s" % (common.config['server']['name'], info.version, common.config['client']['hierarchy']['allmodes'], common.config['channel']['allmodes'])
RPL_LUSERCLIENT = lambda u, c, s, e: "251 "+u.nick+" :There are "+str(c)+" users and "+str(s)+" services on "+str(e+1)+" servers"
RPL_LUSEROP = lambda u, c: "252 "+u.nick+" "+str(c)+" :operator(s) online"
RPL_LUSERCHANNELS = lambda u, c: "254 "+u.nick+" "+str(c)+" :channels formed"
RPL_ADMINME = lambda u: "256 %s %s :Administrative info" % (u.nick, common.config['server']['name'])
RPL_ADMINLOC1 = lambda u: "257 %s :%s" % (u.nick, common.config['admin'].value[0])
RPL_ADMINLOC2 = lambda u: "258 %s :%s" % (u.nick, common.config['admin'].value[1])
RPL_ADMINEMAIL = lambda u: "258 %s :%s" % (u.nick, common.config['admin'].value[2])
RPL_AWAY = lambda u, n: "301 "+u.nick+" "+n.nick+" :"+n.away
RPL_USERHOST = lambda u, r: "302 "+u.nick+" :"+r
RPL_ISON = lambda u, r: "303 "+u.nick+" :"+r
RPL_UNAWAY = lambda u: "305 "+u.nick+" :You are no longer marked as being away"
RPL_NOWAWAY = lambda u: "306 "+u.nick+" :You have been marked as being away"
RPL_WHOISUSER = lambda u, n, a: "311 "+u.nick+" "+n.nick+" "+n.user[0]+" "+a+" * :"+n.user[3]
RPL_WHOISSERVER = lambda u, n, s: "312 %s %s %s :%s" % (u.nick, n.nick, s['name'], s['netname'])
RPL_WHOWASSERVER = lambda u, n, w: "312 "+u.nick+" "+n+" "+w
RPL_WHOISOPERATOR = lambda u, n: "313 "+u.nick+" "+n.nick+" :is a "+n.opname
RPL_WHOISIDLE = lambda u, n: "317 "+u.nick+" "+n.nick+" "+str(int(time.time())-n.idle)+" "+str(n.signon)+" :seconds idle, signon time"
RPL_ENDOFWHOIS = lambda u, n: "318 "+u.nick+" "+n.nick+" :End of WHOIS list"
RPL_WHOISCHANNELS = lambda u, n, c: "319 "+u.nick+" "+n.nick+" :"+c
RPL_WHOWASUSER = lambda u, n, w: "314 "+u.nick+" "+n+" "+w
RPL_ENDOFWHOWAS = lambda u, n: "369 "+u.nick+" "+n+" :End of WHOWAS"
RPL_LISTSTART = lambda u: "321 "+u.nick+" Channel :Users Topic"
RPL_LIST = lambda u, c, a: "322 "+u.nick+" "+c.name+" "+str(len(c.users))+" :"+a+" "+c.topicset
RPL_LISTEND = lambda u: "323 "+u.nick+" :End of /LIST"
RPL_CHANNELMODEIS = lambda u, c: "324 "+u.nick+" "+c.name+" +"+c.getmodes()
RPL_CHANNELMODETIME = lambda u, c: "329 "+u.nick+" "+c.name+" "+c.modestime
RPL_NOTOPIC = lambda u, c: "331 "+u.nick+" "+c.name+" :No topic is set"
RPL_TOPIC = lambda u, c: "332 "+u.nick+" "+c.name+" :"+c.topicset
RPL_TOPICINFO = lambda u, c: "333 "+u.nick+" "+c.name+" "+c.topicby+" "+c.topictime
RPL_INVITE = lambda u, t, c: "341 "+u.nick+" "+t.nick+" "+c.name
RPL_WHOREPLY = lambda u, w, f, m: "352 %s %s %s %s %s %s H%s :0 %s" % (u.nick, w, f.user[0], f.addr, common.config['server']['name'], f.nick, m, f.user[3])
RPL_ENDOFWHO = lambda u, w: "315 "+u.nick+" "+w+" :End of WHO list"
RPL_EXCEPTLIST = lambda u, c, m: "348 "+u.nick+" "+c.name+" "+m
RPL_ENDOFEXCEPTLIST = lambda u, c: "349 "+u.nick+" "+c.name+" :End of channel exception list"
RPL_VERSION = lambda u: "351 %s %s. %s :Built the %s - %s" % (u.nick, info.version.replace(" ", ""), common.config['server']['name'], info.built, info.website)
RPL_NAMREPLY = lambda u, c, n: "353 "+u.nick+" "+c.type+" "+c.name+" :"+n
RPL_ENDOFNAMES = lambda u, c: "366 "+u.nick+" "+c.name+" :End of NAMES list"
RPL_BANLIST = lambda u, c, m: "367 "+u.nick+" "+c.name+" "+m
RPL_ENDOFBANLIST = lambda u, c: "368 "+u.nick+" "+c.name+" :End of channel ban list"
RPL_INFO = lambda u, s: "371 "+u.nick+" :"+s
RPL_ENDOFINFO = lambda u: "374 "+u.nick+" :End of /INFO list"
RPL_MOTDSTART = lambda u: "375 %s :- %s Message of the day - " % (u.nick, common.config['server']['name'])
RPL_MOTD = lambda u, t: "372 "+u.nick+" :- "+t
RPL_ENDOFMOTD = lambda u: "376 "+u.nick+" :End of MOTD command"
RPL_YOUREOPER = lambda u, o: "381 "+u.nick+" :You are now a "+o
RPL_REHASHING = lambda u: "382 "+u.nick+" config.xml :Rehashing"
RPL_TIME = lambda u: "391 %s %s :%s" % (u.nick, common.config['server']['name'], time.ctime())
RPL_UMODEIS = lambda u: "221 "+u.nick+" +"+u.modes
RPL_TRYAGAIN = lambda u, c: "263 "+u.nick+" "+c+" :Please wait a while and try again."

ERR_NOSUCHNICK = lambda u, n: "401 "+u.nick+" "+n+" :No such nick/channel"
ERR_NOSUCHSERVER = lambda u, s: "402 "+u.nick+" "+s+" :No such server"
ERR_NOSUCHCHANNEL = lambda u, c: "403 "+u.nick+" "+c+" :No such channel"
ERR_CANNOTSENDTOCHAN = lambda u, c, m: "404 "+u.nick+" "+c.name+" :Cannot send to channel (+"+m+")"
ERR_TOOMANYCHANNELS = lambda u, c: "405 "+u.nick+" "+c+" :You have joined too many channels"
ERR_WASNOSUCHNICK = lambda u, n: "406 "+u.nick+" "+n+" :There was no such nickname"
ERR_NOORIGIN = lambda u: "409 "+u.nick+" :No origin specified"
ERR_NORECIPIENT = lambda u, c: "411 "+u.nick+" :No recipient given ("+c+")"
ERR_NOTEXTTOSEND = lambda u: "412 "+u.nick+" :No text to send"
ERR_UNKNOWNCOMMAND = lambda u, c: "421 "+u.nick+" "+c+" :Unknown command"
ERR_NOMOTD = lambda u: "422 "+u.nick+" :MOTD File is missing"
ERR_NONICKNAMEGIVEN = lambda u: "431 "+u.nick+" :No nickname given"
ERR_ERRONEOUSNICKNAME = lambda u, n: "432 "+u.nick+" "+n+" :Erroneous nickname"
ERR_ERRONEOUSCHANNELNAME = lambda u, n: "432 "+u.nick+" "+n+" :Erroneous channel name"
ERR_NICKNAMEINUSE = lambda u, n: "433 "+u.nick+" "+n+" :Nickname is already in use"
ERR_NICKCOLLISION = lambda u, n, f: "436 "+u.nick+" "+n+" :Nickname collision KILL from "+f.user[0]+"@"+f.addr
ERR_UNAVAILRESOURCE = lambda u, r: "437 "+u.nick+" "+r+" :Nick/channel is temporarily unavailable"
ERR_USERNOTINCHANNEL = lambda u, n, c: "441 "+u.nick+" "+n+" "+c+" :They aren't on that channel"
ERR_NOTONCHANNEL = lambda u, c: "442 "+u.nick+" "+c.name+" :You're not on that channel"
ERR_USERONCHANNEL = lambda u, n, c: "443 "+u.nick+" "+n.nick+" "+c.name+" :is already on channel"
ERR_NOLOGIN = lambda u, n: "444 "+u.nick+" "+n+" :User not logged in"
ERR_SUMMONDISABLED = lambda u: "445 "+u.nick+" :SUMMON has been disabled"
ERR_NOTREGISTERED = lambda c: "451 "+c+" :You have not registered"
ERR_NEEDMOREPARAMS = lambda u, c: "461 "+c+" :Not enough parameters"
ERR_ALREADYREGISTERED = lambda u: "462 "+u.nick+" :Unauthorized command (already registered)"
ERR_NOPERMFORHOST = lambda u: "463 "+u.nick+" :Your host isn't among the privileged"
ERR_PASSWDMISMATCH = lambda u: "464 "+u.nick+" :Password incorrect"
ERR_YOUREBANNEDCREEP = lambda u: "465 "+u.nick+" :You are banned from this server"
ERR_YOUWILLBEBANNED = lambda u: "466 "+u.nick+" :You will be banned from this server"
ERR_KEYSET = lambda u, c: "467 "+u.nick+" "+c.name+" :Channel key already set"
ERR_CHANNELISFULL = lambda u, c: "471 "+u.nick+" "+c.name+" :Cannot join channel (+l)"
ERR_UNKNOWNMODE = lambda u, c: "472 "+u.nick+" "+c+" :is unknown mode char to me"
ERR_INVITEONLYCHAN = lambda u, c: "473 "+u.nick+" "+c.name+" :Cannot join channel (+i)"
ERR_BANNEDFROMCHAN = lambda u, c: "474 "+u.nick+" "+c.name+" :You are banned from the channel (+b)"
ERR_BADCHANNELKEY = lambda u, c: "475 "+u.nick+" "+c.name+" :Cannot join channel (+k)"
ERR_BADCHANMASK = lambda u, c: "476 "+u.nick+" "+c.name+" :Bad channel Mask"
ERR_NOCHANMODES = lambda u, c: "477 "+u.nick+" "+c.name+" :Channel doesn't support modes"
ERR_BANLISTFULL = lambda u, c, ch: "478 "+u.nick+" "+c.name+" "+ch+" :Channel list is full"
ERR_NOPRIVILEGES = lambda u: "481 "+u.nick+" :Permission Denied- You're not an IRC operator"
ERR_CHANOPRIVSNEEDED = lambda u, c: "482 "+u.nick+" "+c.name+" :You're not channel operator"
ERR_CANTKILLSERVER = lambda u: "483 "+u.nick+" :You can't kill a server!"
ERR_RESTRICTED = lambda u: "484 "+u.nick+" :Your connection is restricted!"
ERR_UNIQOPPRIVSNEEDED = lambda u: "485 "+u.nick+" :You're not the original channel operator"
ERR_NOOPERHOST = lambda u: "491 "+u.nick+" :No O-lines for your host"
ERR_UMODEUNKNOWNFLAG = lambda u: "501 "+u.nick+" :Unknown MODE flag"
ERR_USERSDONTMATCH = lambda u: "502 "+u.nick+" :Cannot change mode for other users"
ERR_NOINVITE = lambda u, c: "518 "+u.nick+" :Cannot invite (+V) at channel "+c.name
