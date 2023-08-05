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
        db.execute('SELECT sid FROM register WHERE sid=%s',(sid))
        if db.ROWCOUNT==0: break
    return sid

def set(db,cmd,u,p):
    if  cmd == 'login':
        s = new(db)
        d = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()+3600))
        t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()+3600))
        db.execute("INSERT INTO register VALUES (%s,%s,'','','','','','',0,1,%s,NOW())",(u,p,s))
        db.ERROR=''
        db.execute('UPDATE register SET sid=%s, exp=%s WHERE email=%s AND pwd=%s',(s,t,u,p))
        return "SID="+s+"; expires="+d+"; path=/"
    elif cmd == 'logout':
        m=re.compile(r'SID=(.*?)(?:;|$)').search(p)
        try: s=m.group(1)
        except: s=''
        d = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()-1))
        t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()-1))
        db.execute('UPDATE register SET sid=NULL, exp=%s WHERE sid=%s',(t,s))
        return "SID=; expires="+d+"; path=/"
    elif cmd == 'timeout':
        m=re.compile(r'SID=(.*?)(?:;|$)').search(p)
        try: s=m.group(1)
        except: s=''
        d = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()+3600))
        t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()+3600))
        db.execute('UPDATE register SET exp=%s WHERE sid=%s',(t,s))
        return "SID="+s+"; expires="+d+"; path=/"
    else:
        m=re.compile(r'SID=(.*?)(?:;|$)').search(p)
        try: s=m.group(1)
        except: s=''
        d = strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(time()+3600))
        t = strftime('%Y-%m-%d %H:%M:%S', gmtime(time()))
        db.execute('UPDATE register SET '+cmd+'=%s WHERE sid=%s AND exp>%s',(u,s,t))
        return "SID="+s+"; expires="+d+"; path=/"

def get(db,cmd,c):
    m=re.compile(r'SID=(.*?)(?:;|$)').search(c)
    try:
        s=m.group(1)
        t=strftime('%Y-%m-%d %H:%M:%S', gmtime(time()))
        db.execute('SELECT '+cmd+' FROM register WHERE sid=%s AND exp>%s',(s,t))
        f=db.fetch()
        if  f: return f[0][0]
    except: return ''
