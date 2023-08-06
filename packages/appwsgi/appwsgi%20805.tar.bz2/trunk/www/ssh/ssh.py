# Copyright(c) gert.cuykens@gmail.com

import os, time, subprocess
from xmlframe import read

def application(environ, response):
    xml = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    v   = read(xml)
    a   = v['fn'][0]+v['ln'][0:6]
    a   = a.lower()

    xml  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    xml += "<root>"
    xml += "<![CDATA["

    proc = subprocess.Popen(['python', os.path.join(os.path.dirname(__file__),'../lib/proc.py') ], stdout=subprocess.PIPE)
    xml += proc.stdout.read()

    xml += "]]>"
    xml += "</root>"

    response('200 OK',[('Content-type','text/xml'),('Content-Length', str(len(xml)))])
    return [xml]

