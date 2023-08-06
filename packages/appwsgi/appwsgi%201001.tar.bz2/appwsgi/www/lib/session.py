# Copyright(c) gert.cuykens@gmail.com
# Set-Cookie: NAME1=VALUE1; expires=Wednesday, 09-Nov-07 23:12:40 GMT; path=/; domain=DOMAIN_NAME; secure
# Cookie: NAME1=VALUE1; NAME2=VALUE2
from re import compile
from time import strftime, gmtime, time
from random import random
from hashlib import sha1

class Session(object):
    UID = None
    GID = None
    SID = None
    EXP = None
    COOKIE = ''

    def __init__(self,db,c,g):
        self.__db=db
        self.__g=g
        m = compile(r'SID=(.*?)(?:;|$)').search(c)
        if c: 
            s = m.group(1)
            self.secure(s)

    def login(self,u,p):
        t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()+3600))
        s = str(sha1(str(random())).hexdigest())
        
        self.__db.execute("INSERT INTO users (uid) VALUES (%s)",(u))
        self.__db.execute("INSERT INTO groups (uid, gid) VALUES (%s,'guest')",(u))
        self.__db.execute("INSERT INTO groups (uid, gid) VALUES (%s,'admin')",(u))
        self.__db.execute("INSERT INTO sessions (uid, pwd, sid, exp) VALUES (%s,%s,%s,%s)",(u,p,s,t))
        self.__db.ERROR = None

        self.__db.execute('UPDATE sessions SET sid=%s, exp=%s WHERE uid=%s AND pwd=%s',(s,t,u,p))
        self.secure(s)

    def secure(self,s):
        t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()))
        self.__db.execute('SELECT uid,sid,exp FROM sessions WHERE sid=%s AND exp>%s',(s,t))
        f=self.__db.fetch()
        if f:
            self.UID = f[0][0]
            self.SID = f[0][1]
            self.EXP = f[0][2]
        self.__db.execute('SELECT gid FROM groups WHERE uid=%s AND gid=%s',(self.UID,self.__g))
        f=self.__db.fetch()
        if f:
            self.GID = f[0][0]
            self.refresh()
        else: self.logout()

    def logout(self):
        d = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()-1))
        self.COOKIE = "SID=; expires="+d+"; path=/"
        self.EXP = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()-1))
        if self.SID: self.__db.execute('UPDATE sessions SET exp=%s WHERE sid=%s',(self.EXP,self.SID))
        self.SID = None
        self.EXP = None
        self.UID = None
        self.GID = None

    def refresh(self):
        d = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()+3600))  
        self.COOKIE = "SID="+self.SID+"; expires="+d+"; path=/" 
        self.EXP = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()+3600))
        self.__db.execute('UPDATE sessions SET exp=%s WHERE sid=%s ',(self.EXP,self.SID))

    def __del__(self):
        # t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()-3600000))
        # self.__db.execute('DELETE FROM sessions WHERE session.exp = %s',(t))
        pass

