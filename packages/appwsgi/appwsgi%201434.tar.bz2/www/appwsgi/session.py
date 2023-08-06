# Copyright(c) gert.cuykens@gmail.com
# Set-Cookie: NAME1=VALUE1; expires=Wednesday, 09-Nov-07 23:12:40 GMT; path=/; domain=DOMAIN_NAME; secure
# Cookie: NAME1=VALUE1; NAME2=VALUE2
from re import compile
from time import strftime, gmtime, time
from os import urandom
from binascii import hexlify

class Session(object):
    UID = None
    GID = None
    SID = None
    EXP = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()+3600))
    COOKIE = ''

    def __init__(self,db,c,g):
        self.__db=db
        self.GID=g
        m = compile(r'SID=(.*?)(?:;|$)').search(c)
        if c: self.SID = m.group(1)
        else: self.logout()
        t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()))
        self.__db.execute('SELECT sessions.uid,exp FROM sessions INNER JOIN groups ON sessions.uid = groups.uid WHERE sid=? AND exp>? AND gid=?',(self.SID,t,self.GID))
        f=self.__db.fetch()
        if f:
            self.UID = f[0][0]
            self.EXP = f[0][1]
            t = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()+3600))
            self.COOKIE = "SID="+self.SID+"; expires="+t+"; path=/"
            self.__db.execute('UPDATE sessions SET exp=? WHERE sid=? ',(self.EXP,self.SID))
        else: self.logout()

    def logout(self):
        t = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()-1))
        self.COOKIE = 'SID=logout; expires='+t+'; path=/'
        self.EXP = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()-1))
        if self.SID: 
            self.__db.execute('UPDATE sessions SET exp=? WHERE sid=?',(self.EXP,self.SID))
            self.SID = None
        self.UID = None
        self.GID = None

    @classmethod
    def key(cls,db):
        s = hexlify(urandom(8)).decode('ascii')
        db.execute('SELECT sid FROM sessions WHERE sid=?',(s,))
        f=db.fetch()
        if f: s=cls.key(db)
        return s
 
    @classmethod
    def login(cls,db,u,p):
        s=cls.key(db)
        t=strftime('%Y-%m-%d %H:%M:%S', gmtime(time()+3600))
        db.execute("INSERT INTO users (uid) VALUES (?)",(u,))
        db.execute("INSERT INTO groups (uid, gid) VALUES (?,'guest')",(u,))
        db.execute("INSERT INTO groups (uid, gid) VALUES (?,'admin')",(u,))
        db.execute("INSERT INTO sessions (uid, pwd, sid, exp) VALUES (?,?,?,?)",(u,p,s,t))
        db.ERROR = None
        db.execute('UPDATE sessions SET sid=?, exp=? WHERE uid=? AND pwd=?',(s,t,u,p))
        return 'SID='+s+';'

