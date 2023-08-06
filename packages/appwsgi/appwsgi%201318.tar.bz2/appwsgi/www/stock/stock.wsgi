# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.session import Session
from appwsgi.db import Db

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read().decode('utf-8'))
    s = Session(db,environ.get('HTTP_COOKIE',''),v['gid'])
    response('200 OK', [('Content-type', 'text/plain;charset=utf-8'), ('Set-Cookie', s.COOKIE)])

    if s.GID:
        if   v['cmd']=='select': db.execute("SELECT * FROM shop_products WHERE pid LIKE ? AND description LIKE ? AND price LIKE ? OR qty <= ?",('%'+v['pid']+'%','%'+v['txt']+'%','%'+v['price']+'%',v['qty']))
        elif v['cmd']=='insert': 
            db.execute("INSERT INTO shop_products VALUES (?,?,?,?)",(v['pid'],v['txt'],v['price'],v['qty']))
            restock(db)
        elif v['cmd']=='update': 
            db.execute("UPDATE shop_products SET description=?, price=?, qty=? WHERE pid=?",(v['txt'],v['price'],v['qty'],v['pid']))
            restock(db)
        elif v['cmd']=='delete': 
            db.execute("DELETE FROM shop_products WHERE pid=?",(v['pid'],))
            restock(db)

    j = '{"cmd":"'+str(v['cmd'])+'",\n'
    j+= ' "sid":"'+str(s.SID)+'",\n'
    j+= ' "exp":"'+str(s.EXP)+'",\n'
    j+= ' "uid":"'+str(s.UID)+'",\n'
    j+= ' "gid":"'+str(s.GID)+'",\n'
    if db.LASTROWID: j+='"row":"'+db.LASTROWID+'",\n'
    if db.ERROR: j+='"error":"'+db.ERROR+'",\n'
    j+= ' "rec":'+db.json()+',\n'
    j+= ' "des":'+db.jdes()+'}'
    return [j.encode('utf-8')]

def restock(db):    
    db.execute('SELECT products,oid FROM shop_orders WHERE bid=2 OR bid=3 ORDER BY time ASC',())
    f = db.fetch()
    for r in f:
        rec,oid=r
        p = loads(rec)
        b = 3
        for i in p:
            v=i[0]
            db.execute('SELECT qty FROM shop_products WHERE pid=?',(v,))
            try: stock=db.fetch()[0][0]
            except: stock=0
            if stock < 0: b=2
        db.execute('UPDATE shop_orders SET bid=? WHERE oid=?',(b,oid))

