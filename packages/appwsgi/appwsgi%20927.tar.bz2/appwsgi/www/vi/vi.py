# Copyright(c) gert.cuykens@gmail.com

from __future__ import with_statement
from xmlframe import read

def application(environ, response):
    xml = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    v   = read(xml)

    if  v['vi'] == 'write':
        f = open('test.txt', 'w')
        f.write(v['txt'])
        f.close()

    xml  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    xml += "<root>"
    xml += "<![CDATA["

    with open('test.txt', 'r') as f:
         for line in f:
             xml += line

    xml += "]]>"
    xml += "</root>"

    response('200 OK',[('Content-type','text/xml'),('Content-Length', str(len(xml)))])
    return [xml]
