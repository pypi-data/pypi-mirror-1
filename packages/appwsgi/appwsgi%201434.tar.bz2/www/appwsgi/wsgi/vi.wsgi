# Copyright(c) gert.cuykens@gmail.com
from os import path
from json import loads
from appwsgi.session import Session
from appwsgi.db import Db

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8'))
    s = Session(db,environ.get('HTTP_COOKIE',''),v['gid'])

    if not s.GID == 'admin':
        j = '{"error":"Access denied!"}'
        j = j.encode('utf-8')
        response('200 OK', [('Content-type', 'text/javascript;charset=utf-8'), ('Content-Length', str(len(j))), ('Set-Cookie', s.COOKIE)])
        return [j]
    
    if v['cmd'] == 'write':
        with open(path.join(path.dirname(__file__),'../www/vi/vi.txt'), 'w') as f:
            f.write(v['txt'])

    j = '{"txt":"'
    with open(path.join(path.dirname(__file__),'../www/vi/vi.txt'), 'r') as f:
         for line in f:
             j += line
    j += '"}'

    j = j.encode('utf-8')
    response('200 OK', [('Content-type', 'text/javascript;charset=utf-8'), ('Content-Length', str(len(j))), ('Set-Cookie', s.COOKIE)])
    return [j]

