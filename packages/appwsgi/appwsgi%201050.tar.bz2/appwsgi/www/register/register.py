# Copyright(c) gert.cuykens@gmail.com
from frame import Frame
from session import Session
from db import Db

def application(environ, response):
    cookie = environ.get('HTTP_COOKIE','')
    document = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    db = Db()
    v = Frame.read(document)
    s = Session(db,cookie,v['gid'])

    if v['cmd']=='login': s.login(v['uid'],v['pwd'])
    elif v['cmd']=='logout': s.logout()

    if s.GID:
        if v['cmd']=='delete': db.execute('DELETE FROM users WHERE uid=?',(s.UID,))
        elif v['cmd']=='update': db.execute('UPDATE users SET name=?, adress=?, city=?, country=?, phone=? WHERE uid=?',(v['name'],v['adress'],v['city'],v['country'],v['phone'],s.UID))
        elif v['cmd']=='passwd': db.execute('UPDATE sessions SET pwd=? WHERE sid=?',(v['pwd'],s.SID))
        else: db.execute('SELECT uid,name,adress,city,country,phone FROM users WHERE uid=?',(s.UID,))
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml+= '<root>\n'
    xml+= ' <cmd>'+str(v['cmd'])+'</cmd>\n'
    xml+= ' <sid>'+str(s.SID)+'</sid>\n'
    xml+= ' <exp>'+str(s.EXP)+'</exp>\n'
    xml+= ' <uid>'+str(s.UID)+'</uid>\n'
    xml+= ' <gid>'+str(s.GID)+'</gid>\n'
    xml+= Frame.write(db)
    xml+= '</root>'

    response('200 OK', [('Content-type', 'text/xml'), ('Set-Cookie', s.COOKIE)])
    return [xml]

