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

import sys, os, re, time
from MODULE import *

__doc__ = """
Operators commands' parser
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
    __functions__ = [c_rehash, c_oper, c_kill, c_engine, c_restart, c_kline]
    add = common.addcommand
    for f in __functions__:
        add(f.func_name[2:], f)
    
@Args(0)
@Logged
def c_rehash(rbuf, client, args):
    """
    This function let opers rehash the configuration file "on the fly"
    @param rbuf: REHASH
    """
    client.s.rehash()
    client.svrsend(client.msg.RPL_REHASHING(client))
    return 1

@Args(2)
@Logged
def c_oper(rbuf, client, args):
    """
    A normal user uses the OPER command to obtain operator privileges
    @param rbuf: OPER <name> <password>
    """
    found = 0
    for op in client.s.common.config['oper']:
        if op.attrs['user'].lower() == args[1].lower():
            found = 1
            break
    if not found:
        client.svrsend(client.msg.ERR_NOOPERHOST(client))
        return 1
    if op['password'].attrs['crypt'].lower() == 'yes': check = client.utils.crypt.digest(args[2])
    else: check = args[2]
    if str(op['password']) == check:
        r = 0
        for uh in op['userhosts'].value:
            if re.match(uh, client.myself()):
                r = 1
                break
        if not r:
            client.svrsend(client.msg.ERR_NOOPERHOST(client))
            return 1
        for m in str(op['modes']):
            if m not in client.modes: client.modes += m
        client.svrsend(client.msg.RPL_YOUREOPER(client, op.attrs['name']))
        client.oper, client.opname = args[1], op.attrs['name']
        client.addr = client.utils.vhost.makevhost(client.raddr, str(op['virtualhost']))
    else:
        client.svrsend(client.msg.ERR_PASSWDMISMATCH(client))
    return 1
            
@Args(2)
@Logged
def c_kill(rbuf, client, args):
    """
    The KILL command is used to cause a client-server connection to be
    closed by the server which has the actual connection
    @param rbuf: KILL <nickname> <comment>
    """
    nick = client.utils.generic.nick_exist(client.s.clients, args[1])
    if not nick:
        client.no(args[1])
        return 1
    client.s.notice('k', "Received KILL message for %s from %s Path: %s (%s)" % (nick.myself(), client.nick, client.myself(), args[2]))
    client.sendto(nick, "KILL %s :%s (%s)" % (args[1], client.myself(), args[2]))
    msg = "[%s] Killed by %s (%s)" % (client.s.common.config['server']['name'], client.nick, args[2])
    nick.bye(msg, client.nick+" ("+msg+")")
    return 1

@Args()
@Logged
def c_engine(rbuf, client, args):
    """
    This is an optional command made for administrators to control the server engines.
    It handles several functions listed belown:
        - MODULE < LIST >
    @param rbuf: ENGINE < MODULE >
    """
    def __send(msg):
        msg =  "%(wb)s"+msg
        client.rnotice(msg % Font)
        
    __slist = lambda msg: __send("%(lblue)s>>>%(color)s "+msg)
    __serr = lambda msg: __send("%(red)s>>>%(color)s "+msg)
    __sok = lambda msg: __send("%(green)s>>>%(color)s "+msg)
        
    engines = {
        '_menu_': 1,
        'MODULE': {
            '_menu_': 1,
            'LIST': {'_menu_': 0, '_args_': []},
            'ADD': {
                '_menu_': 0,
                '_args_': ['module']
            },
            'REMOVE': {
                '_menu_': 0,
                '_args_': ['module']
            },
            'RELOAD': {
                '_menu_': 0,
                '_args_': ['module']
            }
        }
    }
    
    def __mlist(l, middle='%(uline)s'):
        h = '< '
        for a in (m for m in l if m[0] != '_'): h += middle+a+middle+' | '
        if len(h) > 2: h = h[:-2]
        h += '>'
        return h
    
    def __menu(arg=1, menu=engines, where="ENGINE"):
        def __usage(l):
            __serr("Usage: %(bold)s"+where+"%(bold)s "+__mlist(l))
        if len(args) <= arg and menu['_menu_']:
            __usage(menu.keys())
            return 0
        elif len(args) < arg and not menu['_menu_']:
            __usage(menu['_args_'])
            return 0
        try: f = args[arg].upper()
        except: f = ''
        if menu['_menu_']:
            if len(args) <= arg:
                __usage(menu.keys())
                return 0
            if f not in (m for m in menu if m[0] != '_'):
                __serr("Unknown %(bold)s"+where+"%(bold)s function: %(uline)s"+f)
                return 0
        else:
            if len(args)-arg < len(menu['_args_']):
                __usage(menu['_args_'])
                return 0
        if not f in menu: return 1
        return __menu(arg+1, menu[f], where+"->"+f)
    
    def __module():
        del(args[0])
        def __list():
            __slist("%(yellow)sMODULE%(plain)s->%(orange)sLIST%(plain)s:")
            for m in client.s.common.modules:
                __send("- "+m.__name__.split('.', 1)[1])
            __slist("END")
        def __remove(w=True):
            for m in (m for m in client.s.common.modules):
                if m.__name__.split('.', 1)[1] == args[2]:
                    del(client.s.common[m])
                    if w: __sok("Module %r removed" % args[2])
                    return
            __serr("Module %r not found" % args[2])
        def __add(w=True):
            mod = getattr(__import__("modules."+args[2]), args[2])
            if mod in client.s.common.modules:
                __serr("Module %r already loaded!" % args[2])
                return
            try: mod.__functions__
            except:
                __serr("Module %r does not seem to have __functions__" % args[2])
                return
            mod.__init__(client.s.common)
            client.s.common.modules.add(mod)
            if w: __sok("Module %r added successful!" % args[2])
        def __reload():
            for m in client.s.common.modules:
                if m.__name__.split('.')[1] == args[2]:
                    __remove(False)
                    reload(m)
                    __add(False)
                    __sok("Module %r realoded successful!" % args[2])
                    return
            __serr("Module %r is not loaded" % args[2])
        f = args[1].lower()
        if f == 'list': __list()
        elif f == 'remove': __remove()
        elif f == 'add': __add()
        elif f == 'reload': __reload()
        else: __send(">>> Unknown ENGINE->MODULE function: %r" % f)
    if not __menu(): return 1
    f = args[1].lower()
    if f == 'module': __module()
    return 1

@Args(0)
@Logged
def c_restart(rbuf, client, args):
    """
    Restart the IRCd. (doesn't work well yet)
    @param rbuf: RESTART
    """
    #os.system("python ircd.py restart")
    return 1

@Args(3, 1)
@Logged
def c_kline(rbuf, client, args):
    """
    Ban an user locally.
    @param rbuf: KLINE ( ( "+" / "-" ) <mask> ) [ <time> [ <reason> ] ]
    """
    try:
        op = args[1][0]
        if op in ('+', '-'): mask = client.utils.generic.mask(args[1][1:])
        else:
            mask = client.utils.generic.mask(args[1])
            op = '+'
        if len(args) > 2:
            t = args[2]
            if t[-1] == 'd':
                try: t = int(t[:-1])
                except: return 1
                t *= 1440
            else:
                try: t = int(t)
                except: return 1
        else: t = 0
        if len(args) > 3: reason = args[3]
        else: reason = 'no reason'
        if op == '+':
            if mask in client.s.kline: return 1
            client.s.kline[mask] = {
                'from': client.nick,
                'expire': t,
                'reason': reason,
                'time': time.ctime()
            }
            client.s.db.insert('klines', client.nick, mask, t, reason, client.s.kline[mask]['time'])
            client.s.notice('o', "Permanent KLine added for %s on %s (from %s: %s)" %
                    (mask, client.s.kline[mask]['time'], client.myself(), reason))
            for c in client.s.clients: c.banned()
        else:
            if mask in client.s.kline:
                client.s.notice('o', "%s removed KLine %s (set at %s: %s)" %
                        (client.myself(), mask, client.s.kline[mask]['time'], client.s.kline[mask]['reason']))
                del client.s.kline[mask]
                client.s.db.delete('klines', mask=mask)
    except: excDEBUG("modules.oper.c_kline", sys.exc_info())
    return 1
