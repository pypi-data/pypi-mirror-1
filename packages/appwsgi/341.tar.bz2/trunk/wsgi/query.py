# Copyright(c) gert.cuykens@gmail.com

from xmlframe import read,write
from db import MySql

def application(environ, response):
    doc = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    v   = read(doc)
    db  = MySql('localhost',v['user'],v['password'],v['database'])
    db.execute(v['sql'],())
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<root>\n'
    xml+= ' <sql>'+MySql.escape(v['sql'])+'</sql>\n'
    xml+= write(db)
    xml+= '</root>'
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', str(len(xml)))])
    return [xml]

