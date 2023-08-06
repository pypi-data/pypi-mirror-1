# Copyright(c) gert.cuykens@gmail.com
from time import strftime, gmtime, time

class Session(object):
    SID = None
    UID = None
    GID = None
 
    def __init__(self,db,s,g):
        self.__db=db
        self.SID = s
        self.GID = g
        try: self.validate()
        except IndexError: self.GID='login'

    def validate(self):
        self.__db.execute('SELECT sessions.uid,exp FROM sessions INNER JOIN groups ON sessions.uid = groups.uid WHERE sid=? AND exp>? AND gid=?',(self.SID,strftime('%Y-%m-%d %H:%M:%S', gmtime(time())),self.GID))
        self.UID = self.__db.fetch()[0][0]
        self.__db.execute('UPDATE sessions SET exp=? WHERE sid=?',(strftime('%Y-%m-%d %H:%M:%S', gmtime(time()+3600)),self.SID))

