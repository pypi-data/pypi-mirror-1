# Copyright(c) gert.cuykens@gmail.com
from db import Db
from session import Session
from re import search,DOTALL

def application(environ, response):
    db = Db()
    c = "SID="+environ['QUERY_STRING']
    session = Session(db,c,'guest')
    response('200 OK', [('Content-type', 'text/xml'), ('Set-Cookie', session.COOKIE)])
    if not session.GID : return []
    #l = int(environ.get('CONTENT_LENGTH', '0'))
    #print('LENGTH=', l, file=environ['wsgi.errors'])
    s = environ['wsgi.input'].read()
    #print('TYPE=', s, file=environ['wsgi.errors'])
    #print('DATA=', s, file=environ['wsgi.errors']) 
    s = s.decode('latin1')
    #print('STRING=', s, file=environ['wsgi.errors'])
    b = environ['CONTENT_TYPE'].split('boundary=')[1]
    #print('STRING=', b, file=environ['wsgi.errors'])
    p = search(b+r'.*?Content-Type: application/octet-stream\r\n\r\n(.*?)\r\n--'+b,s,DOTALL).group(1)
    db.execute('UPDATE users SET picture=? WHERE uid=?',(p.encode('latin1'),session.UID))
    response('200 OK', [('Content-type', 'text/json')])
    return ['{"error":"'+str(db.ERROR)+'"}']

