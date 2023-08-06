# Copyright(c) gert.cuykens@gmail.com
from json import loads
from session import Session
from db import Db
from os import path

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read().decode('utf-8'))
    s = Session(db,environ.get('HTTP_COOKIE',''),v['gid'])
    response('200 OK', [('Content-type', 'text/plain;charset=utf-8'), ('Set-Cookie', s.COOKIE)])
    if not s.GID == 'admin':
        j = '{"error":"Access denied!"}'
        return [j]
    if v['cmd'] == 'write':
        with open(path.join(path.dirname(__file__),'vi.txt'), 'w') as f:
            f.write(v['txt'])
    j = '{"txt":"'
    with open(path.join(path.dirname(__file__),'vi.txt'), 'r') as f:
         for line in f:
             j += line
    j += '"}'
    return [j]

