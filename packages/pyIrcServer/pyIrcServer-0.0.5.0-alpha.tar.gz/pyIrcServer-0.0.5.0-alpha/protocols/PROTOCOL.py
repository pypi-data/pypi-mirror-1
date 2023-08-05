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

"""
This module is intended to be a support for protocol modules.
It has decoration functions needed by protocol commands to make a less work and make a more readable code
@author: Lethalman
@see: PEP 318 (Python related)
@since: 06/12/2004
"""

def Args(num=-1):
    """
    Decoration for functions which needs to get arguments from a raw command and get the sender of a message (if known)
    @param num: Numbers of arguments, -1 for infinite
    @return: Return a decoration function
    @rtype: Function
    """
    def func(f):
        def nfunc(rbuf, client):
            opts = []
            if rbuf[0] == ":":
                opts.append(rbuf[1:rbuf.find(' ')])
                rbuf = rbuf[rbuf.find(' ')+1:]
            args = client.utils.generic.getopt(rbuf, num+1)
            return f(rbuf, client, args, *opts)
        nfunc.func_name = f.func_name
        return nfunc
    return func
