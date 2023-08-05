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

import sys, time, string

__doc__ = """
This module contains the Log class
@author: Lethalman
"""

class Log:
    """
    The Log class is used to log pyIS events on a file
    @ivar common: The Common instance
    @type common: Common instance
    """
    def __init__(self, common):
        """
        Get a Log instance. Usually pyIS need only one of this in the Common instance,
        used by the whole server.
        @param common: Common instance
        """
        global DEBUG, excDEBUG
        DEBUG, excDEBUG = common.DEBUG, common.excDEBUG
        self.common = common

    def write(self, log):
        """
        Write a log to the log file.
        @param log: Logging data. It should be a tuple (event, log)
        """
        try:
            tlog = string.Template(str(self.common.config['log']['format']))
            t = time.localtime()
            tlog = tlog.safe_substitute(hours=t.tm_hour, minutes=t.tm_min, seconds=t.tm_sec,
                    day=t.tm_mday, month=t.tm_mon, year=t.tm_year,
                    event=log[0], log=log[1])
            f = open(self.common.config['log'].attrs['file'], "a")
            f.write(tlog+"\n")
            f.close()
        except: print excDEBUG("classes.log.write", sys.exc_info())
