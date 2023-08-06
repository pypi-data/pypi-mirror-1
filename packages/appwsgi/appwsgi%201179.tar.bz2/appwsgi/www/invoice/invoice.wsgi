# Copyright(c) gert.cuykens@gmail.com
from json import loads
from session import Session
from db import Db

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read().decode('latin1'))
    s = Session(db,environ.get('HTTP_COOKIE',''),v['gid'])
    response('200 OK', [('Content-type', 'text/plain'), ('Set-Cookie', s.COOKIE)])

    if s.GID=='guest':
        if   v['cmd']=='invoice': db.execute('SELECT * FROM shop_orders WHERE oid=? AND uid=?',(v['oid'],s.UID))
        elif v['cmd']=='comments': #CONCAT(IFNULL(comments,''),?) coalesce(comments,'')||?
             db.execute('UPDATE shop_orders SET comments=comments||?  WHERE oid=? AND uid=?',(v['com'],v['oid'],s.UID))
             db.execute('SELECT comments FROM shop_orders WHERE oid=? AND uid=?',(v['oid'],s.UID))
        elif v['cmd']=='stats': db.execute('SELECT * FROM shop_status')
        elif v['cmd']=='stock': db.execute('SELECT qty FROM shop_products WHERE pid=?',(v['pid'],))
        elif v['cmd']=='status':
             if v['bid'] == '1':
                 db.execute('SELECT products FROM shop_orders WHERE oid=? AND uid=?',(v['oid'],s.UID))
                 rec = loads(db.fetch()[0][0])
                 db.execute('UPDATE shop_orders SET bid=1 WHERE oid=? AND uid=?',(v['oid'],s.UID))
                 remove(db,rec)
             db.execute('SELECT bid FROM shop_orders WHERE oid=? AND uid=?',(v['oid'],s.UID))
                              
    if s.GID=='admin':
        if   v['cmd']=='invoice': db.execute("SELECT * FROM shop_orders WHERE oid=?",(v['oid'],))
        elif v['cmd']=='comments': #CONCAT(IFNULL(comments,''),?) coalesce(comments,'')||?
             db.execute('UPDATE shop_orders SET comments=comments||? WHERE oid=?',(v['com'],v['oid']))
             db.execute('SELECT comments FROM shop_orders WHERE oid=?',(v['oid'],))
        elif v['cmd']=='stats': db.execute('SELECT * FROM shop_status')
        elif v['cmd']=='stock': db.execute('SELECT qty FROM shop_products WHERE pid=?',(v['pid'],))
        elif v['cmd']=='status':
             if v['bid'] == '1':
                 db.execute('SELECT products FROM shop_orders WHERE oid=?',(v['oid'],))
                 rec = loads(db.fetch()[0][0])
                 db.execute('UPDATE shop_orders SET bid=1 WHERE oid=?',(v['oid'],))
                 remove(db,rec)
             else:
                 db.execute('SELECT bid FROM shop_orders WHERE oid=?',(v['oid'],))
                 if db.fetch()[0][0] != 1: db.execute('UPDATE shop_orders SET bid=? WHERE oid=?',(v['bid'],v['oid']))
             db.execute('SELECT bid FROM shop_orders WHERE oid=?',(v['oid'],))

    j = '{"cmd":"'+str(v['cmd'])+'",\n'
    j+= ' "gid":"'+str(s.GID)+'",\n'
    j+= ' "uid":"'+str(s.UID)+'",\n'
    j+= ' "sid":"'+str(s.SID)+'",\n'
    j+= ' "exp":"'+str(s.EXP)+'",\n'
    j+= ' "rec":'+db.json()+',\n'
    j+= ' "des":'+db.jdes()+'}'
    return [j]

def remove(db,rec):
    restock = False
    for i in rec:
        v=i[0]
        q=i[3]
        db.execute('UPDATE shop_products SET qty=qty+? WHERE pid=?',(q,v))
        db.execute('SELECT qty FROM shop_products WHERE pid=?',(i[3],))
        stock=db.fetch()[0][0]
        if stock > 0: restock = True
    if restock == True:
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

