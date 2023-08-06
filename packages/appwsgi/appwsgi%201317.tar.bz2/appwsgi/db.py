# Copyright(c) gert.cuykens@gmail.com
import sqlite3
import os, sys

class Db(object):
    ERROR       = None
    LASTROWID   = None
    DESCRIPTION = None
    ROWCOUNT    = 0
    AUTOCOMMIT  = True
   
    def __init__(self):
        self.__db = self.connect()
        self.__cs = self.__db.cursor()
	
    def connect(self):
        try:
            cn = sqlite3.connect(os.path.join(os.path.dirname(__file__),"sqlite/www.db"))
            return cn
        except sqlite3.OperationalError as e:
            self.ERROR = "Connect error " + e.args[0]
            
    def execute(self,sql,v=None):
        print ((sql, v), file = sys.stderr)
        try:
            if v: self.__cs.execute(sql,v)
            else: self.__cs.execute(sql)
            self.DESCRIPTION=self.__cs.description
            self.ROWCOUNT=self.__cs.rowcount
            self.LASTROWID=self.__cs.lastrowid
            if self.AUTOCOMMIT == True : self.__db.commit()
        except sqlite3.Error as e:
            self.ERROR = "Execute error " + e.args[0]
            print ((e.args[0]), file = sys.stderr)

    def commit(self):
        try:
            self.__db.commit();
        except sqlite3.Error as e:
            self.ERROR = "Commit error " + e.args[0]
   
    def rollback(self):
        try:
            self.__db.rollback();
        except sqlite3.Error as e:
            self.ERROR = "Rollback error " + e.args[0]

    def fetch(self):
        try:
            data = self.__cs.fetchall()
            print (data, file = sys.stderr)
            return data
        except sqlite3.Error as e:
            self.ERROR = "Fetch error " + e.args[0]
            print ((e.args[0]), file = sys.stderr)
            return None

    def jdes(self):
        j = '['
        if self.DESCRIPTION:
            for i in self.DESCRIPTION:
                j+= '"'+str(i[0]).replace('"','\\"')+'",'
            j = j[0:-1]
        j+= ']'
        return j

    def json(self):
        f = self.fetch()
        j = '['
        if f:
            for r in f:
                j+= '['
                for i in r:
                    j+= '"'+str(i).replace('"','\\"')+'",'
                j = j[0:-1]
                j+= '],'
            j = j[0:-1]
        j+= ']'
        return j

    def __del__(self):
        try:
            self.__cs.close()
        except sqlite3.Error as e:
            self.ERROR = "Close error " + e.args[0]
        finally:
            self.__db.close()

