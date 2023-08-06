# Copyright(c) gert.cuykens@gmail.com
from cgi import FieldStorage
from session import Session
from db import Db

def application(environ, response):
    cookie = "SID="+environ['QUERY_STRING']
    bin = FieldStorage(fp=environ['wsgi.input'], environ=environ)
    db = Db()
    session = Session(db,cookie,'guest')
    if bin:
       bin = bin.getfirst('Filedata')
       if  session.GID:
           db.execute('UPDATE users SET picture=%s WHERE uid=%s',(bin, session.UID))
           # print >> environ['wsgi.errors'], Db.escape(data)
           # f = open('/var/www/upload','w')
           # f.write(data.getfirst('Filedata'))
    
    xml  = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    xml += "<root>" + str(db.ERROR) + "</root>"

    response('200 OK', [('Content-type', 'text/xml'), ('Set-Cookie', session.COOKIE)])
    return [xml]

#mem = StringIO()
#input = self.environ['wsgi.input']
#length = int(self.environ["CONTENT_LENGTH"])
#while true:
#    remain = length - mem.tell()
#    if remain <= 0: break
#    chunk = input.read(min(65536, remain))
#    if not chunk: break
#    mem.write(chunk)
#data = mem.getvalue()
#mem.close()

