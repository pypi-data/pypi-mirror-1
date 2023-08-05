# Copyright(c) gert.cuykens@gmail.com

import MySQLdb 

class MySql(object):
    
    def __init__(self,server='localhost',user='root',password='root',database='www'):
        self.ERROR       = None
        self.LASTROWID   = None
        self.INSERTID    = None
        self.DESCRIPTION = None
        self.ROWCOUNT    = 0
        try:
            self.__db__=MySQLdb.connect(server,user,password,database)
            self.__cs__=self.__db__.cursor()
        except MySQLdb.OperationalError, e:
            self.ERROR = "Error %d: %s" % (e.args[0], e.args[1])

    def execute(self,sql,v):
        try:
            self.__cs__.execute(sql,v)
            self.DESCRIPTION=self.__cs__.description
            self.ROWCOUNT=self.__cs__.rowcount
            self.LASTROWID=self.__cs__.lastrowid
            self.INSERTID=self.__db__.insert_id()
            self.__db__.commit()
        except AttributeError:
            pass
        except MySQLdb.Error, e:
            self.ERROR = "Error %d: %s" % (e.args[0], e.args[1])

    def fetch(self):
        try:
            data = self.__cs__.fetchall()
            return data
        except:
            return None

    @staticmethod
    def escape(v):
        return MySQLdb.string_literal(v)

    def __del__(self):
        try:
            self.__cs__.close()
        except:
            pass
        finally:
            self.__db__.close()

