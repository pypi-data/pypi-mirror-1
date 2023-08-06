# Copyright(c) gert.cuykens@gmail.com

import re,sessions
from db import Db

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    s   = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    q   = environ['QUERY_STRING']
    b   = environ['CONTENT_TYPE']
    b   = re.compile('boundary=(.*)').search(b).group(1)
    r   = re.compile(b+r"\r\n(.*?)\r\n(.*?)\r\n\r\n(.*?)\r\n--"+b, re.DOTALL)
    db  = Db()
    
    data=[]
    start=0
    while 1:
        m=r.search(s,start)
        if  m:
            data.append(m.group(3))
            start=m.end()-len(b)
        else: break
        
    if data: sessions.set(db,'picture',data[0],sid)

    xml  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    xml += "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml11.dtd\">"
    xml += "<!-- Copyright(c) gert.cuykens@gmail.com -->"
    xml += "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\">"
    xml += " <head>"
    xml += "  <title>upload</title>"
    xml += " </head>"
    xml += " <body>"
    xml += "  <p>"
    if db.ERROR: xml += db.ERROR
    else: xml += "<script>parent.document.getElementById('picture').src='../download/download.py?picture='+Math.random();document.location='upload.htm';</script>"
    xml += "   <a href=\"upload.htm\">upload</a>"
    xml += "  </p>"
    xml += " </body>"
    xml += "</html>"

    response('200 OK',[('Content-type', 'text/html'),('Content-Length', str(len(xml)))])
    return [xml]
