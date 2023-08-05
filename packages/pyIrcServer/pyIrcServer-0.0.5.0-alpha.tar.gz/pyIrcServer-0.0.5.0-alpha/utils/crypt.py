#!/usr/bin/env python
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

import md5
import sys
from getpass import getpass

__doc__ = """
This module can be used as standalone or as a pyIS util module.
	- Standalone Mode: it's used to generate passwords for the config file
	- Util module Mode: it's used internally by the IRCd to check passwords
@author: Lethalman
"""

def digest(s):
	"""
	Digest a given clear password
	@param s: Password to crypt
	@return: Give back the crypted password
	@rtype: String
	"""
	return md5.new(s).hexdigest()

if __name__ == '__main__':
	try:
		while 1:
			r = ' '
			print digest(getpass("Password: "))
			while r.lower() != '': r = raw_input("Press Ctrl+C to quit or press ENTER to crypt again")
	except: print "\nBye!"