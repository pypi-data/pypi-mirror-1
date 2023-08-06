# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.db import Db
from appwsgi.session import Session

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read().decode('utf-8'))
    if v['cmd']=='login':
        s = Session.login(db,v['uid'],v['pwd'])
        s = Session(db,s,v['gid'])
    else:
        s = Session(db,environ.get('HTTP_COOKIE',''),v['gid'])
        s.logout()
    response('200 OK', [('Content-type', 'text/plain;charset=utf-8'), ('Set-Cookie', s.COOKIE)])    
    j = '{"cmd":"'+str(v['cmd'])+'",\n'
    j+= ' "sid":"'+str(s.SID)+'",\n'
    j+= ' "exp":"'+str(s.EXP)+'",\n'
    j+= ' "uid":"'+str(s.UID)+'",\n'
    j+= ' "gid":"'+str(s.GID)+'",\n'
    j+= ' "rec":'+db.json()+'}'
    return [j]

