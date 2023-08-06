# Copyright(c) gert.cuykens@gmail.com

from xmlframe import xmlframe
from xml.dom import minidom

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    doc = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    data,size,sid = xmlframe(doc,sid,any,user,admin)
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', size),('Set-Cookie', sid)])
    return [data]

def any(db,v):
    pass

def user(db,v):
    if   v['cmd']=='list'  : db.execute("SELECT uid,oid,bid,time FROM shop_orders WHERE uid=%s",(v['uid']))
    elif v['cmd']=='name'  : db.execute("SELECT uid,email,name,adress,city,country,phone FROM register WHERE uid=%s",(v['uid']))
    elif v['cmd']=='cart'  : db.execute("SELECT products FROM shop_orders WHERE oid=%s AND uid=%s",(v['oid'],v['uid']))
    elif v['cmd']=='find'  : db.execute("SELECT * FROM shop_products WHERE description LIKE %s",('%'+v['pna']+'%'))
    elif v['cmd']=='pid'   : db.execute("SELECT * FROM shop_products WHERE pid=%s",(v['pid']))
    elif v['cmd']=='status': db.execute("SELECT * FROM shop_status",())
    elif v['cmd']=='stats' : db.execute("SELECT * FROM shop_orders WHERE bid=%s AND uid=%s",(v['bid'],v['uid']))

    elif v['cmd']=='insert': 
         db.execute("INSERT INTO shop_orders (products,uid,bid,time) VALUES (%s,%s,%s,NOW())",(v['rec'],v['uid'],3))
         oid=db.INSERTID
         insert(db,v['rec'],oid)
         db.INSERTID=oid

    #elif v['cmd']=='update':
         #update(db,v['rec'],v['oid']) 
         #db.execute("UPDATE shop_orders SET products=%s WHERE oid=%s AND uid=%s",(v['rec'],v['oid'],v['uid']))
         #restock(db)

    #elif v['cmd']=='remove': 
         #remove(db,v['oid'])
         #db.execute("DELETE FROM shop_orders WHERE oid=%s AND uid=%s",(v['oid'],v['uid']))
         #restock(db)

def admin(db,v):
    if   v['cmd']=='list'  : db.execute("SELECT uid,oid,bid,time FROM shop_orders WHERE uid=%s",(v['uida']))
    elif v['cmd']=='name'  : db.execute("SELECT uid,email,name,adress,city,country,phone FROM register WHERE name LIKE %s",('%'+v['una']+'%'))
    elif v['cmd']=='cart'  : db.execute("SELECT products FROM shop_orders WHERE oid=%s",(v['oid']))
    elif v['cmd']=='find'  : db.execute("SELECT * FROM shop_products WHERE description LIKE %s",('%'+v['pna']+'%'))
    elif v['cmd']=='pid'   : db.execute("SELECT * FROM shop_products WHERE pid=%s",(v['pid']))
    elif v['cmd']=='status': db.execute("SELECT * FROM shop_status",())
    elif v['cmd']=='stats' : db.execute("SELECT * FROM shop_orders WHERE bid=%s",(v['bid']))   
    
    elif v['cmd']=='insert':
         db.execute("INSERT INTO shop_orders (products,uid,bid,time) VALUES (%s,%s,%s,NOW())",(v['rec'],v['uida'],3))
         oid=db.INSERTID
         insert(db,v['rec'],oid)
         db.INSERTID=oid

    elif v['cmd']=='update':
         update(db,v['rec'],v['oid'])
         db.execute("UPDATE shop_orders SET products=%s, uid=%s WHERE oid=%s",(v['rec'],v['uida'],v['oid']))
         restock(db)

    elif v['cmd']=='remove':
         remove(db,v['oid'])
         db.execute("DELETE FROM shop_orders WHERE oid=%s",(v['oid']))
         restock(db)

def insert(db,doc,oid):
    document = minidom.parseString(doc)
    status=3
    for i,pid in enumerate(document.getElementsByTagName('pid')):
        p=pid.childNodes[0].nodeValue
        q=document.getElementsByTagName('qty')[i].childNodes[0].nodeValue
        db.execute("UPDATE shop_products SET qty=qty-%s WHERE pid=%s",(q,p))
        db.execute("SELECT qty FROM shop_products WHERE pid=%s",(p))
        stock=int(db.fetch()[0][0])
        if stock < 0: status=2
    db.execute("UPDATE shop_orders SET bid=2 WHERE oid=%s",(oid))

def update(db,doc,oid):
    db.execute("SELECT products FROM shop_orders WHERE oid=%s",(oid))
    document = minidom.parseString(db.fetch()[0][0])
    documenn = minidom.parseString(doc)

    status=3

    for j,pn in enumerate(documenn.getElementsByTagName('pid')):
        p=pn.childNodes[0].nodeValue
        q=documenn.getElementsByTagName('qty')[j].childNodes[0].nodeValue
        u=bool(1)
        for i,pid in enumerate(document.getElementsByTagName('pid')):
            if p == pid.childNodes[0].nodeValue: u = bool(0)
        if u : db.execute("UPDATE shop_products SET qty=qty-%s WHERE pid=%s",(q,p))

        db.execute("SELECT qty FROM shop_products WHERE pid=%s",(p))
        stock=int(db.fetch()[0][0])
        if stock < 0: status=2

    for i,pid in enumerate(document.getElementsByTagName('pid')):
        p=pid.childNodes[0].nodeValue
        q=document.getElementsByTagName('qty')[i].childNodes[0].nodeValue
        u=0
        for j,pn in enumerate(documenn.getElementsByTagName('pid')):
            if  p == pn.childNodes[0].nodeValue:
                u=documenn.getElementsByTagName('qty')[j].childNodes[0].nodeValue
        q=int(q)-int(u)
        if q != 0: db.execute("UPDATE shop_products SET qty=qty+%s WHERE pid=%s",(q,p))
 
        db.execute("SELECT qty FROM shop_products WHERE pid=%s",(p))
        stock=int(db.fetch()[0][0])
        if stock < 0: status=2

    db.execute("UPDATE shop_orders SET bid=2 WHERE oid=%s",(oid))

def remove(db,oid):
    db.execute("SELECT products FROM shop_orders WHERE oid=%s",(oid))
    document = minidom.parseString(db.fetch()[0][0])
    for i,pid in enumerate(document.getElementsByTagName('pid')):
        p=pid.childNodes[0].nodeValue
        q=document.getElementsByTagName('qty')[i].childNodes[0].nodeValue
        db.execute("UPDATE shop_products SET qty=qty+%s WHERE pid=%s",(q,p))
    db.execute("UPDATE shop_orders SET bid=1 WHERE oid=%s",(oid))

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

