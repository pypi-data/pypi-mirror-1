# Copyright(c) gert.cuykens@gmail.com
import sqlite3

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
        import os
        try:
            cn = sqlite3.connect(os.path.join(os.path.dirname(__file__),"www.db"))
            return cn
        except sqlite3.OperationalError as e:
            self.ERROR = "Connect error " + e.args[0]
            
    def execute(self,sql,v=None):
        import sys
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
            return data
        except sqlite3.Error as e:
            self.ERROR = "Fetch error " + e.args[0]
            return None

    def __del__(self):
        try:
            self.__cs.close()
        except sqlite3.Error as e:
            self.ERROR = "Close error " + e.args[0]
        finally:
            self.__db.close()

