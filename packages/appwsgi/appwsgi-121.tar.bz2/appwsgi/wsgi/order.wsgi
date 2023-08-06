# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.db import Db
from appwsgi.session import Session
from appwsgi.out import text
from binascii import hexlify
from os import urandom

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8'))
    s = Session(db,v['sid'],v['gid'])

    def order1(db,v,s):  db.execute("SELECT * FROM orders WHERE uid=? AND oid=?",(v['uid'],v['oid']))
    def order2(db,v,s):  db.execute("SELECT * FROM orders WHERE uid=? AND oid=?",(s.UID,v['oid']))
    def find(db,v,s):    db.execute("SELECT p.pid,p.txt,p.price,p.qty-IFNULL(q.qty_sold,0) 'qty_available' FROM PRODUCTS p LEFT JOIN (SELECT o.pid 'pid', SUM(o.qty) 'qty_sold' FROM ORDERS o GROUP BY pid) q ON q.pid=p.pid WHERE ? LIKE ?",('txt','%'+v['txt']+'%',))
    def insert1(db,v,s): 
        db.execute("INSERT INTO orders (pid, txt, price) SELECT pid, txt, price FROM products WHERE pid=? AND ? NOT IN (SELECT pid FROM orders WHERE oid='new')",(v['pid'],v['pid']))
        db.execute("UPDATE orders SET qty=?, time=DATETIME('NOW'), uid=?, gid=? WHERE pid=? AND oid='new'",(v['qty'],v['uid'],v['gid'],v['pid']))
    def insert2(db,v,s): 
        db.execute("INSERT INTO orders (pid, txt, price) SELECT pid, txt, price FROM products WHERE pid=? AND ? NOT IN (SELECT pid FROM orders WHERE oid='new')",(v['pid'],v['pid']))
        db.execute("UPDATE orders SET qty=?, time=DATETIME('NOW'), uid=?, gid=? WHERE pid=? AND oid='new'",(v['qty'],s.UID,v['gid'],v['pid']))
    def delete1(db,v,s): db.execute("DELETE FROM orders WHERE pid=? AND uid=? AND oid='new'",(v['pid'],v['uid']))
    def delete2(db,v,s): db.execute("DELETE FROM orders WHERE pid=? AND uid=? AND oid='new'",(v['pid'],s.UID))
    def pay1(db,v,s):
        for i in range(3):
            r=hexlify(urandom(8)).decode('ascii') 
            db.execute("SELECT count(*) FROM orders WHERE oid=?",(r,))
            if db.fetch()[0][0]==0:
                db.execute("UPDATE orders SET oid=? WHERE uid=? AND oid='new'",(r,v['uid']))
                break
        else: raise RuntimeError('Failed to generate unique order ID')
    def pay2(db,v,s):
        for i in range(3):
            r=hexlify(urandom(8)).decode('ascii') 
            db.execute("SELECT count(*) FROM orders WHERE oid=?",(r,))
            if db.fetch()[0][0]==0:
                db.execute("UPDATE orders SET oid=? WHERE uid=? AND oid='new'",(r,s.UID))
                break
        else: raise RuntimeError('Failed to generate unique order ID')

    func = {('order', 'admin'): order1,
            ('order', 'guest'): order2,
            ('find',  'guest'): find,
            ('insert','admin'): insert1,
            ('insert','guest'): insert2,
            ('delete','admin'): delete1,
            ('delete','guest'): delete2,
            ('pay',   'admin'): pay1,
            ('pay',   'guest'): pay2}
 
    try: func[(v['cmd'],s.GID)](db,v,s)
    except KeyError: pass
    return text(response,db,s)

