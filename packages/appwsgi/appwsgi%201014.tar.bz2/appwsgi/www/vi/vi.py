# Copyright(c) gert.cuykens@gmail.com
from __future__ import with_statement
from frame import Frame
from session import Session
from db import Db

def application(environ, response):
    cookie = environ.get('HTTP_COOKIE','')
    document = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    db = Db()
    v = Frame.read(document)
    s = Session(db,cookie,v['gid'])
    
    response('200 OK', [('Content-type', 'text/xml')])
    xml  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    xml += "<root>\n"

    if not s.GID == 'admin':
        xml += " <error>Access denied!</error>\n"
        xml += "</root>"
        return [xml]

    if v['cmd'] == 'write':
        f = open('test.txt', 'w')
        f.write(xml['txt'])
        f.close()

    xml += "<![CDATA["

    with open('test.txt', 'r') as f:
         for line in f:
             xml += line

    xml += "]]>\n"
    xml += "</root>"

    return [xml]

