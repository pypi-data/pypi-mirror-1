# Copyright(c) gert.cuykens@gmail.com

from session import get
from db import MySql

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    db = MySql()
    g = get('gid',db,sid)

    ERROR = ''
    if  environ['mod_wsgi.process_group'] != '' and g == 2:
        import signal, os
        os.kill(os.getpid(), signal.SIGINT)
    else:
        ERROR = environ['mod_wsgi.process_group']+' security level '+str(g)

    xml  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    xml += "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">"
    xml += "<!-- Copyright(c) gert.cuykens@gmail.com -->"
    xml += "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\">"
    xml += " <head>"
    xml += "  <title>reload</title>"
    xml += " </head>"
    xml += " <body>"
    if ERROR: xml+="<p>"+ERROR+"</p>"
    else: xml+="<script>document.location='/'</script>"
    xml += " </body>"
    xml += "</html>"

    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', str(len(xml)))])
    return [xml]

