# Copyright(c) gert.cuykens@gmail.com
from frame import Frame
from session import Session
from db import Db
from xml.dom import minidom

def application(environ, response):
    cookie = environ.get('HTTP_COOKIE','')
    document = environ['wsgi.input'].read()
    db = Db()
    v = Frame.read(document)
    s = Session(db,cookie,v['gid'])

    if s.GID=='guest':
        if   v['cmd']=='list'  : db.execute("SELECT uid,oid,bid,time FROM shop_orders WHERE uid=?",(v['uid'],))
        elif v['cmd']=='name'  : db.execute("SELECT uid,name,adress,city,country,phone FROM users WHERE uid=?",(v['uid'],))
        elif v['cmd']=='cart'  : db.execute("SELECT products FROM shop_orders WHERE oid=? AND uid=?",(v['oid'],v['uid'],))
        elif v['cmd']=='find'  : db.execute("SELECT * FROM shop_products WHERE description LIKE ?",('%'+v['pna']+'%',))
        elif v['cmd']=='pid'   : db.execute("SELECT * FROM shop_products WHERE pid=?",(v['pid'],))
        elif v['cmd']=='status': db.execute("SELECT * FROM shop_status")
        elif v['cmd']=='stats' : db.execute("SELECT * FROM shop_orders WHERE bid=? AND uid=?",(v['bid'],v['uid']))

        elif v['cmd']=='insert': 
             db.execute("INSERT INTO shop_orders (products,uid,bid,time) VALUES (?,?,?,DATETIME('NOW'))",(v['rec'],v['uid'],3))
             oid=db.LASTROWID
             insert(db,v['rec'],oid)
             db.LASTROWID=oid

        #elif v['cmd']=='update':
             #update(db,v['rec'],v['oid']) 
             #db.execute("UPDATE shop_orders SET products=? WHERE oid=? AND uid=?",(v['rec'],v['oid'],v['uid']))
             #restock(db)

        #elif v['cmd']=='remove': 
             #remove(db,v['oid'])
             #db.execute("DELETE FROM shop_orders WHERE oid=? AND uid=?",(v['oid'],v['uid']))
             #restock(db)

    if s.GID=='admin':
        if   v['cmd']=='list'  : db.execute("SELECT uid,oid,bid,time FROM shop_orders WHERE uid=?",(v['uida'],))
        elif v['cmd']=='name'  : db.execute("SELECT uid,name,adress,city,country,phone FROM users WHERE name LIKE ?",('%'+v['una']+'%',))
        elif v['cmd']=='cart'  : db.execute("SELECT products FROM shop_orders WHERE oid=?",(v['oid'],))
        elif v['cmd']=='find'  : db.execute("SELECT * FROM shop_products WHERE description LIKE ?",('%'+v['pna']+'%',))
        elif v['cmd']=='pid'   : db.execute("SELECT * FROM shop_products WHERE pid=?",(v['pid'],))
        elif v['cmd']=='status': db.execute("SELECT * FROM shop_status")
        elif v['cmd']=='stats' : db.execute("SELECT * FROM shop_orders WHERE bid=?",(v['bid'],))   
        
        elif v['cmd']=='insert':
             db.execute("INSERT INTO shop_orders (products,uid,bid,time) VALUES (?,?,?,DATETIME('NOW'))",(v['rec'],v['uida'],3))
             oid=db.LASTROWID
             insert(db,v['rec'],oid)
             db.LASTROWID=oid

        elif v['cmd']=='update':
             update(db,v['rec'],v['oid'])
             db.execute("UPDATE shop_orders SET products=?, uid=? WHERE oid=?",(v['rec'],v['uida'],v['oid']))
             restock(db)

        elif v['cmd']=='remove':
             remove(db,v['oid'])
             db.execute("DELETE FROM shop_orders WHERE oid=?",(v['oid'],))
             restock(db)

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml+= '<root>\n'
    xml+= ' <cmd>'+str(v['cmd'])+'</cmd>\n'
    xml+= ' <gid>'+str(s.GID)+'</gid>\n'
    xml+= ' <uid>'+str(s.UID)+'</uid>\n'
    xml+= ' <sid>'+str(s.SID)+'</sid>\n'
    xml+= ' <exp>'+str(s.EXP)+'</exp>\n'
    xml+= Frame.write(db)
    xml+= '</root>'

    response('200 OK', [('Content-type', 'text/xml'), ('Set-Cookie', s.COOKIE)])
    return [xml]

def insert(db,doc,oid):
    document = minidom.parseString(doc)
    status=3
    for i,pid in enumerate(document.getElementsByTagName('pid')):
        p=pid.childNodes[0].nodeValue
        q=document.getElementsByTagName('qty')[i].childNodes[0].nodeValue
        db.execute("UPDATE shop_products SET qty=qty-? WHERE pid=?",(q,p))
        db.execute("SELECT qty FROM shop_products WHERE pid=?",(p,))
        stock=int(db.fetch()[0][0])
        if stock < 0: status=2
    db.execute("UPDATE shop_orders SET bid=? WHERE oid=?",(status,oid))

def update(db,doc,oid):
    db.execute("SELECT products FROM shop_orders WHERE oid=?",(oid,))
    document = minidom.parseString(db.fetch()[0][0])
    documenn = minidom.parseString(doc)
    status=3
    for j,pn in enumerate(documenn.getElementsByTagName('pid')):
        p=pn.childNodes[0].nodeValue
        q=documenn.getElementsByTagName('qty')[j].childNodes[0].nodeValue
        u=bool(1)
        for i,pid in enumerate(document.getElementsByTagName('pid')):
            if p == pid.childNodes[0].nodeValue: u = bool(0)
        if u : db.execute("UPDATE shop_products SET qty=qty-? WHERE pid=?",(q,p))
        db.execute("SELECT qty FROM shop_products WHERE pid=?",(p,))
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
        if q != 0: db.execute("UPDATE shop_products SET qty=qty+? WHERE pid=?",(q,p))
        db.execute("SELECT qty FROM shop_products WHERE pid=?",(p,))
        stock=int(db.fetch()[0][0])
        if stock < 0: status=2
    db.execute("UPDATE shop_orders SET bid=? WHERE oid=?",(status,oid))

def remove(db,oid):
    db.execute("SELECT products FROM shop_orders WHERE oid=?",(oid,))
    document = minidom.parseString(db.fetch()[0][0])
    for i,pid in enumerate(document.getElementsByTagName('pid')):
        p=pid.childNodes[0].nodeValue
        q=document.getElementsByTagName('qty')[i].childNodes[0].nodeValue
        db.execute("UPDATE shop_products SET qty=qty+? WHERE pid=?",(q,p))
    db.execute("UPDATE shop_orders SET bid=1 WHERE oid=?",(oid,))

def restock(db):    
    db.execute("SELECT products,oid FROM shop_orders WHERE bid=2 OR bid=3 ORDER BY time ASC",())
    f = db.fetch()
    for r in f:
        doc,oid=r
        document = minidom.parseString(doc)
        status = 3
        for i,pid in enumerate(document.getElementsByTagName('pid')):
            p=pid.childNodes[0].nodeValue
            db.execute("SELECT qty FROM shop_products WHERE pid=?",(p,))
            try: stock=int(db.fetch()[0][0])
            except: stock=0
            if stock < 0: status=2
        db.execute("UPDATE shop_orders SET bid=? WHERE oid=?",(status,oid))

