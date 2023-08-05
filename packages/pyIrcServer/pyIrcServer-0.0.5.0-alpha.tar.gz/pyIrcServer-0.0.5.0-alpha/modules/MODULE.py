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
This module is a support for pyIS Modules.
The functions defined into the modules, use these function for decorations.
They help the developer to make a fast and good looking code.
@author: Lethalman
@see: PEP 318 (Python related)
@since: 01/12/2004
@var Font: Dict of the whole font
@type Font: Dict
@var Bold: Bold font
@type Bold: Char
@var Underline: Underline font
@type Underline: Char
@var Plain: Plain font
@type Plain: Char
"""

def Args(num=-1, req=-1):
    """
    Decoration for functions which needs to get arguments from a raw command.
    @param num: Numbers of arguments. -1 are the maximum set in the config file
    @param req: Numbers of required arguments
    @return: Return a decoration function
    @rtype: Function
    """
    def func(f):
        def nfunc(rbuf, client):
            _req = req
            _num = num
            if num > 0 and req < 0: _req = num
            if num < 0: _num = int(client.s.common.config['client']['maxoptions'])
            args = client.utils.generic.getopt(rbuf, _num+1)
            if len(args)-1 < _req:
                client.svrsend(client.msg.ERR_NEEDMOREPARAMS(client, args[0]))
                return 1
            return f(rbuf, client, args)
        nfunc.func_name = f.func_name
        return nfunc
    return func
    
def Logged(f):
    """
    The function can be excuted only if the client is logged.
    @return: Return a decoration function
    @rtype: Function
    """
    def func(rbuf, client, *args):
        if not client.logged:
            client.svrsend(client.msg.ERR_NOTREGISTERED(rbuf.split(' ')[0]))
            return 1
        return f(rbuf, client, *args)
    func.func_name = f.func_name
    return func

def NoLogged(f):
    """
    The function can be executed only if the client is not logged
    @return: Return a decoration function
    @rtype: Function
    """
    def func(rbuf, client, *args):
        if client.logged:
            client.svrsend(client.msg.ERR_ALREADYREGISTERED(client))
            return 1
        return f(rbuf, client, *args)
    func.func_name = f.func_name
    return func
    
__colors = dict(zip(('white', 'black', 'blue', 'green', 'red', 'dred', 'violet', 'orange', 'yellow', 'lgreen', 'dcyan', 'cyan', 'lblue', 'pink', 'gray', 'lgray'), range(15)))
Bold = '\x02'
Underline = '\x1f'
Plain = '\x0f'
Font = {
'bold': Bold,
'uline': Underline,
'plain': Plain,
'color': '\x03'
}
def Color(fore, back=None):
    """
    Return a color
    @param fore: Foreground color
    @param back: Background color
    @return: Formatted color
    @rtype: String
    """
    fore = fore.lower()
    if not fore in __colors: return ""
    ret = '\x03'+str(__colors[fore])
    if back:
        back = back.lower()
        if not back in __colors: return ""
        ret += ','+str(__colors[back])
    return ret
for k in __colors: Font[k] = Color(k)
Font['wb'] = Color('white', 'black')
