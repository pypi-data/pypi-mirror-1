# Copyright(c) gert.cuykens@gmail.com

from xmlframe import xmlframe
from order import restock

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    doc = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    data,size,sid = xmlframe(doc,sid,any)
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', size),('Set-Cookie', sid)])
    return [data]

def any(db,v):
    if   v['cmd']=='select': db.execute("SELECT * FROM shop_products WHERE pid LIKE %s AND description LIKE %s AND price LIKE %s OR qty <= %s",('%'+v['pid']+'%','%'+v['txt']+'%','%'+v['price']+'%',v['qty']))
    elif v['cmd']=='insert': 
        db.execute("INSERT shop_products VALUE (0,%s,%s,%s)",(v['txt'],v['price'],v['qty']))
        restock(db)
    elif v['cmd']=='update': 
        db.execute("UPDATE shop_products SET description=%s, price=%s, qty=%s WHERE pid=%s",(v['txt'],v['price'],v['qty'],v['pid']))
        restock(db)
    elif v['cmd']=='delete': 
        db.execute("DELETE FROM shop_products WHERE pid=%s",(v['pid']))
        restock(db)
