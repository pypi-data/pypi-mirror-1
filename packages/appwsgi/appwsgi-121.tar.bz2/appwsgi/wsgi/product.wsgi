# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.db import Db
from appwsgi.session import Session
from appwsgi.out import text

def application(environ, response):
    db= Db()
    v = loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8'))
    s = Session(db,v['sid'],v['gid'])

    def select(db,v,s): db.execute("SELECT p.pid,p.txt,p.price,p.qty-IFNULL(q.qty_sold,0) 'qty_available' FROM PRODUCTS p LEFT JOIN (SELECT o.pid 'pid', SUM(o.qty) 'qty_sold' FROM ORDERS o GROUP BY pid) q ON q.pid=p.pid WHERE p.pid LIKE ? AND p.txt LIKE ? AND p.price LIKE ? OR p.qty <= ?",('%'+v['pid']+'%','%'+v['txt']+'%','%'+v['price']+'%',v['qty']))
    def insert(db,v,s): db.execute("INSERT INTO products VALUES (?,?,?,?+coalesce((SELECT sum(qty) FROM orders WHERE pid=?),0))",(v['pid'],v['txt'],v['price'],v['qty'],v['pid']))
    def update(db,v,s): db.execute("UPDATE products SET txt=?, price=?, qty=?+coalesce((SELECT sum(qty) FROM orders WHERE pid=products.pid),0) WHERE pid=?",(v['txt'],v['price'],v['qty'],v['pid']))
    def delete(db,v,s): db.execute("DELETE FROM products WHERE pid=?",(v['pid'],))

    func = {('select', 'admin'): select,
            ('insert', 'admin'): insert,
            ('update', 'admin'): update,
            ('delete', 'admin'): delete}

    try: func[(v['cmd'], s.GID)](db,v,s)
    except KeyError: pass
    return text(response,db,s)

