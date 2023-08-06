# Copyright(c) gert.cuykens@gmail.com
from frame import Frame
from db import Db

def application(environ, response):
    document = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    v = Frame.read(document)
    db = Db()
    db.execute(v['sql'],())
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<root>\n'
    xml+= ' <sql>'+v['sql']+'</sql>\n'
    xml+= Frame.write(db)
    xml+= '</root>'
    response('200 OK', [('Content-type', 'text/xml')])
    return [xml]

