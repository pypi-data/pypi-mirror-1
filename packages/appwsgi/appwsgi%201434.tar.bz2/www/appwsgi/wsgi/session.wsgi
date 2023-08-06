# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.db import Db
from appwsgi.session import Session
from appwsgi.mail import mail

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8'))
    if v['cmd']=='login':
        s = Session.login(db,v['uid'],v['pwd'])
        s = Session(db,s,v['gid'])
    elif v['cmd']=='mailpasswd':
        db.execute('SELECT pwd FROM sessions WHERE uid=?',(v['uid'],)) 
        j=mail(v['uid'],'password',db.json())
        j=j.encode('utf-8')
        response('200 OK', [('Content-type', 'text/javascript;charset=utf-8'), ('Content-Length', str(len(j)))])
        return [j]       
    else:
        s = Session(db,environ.get('HTTP_COOKIE',''),v['gid'])
        s.logout()

    j = '{"cmd":"'+str(v['cmd'])+'",\n'
    j+= ' "sid":"'+str(s.SID)+'",\n'
    j+= ' "exp":"'+str(s.EXP)+'",\n'
    j+= ' "uid":"'+str(s.UID)+'",\n'
    j+= ' "gid":"'+str(s.GID)+'",\n'
    j+= ' "rec":'+db.json()+'}'

    j = j.encode('utf-8')
    response('200 OK', [('Content-type', 'text/javascript;charset=utf-8'), ('Content-Length', str(len(j))), ('Set-Cookie', s.COOKIE)])
    return [j]
