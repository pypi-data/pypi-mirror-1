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
This module is a support for pyIS Classes.
The functions defined into the classes use these function for decorations.
They help the developer to make a fast and good looking code.
@author: Lethalman
@see: PEP 318 (Python related)
@since: 02/12/2004
@var rbreak: This variable is used when reading data from the connection.
It filters unknown characters as newline one.
"""

import re

rbreak = re.compile("^[\xff\xfb\xf4\x06\xfd\n\r\t\x0c\x0b ]*$")

def sockread(f):
    """
    This decoration is used to read data from socket
    by every connection. Its base is really common.
    @return: Return a decoration function
    @rtype: Function
    """
    def func(self):
        while(self.connected):
            try: readed = self.sock.recv(8192)
            except: self.bye()
            if not readed:
                self.bye()
                return
            try: realbuf = filter(lambda x:len(x)>0, readed.strip().split('\n'))
            except: return
            if not self.connected:
                self.bye()
                return
            for rbuf in realbuf:
                rbuf = rbuf.strip()
                if rbreak.match(rbuf): continue
                f(self, rbuf)
    func.func_name = f.func_name
    return func
