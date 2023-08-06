# Copyright(c) gert.cuykens@gmail.com
from frame import Frame
from session import Session
from db import Db
from os import path

def application(environ, response):
    cookie = environ.get('HTTP_COOKIE','')
    document = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    db = Db()
    v = Frame.read(document)
    s = Session(db,cookie,v['gid'])
    
    response('200 OK', [('Content-type', 'text/xml')])
    xml  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    xml += "<root>"

    if not s.GID == 'admin':
        xml += " <error>Access denied!</error>\n"
        xml += "</root>"
        return [xml]

    if v['cmd'] == 'write':
        f = open(path.join(path.dirname(__file__),'vi.txt'), 'w')
        f.write(v['txt'])
        f.close()

    xml += "<![CDATA["

    with open(path.join(path.dirname(__file__),'vi.txt'), 'r') as f:
         for line in f:
             xml += line

    xml += "]]>"
    xml += "</root>"

    return [xml]

