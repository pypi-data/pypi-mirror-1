# Copyright(c) gert.cuykens@gmail.com
import os, subprocess, cgi

def application(environ, response):
    xml  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    xml += "<root>"
    xml += "<![CDATA["

    proc = subprocess.Popen(['python', os.path.join(os.path.dirname(__file__),'../lib/proc.py') ], stdout=subprocess.PIPE)
    xml += cgi.escape(proc.stdout.read())

    xml += "]]>"
    xml += "</root>"

    response('200 OK', [('Content-type', 'text/xml')])
    return [xml]

