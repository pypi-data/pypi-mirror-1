# Copyright(c) gert.cuykens@gmail.com
from re import search,DOTALL
from appwsgi.db import Db
from appwsgi.session import Session

def application(environ, response):
    db = Db()
    s = Session(db,environ['QUERY_STRING'],'guest')
    if not s.GID:
        j = 'access denied!'
        j = j.encode('utf-8')
        response('200 OK', [('Content-type', 'text/plain;charset=utf-8'), ('Content-Length', str(len(j))), ('Set-Cookie', s.COOKIE)])
        return [j]
    t = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('latin1')
    b = environ['CONTENT_TYPE'].split('boundary=')[1]
    p = search(b+r'.*?Content-Type: application/octet-stream\r\n\r\n(.*?)\r\n--'+b,t,DOTALL).group(1)
    p = p.encode('latin1')
    db.execute('UPDATE users SET picture=? WHERE uid=?', (p, s.UID))
    if db.ERROR:
        j = str(db.ERROR)
        j = j.encode('utf-8')
        response('200 OK', [('Content-type', 'text/plain;charset=utf-8'), ('Content-Length', str(len(j))), ('Set-Cookie', s.COOKIE)])
        return [j]
    else:
        j = s.COOKIE.encode('utf-8')
        response('200 OK', [('Content-type', 'text/plain;charset=utf-8'), ('Content-Length', str(len(j))), ('Set-Cookie', s.COOKIE)])
        return [j]
