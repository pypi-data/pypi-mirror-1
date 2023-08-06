# Copyright(c) gert.cuykens@gmail.com
# Set-Cookie: NAME1=VALUE1; expires=Wednesday, 09-Nov-07 23:12:40 GMT; path=/; domain=DOMAIN_NAME; secure
# Cookie: NAME1=VALUE1; NAME2=VALUE2
  
import re
from time import strftime, gmtime, time
from random import random
from hashlib import sha1

def new(db):
    while 1:
        sid=str(sha1(str(random())).hexdigest())
        exp=strftime('%Y-%m-%d %H:%M:%S', gmtime(time()+3600))
        db.execute('SELECT sid FROM sessions WHERE sid=%s',(sid))
        if db.ROWCOUNT==0: break
    db.execute("INSERT INTO sessions VALUES (%s,%s)",(sid,exp))
    return sid

def set(db,cmd,u,p):
    if  cmd == 'login':
        d = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()+3600))
        s = new(db)
        db.execute("INSERT INTO register (sid, email, pwd) VALUES (%s,%s,%s)",(s,u,p))
        db.ERROR=''
        db.execute('UPDATE register SET sid=%s WHERE email=%s AND pwd=%s',(s,u,p))
        db.execute('DELETE FROM sessions USING sessions LEFT JOIN register ON register.sid = sessions.sid WHERE register.email IS NULL;')
        return "SID="+s+"; expires="+d+"; path=/"
    elif cmd == 'logout':
        m=re.compile(r'SID=(.*?)(?:;|$)').search(p)
        try: s=m.group(1)
        except: s=''
        d = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()-1))
        t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()-1))
        db.execute('UPDATE sessions SET exp=%s WHERE sid=%s',(t,s))
        return "SID=; expires="+d+"; path=/"
    elif cmd == 'timeout':
        m=re.compile(r'SID=(.*?)(?:;|$)').search(p)
        try: s=m.group(1)
        except: s=''
        d = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()+3600))
        t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()+3600))
        db.execute('UPDATE sessions SET exp=%s WHERE sid=%s',(t,s))
        return "SID="+s+"; expires="+d+"; path=/"
    else:
        m=re.compile(r'SID=(.*?)(?:;|$)').search(p)
        try: s=m.group(1)
        except: s=''
        d = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()+3600))
        t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()))
        db.execute('UPDATE register, sessions SET register.'+cmd+'=%s WHERE register.sid=%s AND sessions.exp>%s',(u,s,t))
        return "SID="+s+"; expires="+d+"; path=/"

def get(db,cmd,c):
    m=re.compile(r'SID=(.*?)(?:;|$)').search(c)
    try:
        s=m.group(1)
        t=strftime('%Y-%m-%d %H:%M:%S', gmtime(time()))
        db.execute('SELECT register.'+cmd+' FROM register, sessions WHERE register.sid=%s AND sessions.exp>%s GROUP BY register.sid',(s,t))
        f=db.fetch()
        if  f: return f[0][0]
    except: return ''

