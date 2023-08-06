# Copyright(c) gert.cuykens@gmail.com
from xmlframe import read,write
from db import Db

def application(environ, response):
    xml = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    x   = read(xml)
    db  = Db('localhost',x['user'],x['password'],x['database'])
    db.execute(x['sql'],())
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<root>\n'
    xml+= ' <sql>'+Db.escape(x['sql'])+'</sql>\n'
    xml+= write(db)
    xml+= '</root>'
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', str(len(xml)))])
    return [xml]

