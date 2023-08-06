# Copyright(c) gert.cuykens@gmail.com
from frame import Frame
from session import Session
from db import Db
from xml.dom import minidom

def application(environ, response):
    cookie = environ.get('HTTP_COOKIE','')
    document = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    db = Db()
    v = Frame.read(document)
    s = Session(db,cookie,v['gid'])

    if s.GID:
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

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml+= '<root>\n'
    xml+= ' <cmd>'+str(v['cmd'])+'</cmd>\n'
    xml+= ' <sid>'+str(s.SID)+'</sid>\n'
    xml+= ' <exp>'+str(s.EXP)+'</exp>\n'
    xml+= ' <uid>'+str(s.UID)+'</uid>\n'
    xml+= ' <gid>'+str(s.GID)+'</gid>\n'
    xml+= Frame.write(db)
    xml+= '</root>'

    response('200 OK', [('Content-type', 'text/xml'), ('Set-Cookie', s.COOKIE)])
    return [xml]

def restock(db):    
    db.execute("SELECT products,oid FROM shop_orders WHERE bid=2 OR bid=3 ORDER BY time ASC",())
    f = db.fetch()
    for r in f:
        doc,oid=r
        document = minidom.parseString(doc)
        status = 3
        for i,pid in enumerate(document.getElementsByTagName('pid')):
            p=pid.childNodes[0].nodeValue
            db.execute("SELECT qty FROM shop_products WHERE pid=%s",(p))
            try: stock=int(db.fetch()[0][0])
            except: stock=0
            if stock < 0: status=2
        db.execute("UPDATE shop_orders SET bid=%s WHERE oid=%s",(status,oid))

