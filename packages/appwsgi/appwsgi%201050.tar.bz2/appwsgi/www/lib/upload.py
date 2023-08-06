# Copyright(c) gert.cuykens@gmail.com
from db import Db
from session import Session
from re import search,match,DOTALL

def application(environ, response):
    db = Db()
    cookie = "SID="+environ['QUERY_STRING']
    session = Session(db,cookie,'guest')
    response('200 OK', [('Content-type', 'text/xml'), ('Set-Cookie', session.COOKIE)])
    if not session.GID : return []
    s = environ['wsgi.input'].read().decode('latin1')
    b = environ['CONTENT_TYPE'].split('boundary=')[1]
    p = search(r'Content-Type: application/octet-stream\r\n\r\n(.*)\r\n--',s,DOTALL).group(1)
    db.execute('UPDATE users SET picture=? WHERE uid=?',(p.encode('latin1'),session.UID))
    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    xml+= "<root>"+str(db.ERROR)+"</root>"
    response('200 OK', [('Content-type', 'text/xml')])
    return [xml]

