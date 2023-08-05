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

import sys, re

__doc__ = """
This util contains functions which can be called from classes and modules to help the developer
@author: Lethalman
"""

def clean(l):
    """
    Clean the given list from any empty string
    @param l: List to be cleaned
    @return: Return the cleaned list
    @rtype: List
    """
    for i in l:
        if i == "":
            del(l[l.index(i)])
    return l

def getopt(s, n):
    """
    Make a list of options on the given raw format
    @param s: Raw format buffer
    @param n: Length of the options
    @return: Return a list of options
    @rtype: List
    """
    ss = clean(s.split(':', 1))
    if not ss: return 0
    lss = clean(ss[0].split(' '))
    try: rss = ss[1]
    except: pass
    ret = []
    if len(lss) >= n:
        l = 0
        for i in range(len(lss)):
            if i == (n-1): break
            l += len(lss[i])+1
            ret.append(lss[i])
        last = s[l:]
        ret.append(last.strip())
    else:
        for i in lss: ret.append(i)
        try: ret.append(rss)
        except: pass
    return clean(ret)

def chan_exist(l, n):
    """
    Check if a given chan exists in a given list
    @param l: List of channels
    @param n: Channel name
    @return: Return false if the channel doesn't exist or the Channel instance itself if it exists
    @rtype: Boolean | Channel instance
    """
    for c in l:
        if n.lower() == c.name.lower(): return c
    return False

def nick_exist(l, n):
    """
    Check if a given nick exists in a given list
    @param l: List of clients
    @param n: Nickname
    @return: Return False if the client doesn't exist or the Client instance if it exists
    @rtype: Boolean | Client instance
    """
    for c in l:
        if n.lower() == c.nick.lower(): return c
    return False
    
def makecontext(hierarchy, element, subelement, attribute='name'):
    """
    Make a dict containing the value of the subelement
    for each mode.
    @note:
    In this example users who have the 'o' mode can set
    'ohv' modes, and users who have nothing can set 'v'.
    Example:
    
    >>> element = "mode"
    >>> subelement = "modes"
    >>> makecontext(hierarchy, element, subelement)
    {'o': 'ohv', '': 'v'}
    
    @param hierarchy: Hierarchy element
    @param element: Element name
    @param subelement: Subelement name
    @return: Return a dict {perm: actions}
    @rtype: Dict
    """
    ret = {}
    for i in hierarchy[element]:
        if subelement in i.data: ret[i.attrs[attribute]] = i[subelement].value
        else: ret[i.attrs[attribute]] = ""
    if subelement in hierarchy.data: ret[''] = hierarchy[subelement].value
    else: ret[''] = []
    return ret
    
def permit(hierarchy, context, perms, recurse=1):
    """
    The function check if one of the modes in the hierarchy is in perms,
    then get recursive permissions by the context.
    @note:
    Example:
        >>> hierarchy = ['o', 'h', '']
        >>> context = {'o': ['mode'], 'h': ['kick', 'topic'], '': ['privmsg']}
        >>> perms = 'h'
        >>> permit(hierarchy, context, perms)
        ['kick', 'topic', 'privmsg']
    
    @param hierarchy: The hierarchy element
    @param context: A dict containing a list of permissions
    @param perms: Current gained modes
    @return: Return a list of actions that can be done
    @rtype: List
    """
    if '' in context: can = context['']
    else: can = []
    if recurse:
        lh = len(hierarchy)
        for h in range(lh):
            if hierarchy[h] in perms:
                found = 1
                for hh in range(h, lh):
                    can += context[hierarchy[hh]]
                break
    else:
        for m in perms:
            if m in context: can += context[m]
    return can
      
def getusers(users, m):
    """
    Return a list of users which got the given mode in a given list of users.
    
    @param users: List of users
    @param m: Special mode
    @return: Return a list of users which got the given mode
    @rtype: List
    """
    ret = []
    for u, f in users.items():
        if m in f: ret.append(u)
    return ret
        
def getprefix(hierarchy, modes):
    """
    Get the prefix on the base of current modes and the hierarchy.
    The function looks for a mode in the hierarchy which is in modes,
    then get the related prefix using prefixes.
    
    @param hierarchy: The mode hierarchy
    @param modes: Current modes
    @return: Return the prefix
    @rtype: String
    """
    for h in hierarchy.attrs['value']:
        if h in modes:
            for m in hierarchy['mode']:
                if 'prefix' in m.attrs and m.attrs['name'] == h: return m.attrs['prefix']
    return ""
        
fullmask = re.compile("^.+?!.+?@.+?$")
raddrmask = re.compile("^!.+?@.+?$")
addrmask = re.compile("^@.+?$")
firstmask = re.compile("^.+?!.+?$")
rightmask = re.compile("^!.+?$")
def mask(m):
    """
    Filter a given incomplete mask into a standard one
    @param m: The normal mask
    @return: Standard mask
    @rtype: String
    """
    if '!' not in m and '@' not in m: return m+"!*@*"
    if fullmask.match(m): return m
    if raddrmask.match(m): return "*"+m
    if addrmask.match(m): return "*!*"+m
    if firstmask.match(m): return m+"@*"
    if rightmask.match(m): return "*"+m+"@*"
    return 0 
    
def ismask(m, t):
    """
    Check if a mask matches the real one
    @param m: The mask
    @param t: The real mask
    @return: True or false if it matches or not
    @rtype: Boolean
    """
    m = re.compile(m.replace("*", ".*?"))
    if m.match(t): return 1
    else: return 0
    
def isbanned(user, chan):
    """
    Check if a given user is banned on a channel.
    It looks first on the exceptions list
    @param user: The client to check
    @param chan: Channel
    @return: True or false if it's banned or not
    @rtype: Boolean
    """
    for e in chan.exc:
        if ismask(e, user.myself()): return 0
    for b in chan.ban:
        if ismask(b, user.myself()): return 1
    return 0
    
def lowlist(l):
    """
    Transform each element of a list in its lower format
    @param l: The list to convert
    @return: Return the lower list
    @rtype: List
    """
    for i in range(len(l)):
        l[i] = l[i].lower()
    return l

def lowdict(d, umask=None):
    """
    Transform each key of a dict in its lower format.
    If a key matches the umask, it won't be lowered
    @param d: The dict to convert
    @param umask: Don't trasform matching keys
    @return: Return the lower dict
    @rtype: Dict
    """
    newd = {}
    for k, v in d.items():
        if umask != None and re.match(umask, k): newd[k] = v
        else: newd[k.lower()] = v
    return newd
        
def stripbadwords(s, b):
    """
    Censure bad words in a given string
    @param s: String to be checked
    @param b: Badwords
    @return: Gives back the cleaned string
    @rtype: String
    """
    for bad in b:
        for vv in bad.value: s = re.sub("\S*?"+vv+"\S*", bad.attrs['replace'], s)
    return s
