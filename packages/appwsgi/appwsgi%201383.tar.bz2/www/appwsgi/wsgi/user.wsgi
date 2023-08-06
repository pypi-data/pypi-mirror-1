# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.session import Session
from appwsgi.db import Db

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8'))
    s = Session(db,environ.get('HTTP_COOKIE',''), v['gid'])

    if s.GID:
        if v['cmd']=='delete': 
            db.execute('DELETE FROM users WHERE uid=?',(s.UID,))
            db.execute('DELETE FROM sessions WHERE uid=?',(s.UID,)) # sqlite no foreign key yet
        elif v['cmd']=='update': db.execute('UPDATE users SET name=?, adress=?, city=?, country=?, phone=? WHERE uid=?',(v['name'],v['adress'],v['city'],v['country'],v['phone'],s.UID))
        elif v['cmd']=='passwd': db.execute('UPDATE sessions SET pwd=? WHERE sid=?',(v['pwd'],s.SID))
        elif v['cmd']=='email':
            db.TRANSACTION=True
            db.execute('UPDATE users SET uid=? WHERE uid=?',(v['uid'],s.UID))
            db.execute('UPDATE sessions SET uid=? WHERE sid=?',(v['uid'],s.SID))
            db.execute('UPDATE groups SET uid=? WHERE uid=?',(v['uid'],s.UID)) # at all foreign databases for manual uid update
            if db.ERROR == None: db.commit()
            else: db.rollback()
            db.execute('SELECT uid FROM sessions WHERE sid=?',(s.SID,))
        else: db.execute('SELECT uid,name,adress,city,country,phone FROM users WHERE uid=?',(s.UID,))
  
    j = '{"cmd":"'+str(v['cmd'])+'",\n'
    j+= ' "sid":"'+str(s.SID)+'",\n'
    j+= ' "exp":"'+str(s.EXP)+'",\n'
    j+= ' "uid":"'+str(s.UID)+'",\n'
    j+= ' "gid":"'+str(s.GID)+'",\n'
    j+= ' "rec":'+db.json()+'}'

    j = j.encode('utf-8')
    response('200 OK', [('Content-type', 'text/javascript;charset=utf-8'), ('Content-Length', str(len(j))), ('Set-Cookie', s.COOKIE)])
    return [j]
