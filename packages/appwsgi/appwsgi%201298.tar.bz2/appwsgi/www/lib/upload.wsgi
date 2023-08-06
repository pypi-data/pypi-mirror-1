# Copyright(c) gert.cuykens@gmail.com
from db import Db
from session import Session
from re import search,DOTALL

def application(environ, response):
    db = Db()
    session = Session(db,environ['QUERY_STRING'],'guest')
    response('200 OK', [('Content-type', 'text/plain;charset=utf-8'), ('Set-Cookie', session.COOKIE)])
    if not session.GID: return ['access denied!']
    s = environ['wsgi.input'].read().decode('latin1')
    b = environ['CONTENT_TYPE'].split('boundary=')[1]
    p = search(b+r'.*?Content-Type: application/octet-stream\r\n\r\n(.*?)\r\n--'+b,s,DOTALL).group(1)
    p = p.encode('latin1')
    db.execute('UPDATE users SET picture=? WHERE uid=?', (p, session.UID))
    if db.ERROR: return ['{"error":"'+str(db.ERROR)+'"}']
    else: return [session.COOKIE]

