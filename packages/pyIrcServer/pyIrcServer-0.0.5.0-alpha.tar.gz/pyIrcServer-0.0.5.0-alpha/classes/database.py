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

import psycopg, sys, thread, time

__doc__ = """
Handles database requests in real time through PostgreSQL
notifies. This allows external programs to have a direct
access to the server informations.
@author: Lethalman
@see: PostgreSQL and PsycoPG
@since: 28/02/05
"""

class Database:
    """
    The Database class.
    This class is used to handle database data and external requests
    @ivar s: The Server instance itself
    @type s: Server instance
    @ivar dsn: The connect path of the pgserver
    @type dsn: String
    @ivar connected: Connection state
    @type connected: Boolean
    @ivar conn: Database Connection
    @type conn: PostgreSQL Connection
    @ivar curs: Database cursor
    @type curs: PostgreSQL Cursor
    """
    
    def __init__(self, s):
        """
        Initialize database informations
        @param s: The MainServer instance
        """
        global DEBUG, excDEBUG
        DEBUG, excDEBUG = s.common.DEBUG, s.common.excDEBUG
        self.s = s
        db = self.s.common.config['database']
        self.opts = {}
        if 'hostname' in db.data:
            hn = db['hostname']
            if str(hn): self.opts['host'] = str(hn)
            if 'port' in hn.attrs: self.opts['port'] = hn.attrs['port']
        if str(db['dbname']): self.opts['database'] = str(db['dbname'])
        if str(db['username']): self.opts['user'] = str(db['username'])
        if str(db['password']): self.opts['pass'] = str(db['password'])
        self.connected = False

    def connect(self):
        """
        Let's connect to the database and get informations.
        Then start handling notifies.
        """
        self.connected = True
        try: self.conn = psycopg.connect(**self.opts)
        except:
            excDEBUG("classes.database.connect", sys.exc_info())
            return
        self.conn.autocommit(1)
        self.curs = self.conn.cursor()
        self.get_klines()
        thread.start_new_thread(self.notifies, ())
        
    def notifies(self):
        """
        Handle notifies from external resources.
        """
        try:
            self.curs.execute("""
            listen pyis_rehash;
            listen pyis_klines;
            """)
            while self.connected:
                time.sleep(int(self.s.common.config['database']['idle']))
                self.curs.execute("select 1")
                notifies = self.curs.notifies()
                if not notifies: continue
                for notify in notifies:
                    notify = notify[0].split('pyis_')[-1]
                    print notify
                    if notify == 'rehash': self.s.rehash()
                    elif notify == 'klines': self.get_klines()
        except:
            excDEBUG("classes.database.notify", sys.exc_info())
            self.connected = False
            
    def get_klines(self):
        """
        Get Klines from database and store them.
        """
        if not self.query("select * from pyis_klines"): return
        data = self.curs.dictfetchall()
        self.s.kline = {}
        for kline in data:
            mask = kline['mask']
            del kline['mask']
            self.s.kline[mask] = kline
            
    def query(self, sql):
        try:
            self.curs.execute(sql)
            return 1
        except:
            excDEBUG("classes.database.query", sys.exc_info())
            return 0
        
    def insert(self, table, *values):
        vals = ""
        for v in values:
            if type(v) is int: vals += "%d" % v
            else: vals += "'%s'" % v.replace("'", "\\'")
            vals += ', '
        if vals: vals = vals[:-2]
        sql = "insert into pyis_%s VALUES (%s)" % (table, vals)
        self.query(sql)
        
    def delete(self, table, **where):
        if where: whr = ' WHERE '
        else: whr = ''
        for k, v in where.items():
            whr += k+'='
            if type(v) is int: whr += str(v)
            else: whr += "'%s'" % v.replace("'", "\\'")
            whr += ', '
        if whr: whr = whr[:-2]
        sql = "delete from pyis_%s%s" % (table, whr)
        self.query(sql)
