# Copyright(c) gert.cuykens@gmail.com

from xmlframe import xmlframe

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    doc = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    data,size,sid = xmlframe(doc,sid,any)
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', size),('Set-Cookie', sid)])
    return [data]

def any(db,v):
    if   v['cmd']=='update': db.execute("UPDATE register SET email=%s, name=%s, adress=%s, city=%s, country=%s, phone=%s, gid=%s WHERE uid=%s",(v['email'],v['name'],v['adress'],v['city'],v['country'],v['phone'],v['gida'],v['uida']))
    elif v['cmd']=='delete': db.execute("DELETE FROM register WHERE uid=%s",(v['uida']))
    elif v['cmd']=='select': db.execute("SELECT email,name,adress,city,country,phone,uid,gid FROM register WHERE email LIKE %s AND name LIKE %s AND adress LIKE %s AND city LIKE %s AND country LIKE %s AND phone LIKE %s OR gid=%s OR uid=%s",('%'+v['email']+'%','%'+v['name']+'%','%'+v['adress']+'%','%'+v['city']+'%','%'+v['country']+'%','%'+v['phone']+'%',v['gida'],v['uida']))
    
