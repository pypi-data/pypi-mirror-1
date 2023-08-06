# Copyright(c) gert.cuykens@gmail.com
import MySQLdb

class Db(object):
    
    def __init__(self,server='localhost',user='root',password='root',database='www'):
        self.ERROR       = None
        self.LASTROWID   = None
        self.INSERTID    = None
        self.DESCRIPTION = None
        self.ROWCOUNT    = 0
        self.AUTOCOMMIT  = True
        self.__db        = self.connect(server,user,password,database)
        self.__cs        = self.__db.cursor()
	
    def connect(self,server,user,password,database):
        try:
            cn = MySQLdb.connect(server,user,password,database)
        except MySQLdb.OperationalError, e:
            self.ERROR = "Error %d: %s" % (e.args[0], e.args[1])
        return cn

    def execute(self,sql,v=()):
        try:
            self.__cs.execute(sql,v)
            self.DESCRIPTION=self.__cs.description
            self.ROWCOUNT=self.__cs.rowcount
            self.LASTROWID=self.__cs.lastrowid
            self.INSERTID=self.__db.insert_id()
            if self.AUTOCOMMIT == True : self.__db.commit()
        except AttributeError:
            pass
        except MySQLdb.Error, e:
            self.ERROR = "Error %d: %s" % (e.args[0], e.args[1])

    def commit(self):
        try:
            self.__db.commit();
        except AttributeError:
            pass
        except MySQLdb.Error, e:
            self.ERROR = "Error %d: %s" % (e.args[0], e.args[1])
   
    def rollback(self):
        try:
            self.__db.rollback();
        except AttributeError:
            pass
        except MySQLdb.Error, e:
            self.ERROR = "Error %d: %s" % (e.args[0], e.args[1])

    def fetch(self):
        try:
            data = self.__cs.fetchall()
            return data
        except:
            return None

    @classmethod
    def escape(cls,v):
        return MySQLdb.string_literal(v)

    def __del__(self):
        try:
            self.__cs.close()
        except:
            pass
        finally:
            self.__db.close()

