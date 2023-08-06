# Copyright(c) gert.cuykens@gmail.com
import sessions,cgi
from db import Db

def application(environ, response):
    sid  = environ['QUERY_STRING']
    bin = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    if bin:
       bin = bin.getfirst('Filedata')
       db = Db()
       sessions.set(db,'picture',bin,'SID='+sid)
       # print >> environ['wsgi.errors'], Db.escape(data)
       # print >> environ['wsgi.errors'], sid # NO COOKIE FROM FLASH
       # f = open('/var/www/upload','w')
       # f.write(data.getfirst('Filedata'))
    
    xml  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    xml += "<root>" + str(db.ERROR) + "</root>"

    response('200 OK',[('Content-type', 'text/html')])
    return [xml]
