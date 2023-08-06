# Copyright(c) gert.cuykens@gmail.com

import os, time
from xmlframe import read

def application(environ, response):
    xml = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    v   = read(xml)
    a   = v['fn'][0]+v['ln'][0:6]
    a   = a.lower()

    xml  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    xml += "<root>"
    xml += "<![CDATA["

    ssh_pipe = os.popen("ssh root@127.0.0.1 'echo \"<span>The server excecutes a ssh command to the unix server to create user "+a+"<span>\";'")
    xml += ssh_pipe.read()
    ssh_pipe.flush()
    ssh_pipe.close()

    xml += "]]>"
    xml += "</root>"

    response('200 OK',[('Content-type','text/xml'),('Content-Length', str(len(xml)))])
    return [xml]

