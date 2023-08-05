# Copyright(c) gert.cuykens@gmail.com

from xmlframe import xmlframe

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    doc = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    data,size,sid = xmlframe(doc,sid,any,user,admin)
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', size),('Set-Cookie', sid)])
    return [data]

def any(db,v):
    pass

def user(db,v):
    db.execute("SELECT * FROM shop_orders WHERE oid=%s AND uid=%s",(v['oid'],v['uid']))

def admin(db,v):
    db.execute("SELECT * FROM shop_orders WHERE oid=%s",(v['oid']))
    
