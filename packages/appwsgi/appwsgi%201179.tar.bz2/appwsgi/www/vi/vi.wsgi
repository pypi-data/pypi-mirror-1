# Copyright(c) gert.cuykens@gmail.com
from json import loads
from session import Session
from db import Db
from os import path

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read().decode('latin1'))
    s = Session(db,environ.get('HTTP_COOKIE',''),v['gid'])
    response('200 OK', [('Content-type', 'text/plain')])

    if not s.GID == 'admin':
        j = '{"error":"Access denied!"}'
        return [j]

    if v['cmd'] == 'write':
        f = open(path.join(path.dirname(__file__),'vi.txt'), 'w')
        f.write(v['txt'])
        f.close()

    j = '{"txt":"'

    with open(path.join(path.dirname(__file__),'vi.txt'), 'r') as f:
         for line in f:
             j += line

    j += '"}'

    return [j]

