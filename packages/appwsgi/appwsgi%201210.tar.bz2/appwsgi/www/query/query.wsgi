# Copyright(c) gert.cuykens@gmail.com
from json import loads
from db import Db

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read().decode('latin1'))
    response('200 OK', [('Content-type', 'text/plain')])
    db.execute(v['sql'])
    j = '{"sql":"'+v['sql']+'",\n'
    j+= ' "rec":'+db.json()+',\n'
    j+= ' "des":'+db.jdes()+'}'
    return [j]

