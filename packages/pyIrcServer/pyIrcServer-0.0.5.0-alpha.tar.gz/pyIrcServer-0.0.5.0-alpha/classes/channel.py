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

import sys, time

__doc__ = """
This module contains the Channel class
@author: Lethalman
"""

class Channel:
    """
    The Channel class
    @ivar s: The Server instance
    @type s: Server instance
    @ivar name: The channel name
    @type name: String
    @ivar users: Users who joined this channel
    @type users: Dict
    @ivar modes: Channel modes
    @type modes: String
    @ivar modestime: Last modify to modes
    @type modestime: String
    @ivar key: The channel key
    @type key: String
    @ivar topicset: The channel topic
    @type topicset: String
    @ivar topictime: Last modify to the topic
    @type topictime: String
    @ivar topicby: Nickname who set the topic
    @type topicby: String
    @ivar invited: List of invited users
    @type invited: List
    @ivar ban: Banned users
    @type ban: List
    @ivar exc: Exceptions on ban
    @type exc: List
    @ivar maxusers: User join limit
    @type maxusers: Integer
    """

    def __init__(self, s, name):
        """
        Initialize the instance usually called by a Client one.
        @param s: The Server instance
        @param name: ThexcDEBUe channel name
        """
        global DEBUG, excDEBUG
        DEBUG, excDEBUG = s.common.DEBUG, s.common.excDEBUG
        self.s = s
        self.utils = self.s.common.utils
        self.name = name
        self.users = {}
        self.modes = ""
        self.modestime = ""
        self.key = ""
        self.topicset = ""
        self.topicby = ""
        self.topictime = ""
        self.invited = []
        self.ban = []
        self.exc = []
        self.maxusers = 0

    def join(self, user, key):
        """
        Join an user to myself.
        Check if the user is banned, invited, etc.
        @param user: The user who wants to join
        @param key: The given key
        @return: True or false if the user can join or not
        @rtype: Boolean
        """
        try:
            if user in self.users: return False
            if self.utils.generic.isbanned(user, self):
                user.svrsend(user.msg.ERR_BANNEDFROMCHAN(user, self))
                return 0
            if 'k' in self.modes and key != self.key:
                user.svrsend(user.msg.ERR_BADCHANNELKEY(user, self))
                return 0
            if 'i' in self.modes and user not in self.invited:
                user.svrsend(user.msg.ERR_INVITEONLYCHAN(user, self))
                return 0
            if 'l' in self.modes and len(self.users) == self.maxusers:
                user.svrsend(user.msg.ERR_CHANNELISFULL(user, self))
                return 0
            if not self.users: self.users[user] = self.s.common.config['channel']['hierarchy'].attrs['value'][0]
            else: self.users[user] = ""
            for i in self.users:
                user.sendto(i, "JOIN :"+self.name)
            self.s.sglobal("join", user, self)
            self.s.sglobal("mode", self, "+"+self.users[user], user.nick, str(int(time.time())))
            user.joined.append(self)
        except: excDEBUG("classes.channel.join", sys.exc_info())
        return 1

    def invite(self, user, to):
        """
        Invite an user to join a channel from another user.
        @param user: Client who invited
        @param to: Invited client
        @return: True or false if user can invite or not
        @rtype: Boolean
        """
        if 'i' in self.modes:
            cancommands = self.utils.generic.permit(
                    self.s.common.config['channel']['hierarchy'].attrs['value'],
                    self.utils.generic.makecontext(
                            self.s.common.config['channel']['hierarchy'], 'mode', 'commands'
                    ), self.users[user])
            if 'invite' not in cancommands:
                user.svrsend(user.msg.ERR_CHANOPRIVSNEEDED(user, self))
                return 0
        if to in self.users:
            user.svrsend(user.msg.ERR_USERONCHANNEL(user, to, self))
            return 0
        user.svrsend(user.msg.RPL_INVITE(user, to, self))
        if to.away: user.svrsend(user.msg.RPL_AWAY(user, to))
        if 'i' in self.modes:
            ops = user.utils.generic.getusers(self.users, self.s.common.config['channel']['hierarchy'].attrs['value'][0])
            for o in ops:
                o.notice('@'+self.name, user.nick+" has invited "+to.nick+" into the channel.")
        self.invited.append(to)
        user.sendto(to, "INVITE "+to.nick+" :"+self.name)
        return 1
        
    def names(self, user):
        """
        Return a list of clients which entered the channels,
        only if the user is inside me
        @param user: User who requested names
        @return: List of clients
        @rtype: List
        """
        names = ""
        if user in self.users:
            for i in self.users:
                n = user.utils.generic.getprefix(self.s.common.config['channel']['hierarchy'], self.users[i])+i.nick
                names += n+" "
            user.svrsend("353 "+user.nick+" = "+self.name+" :"+names)
        elif user not in self.users and self.users != {}:
            user.svrsend("353 "+user.nick+" = "+self.name+" :")
        user.svrsend("366 "+user.nick+" "+self.name+" :End of /NAMES list.")

    def viewtopic(self, user):
        """
        Send the topic to the client if it's not empty
        @param user: Client who requested viewtopic
        """
        if not self.topicset: return 1
        user.svrsend(user.msg.RPL_TOPIC(user, self))
        user.svrsend(user.msg.RPL_TOPICINFO(user, self))
        
    def topic(self, user, t):
        """
        Set the topic of the channel only if the user is allowed
        @param user: User who requested topic
        @param t: The topic
        """
        try:
            t = t[:int(self.s.common.config['channel']['topiclength'])]
            if not isinstance(user, self.s.common.SClient):
                if user not in self.users:
                    user.svrsend(user.msg.ERR_NOTONCHANNEL(user, self))
                    return 1
                if 't' in self.modes:
                    cancommands = self.utils.generic.permit(
                        self.s.common.config['channel']['hierarchy'].attrs['value'],
                        self.utils.generic.makecontext(
                                self.s.common.config['channel']['hierarchy'], 'mode', 'commands'
                        ), self.users[user])
                    if 'topic' not in cancommands:
                        user.svrsend(user.msg.ERR_CHANOPRIVSNEEDED(user, self))
                        return 1
                if t == self.topic: return 1
            self.topicset = t
            self.topictime = str(int(time.time()))
            self.topicby = user.nick
            for u in self.users:
                user.sendto(u, "TOPIC "+self.name+" :"+t)
            if not isinstance(user, self.s.common.SClient): self.s.sglobal("topic", user, self)
        except: excDEBUG("classes.channel.topic", sys.exc_info())

    def getmodes(self):
        """
        Return the channel modes with their args
        @return: Channel modes
        @rtype: String
        """
        modes = self.modes
        args = ""
        if 'k' in modes: args += self.key+" "
        return modes+" "+args
                        
    def mode(self, buf, user):
        """
        Set the channel modes.
        First check if the user is allowed or not
        @param buf: <modes> <modesparam>
        @param user: User who requested mode
        """
        try:
            add = -1
            modes = ""
            args = ""
            buf = buf.split(' ', 1)
            bufmodes = buf[0]
            SClient = self.s.common.SClient
            try: bufargs = filter(lambda x: len(x) != 0, buf[1].split(' '))
            except: bufargs = ""
            if isinstance(user, SClient): canmodes = str(self.s.common.config['channel']['hierarchy']['allmodes'])
            else: canmodes = self.utils.generic.permit(
                    self.s.common.config['channel']['hierarchy'].attrs['value'],
                    self.utils.generic.makecontext(
                            self.s.common.config['channel']['hierarchy'], 'mode', 'modes'
                    ), self.users[user])
            for c in bufmodes:
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
                if c not in str(self.s.common.config['channel']['hierarchy']['allmodes']):
                    if not isinstance(user, SClient): user.svrsend("472 "+user.nick+" "+c+" :is unknown mode char to me")
                    continue
                if c not in canmodes:
                    if not isinstance(user, SClient): user.svrsend(user.msg.ERR_CHANOPRIVSNEEDED(user, self))
                    continue
                if c not in str(self.s.common.config['channel']['hierarchy']['requirearg']) or (c == 'k' and not add) or (c == 'l' and not add):
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
                else:
                    try: narg = bufargs[0]
                    except: continue
                    del(bufargs[0])
                    if c in self.s.common.config['channel']['hierarchy'].attrs['value']:
                        nick = self.utils.generic.nick_exist(self.s.clients, narg)
                        if not nick or nick not in self.users:
                            user.no(narg)
                            continue
                        if add and c not in self.users[nick]:
                            self.users[nick] += c
                            args += narg+" "
                            if changed:
                                modes += "+"+c
                                changed = 0
                            else: modes += c
                        elif not add and c in self.users[nick]:
                            self.users[nick] = self.users[nick].replace(c, "")
                            args += narg+" "
                            if changed:
                                modes += "-"+c
                                changed = 0
                            else: modes += c
                    else:
                        if add and c not in self.modes or c == 'l':
                            if c == 'k': 
                                if narg == self.key: continue
                                self.key = narg
                            elif c == 'b':
                                narg = self.utils.generic.mask(narg)
                                if narg in self.ban: continue
                                if narg: self.ban.append(narg)
                                else: continue
                            elif c == 'e':
                                narg = self.utils.generic.mask(narg)
                                if narg in self.exc: continue
                                if narg: self.exc.append(narg)
                                else: continue
                            elif c == 'l':
                                self.modes = self.modes.replace("l", "")
                                self.maxusers = int(narg)
                            if c != 'b' and c != 'e': self.modes += c
                            args += narg+" "
                            if changed:
                                modes += "+"+c
                                changed = 0
                            else: modes += c
                        elif (not add and c in self.modes) or c == 'b' or c == 'e':
                            if c == 'b':
                                narg = self.utils.generic.mask(narg)
                                if narg not in self.ban: continue
                                del(self.ban[self.ban.index(narg)])
                            elif c == 'e':
                                narg = self.utils.generic.mask(narg)
                                if narg not in self.exc: continue
                                del(self.exc[self.exc.index(narg)])
                            self.modes = self.modes.replace(c, "")
                            args += narg+" "
                            if changed:
                                modes += "-"+c
                                changed = 0
                            else: modes += c
            if modes:
                self.modestime = str(int(time.time()))
                for u in self.users:
                    user.sendto(u, "MODE "+self.name+" "+modes+" "+args)
                if not isinstance(user, SClient): self.s.sglobal("mode", self, modes, args, self.modestime, user.nick)
        except: excDEBUG("classes.channel.mode", sys.exc_info())
        
    def perform(self, user, perform):
        try:
            for pcmd in perform:
                pcmd = pcmd.replace('%nick', user.nick).replace('%chan', self.name)
                cmd = pcmd.split(' ', 1)[0].lower()
                if cmd in self.s.common.commands:
                    for f in self.s.common.commands[cmd]:
                        if not f(pcmd, user): break
        except: excDEBUG("classes.channel.perform", sys.exc_info())

    def _check(self):
        """
        If i've not users anymore, remove myself from channels
        """
        if not self.users: del(self.s[self])

    def __delitem__(self, user):
        """
        Remove a client from the channel
        @param user: User to remove
        """
        del(self.users[user])
        del(user.joined[user.joined.index(self)])
        if user in self.invited: del(self.invited[self.invited.index(user)])
        self._check()
