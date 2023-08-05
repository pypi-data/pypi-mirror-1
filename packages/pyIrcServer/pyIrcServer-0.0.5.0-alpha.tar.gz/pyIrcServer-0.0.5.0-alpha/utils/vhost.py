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

import md5, re

__doc__ = """
This module contains utilities to make virtual hosts.
Virtual hosts are used instead of real addresses for clients
@author: Lethalman
"""

def makevhost(ip, mask):
	"""
	Make a unic virtual host for a given ip by using a given mask
	@param ip: Algorithm based on this IP
	@param mask: Customize virtual host with this mask
	@return: Return the virtual host
	@rtype: String
	"""
	tot = 0
	r = md5.new(ip).hexdigest().upper()
	for i in r: tot+=ord(i)
	step = tot/100
	while(step>32): step /= 2
	while(1):
		m = re.search("%(\d+?)%", mask)
		if not m: break
		n = int(m.group(1))
		ret = ""
		pos = step
		while(len(ret) < n):
			ret += r[pos]
			pos+=step
			if pos >= 32: pos -= 32
		mask = mask.replace("%"+str(n)+"%", ret)
	return mask