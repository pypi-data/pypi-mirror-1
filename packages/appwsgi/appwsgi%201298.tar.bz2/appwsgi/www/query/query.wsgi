# Copyright(c) gert.cuykens@gmail.com
from json import loads
from db import Db

def application(environ, response):
    response('200 OK', [('Content-type', 'text/plain;charset=utf-8')])
    v = loads(environ['wsgi.input'].read().decode('utf-8'))
    db = Db()
    db.execute(v['sql'])
    j = '{"sql":"'+v['sql']+'",\n'
    j+= ' "rec":'+db.json()+',\n'
    j+= ' "des":'+db.jdes()+'}'
    return [j]

