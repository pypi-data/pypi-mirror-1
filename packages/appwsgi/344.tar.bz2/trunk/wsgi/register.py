# Copyright(c) gert.cuykens@gmail.com

from xmlframe import xmlframe

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    doc = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    data,size,sid = xmlframe(doc,sid,any)
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', size),('Set-Cookie', sid)])
    return [data]

def any(db,v):
    if   v['cmd']=='delete': db.execute('DELETE FROM register WHERE email=%s AND pwd=%s',(v['email'],v['pwd']))
    elif v['cmd']=='update': db.execute('UPDATE register SET pwd=%s, name=%s, adress=%s, city=%s, country=%s, phone=%s WHERE email=%s AND pwd=%s',(v['pwn'],v['name'],v['adress'],v['city'],v['country'],v['phone'],v['email'],v['pwd']))
    elif v['cmd']=='login' : db.execute('SELECT email,name,adress,city,country,phone FROM register WHERE email=%s AND pwd=%s',(v['email'],v['pwd']))

