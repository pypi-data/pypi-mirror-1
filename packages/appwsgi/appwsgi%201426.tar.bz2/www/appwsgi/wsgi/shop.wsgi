# Copyright(c) gert.cuykens@gmail.com
from json import loads, dumps
from appwsgi.session import Session
from appwsgi.db import Db

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8'))
    s = Session(db,environ.get('HTTP_COOKIE',''),v['gid'])

    if s.GID=='guest':
        if   v['cmd']=='find'  : db.execute("SELECT * FROM shop_products WHERE description LIKE ?",('%'+v['pna']+'%',))
        elif v['cmd']=='pid'   : db.execute("SELECT * FROM shop_products WHERE pid=?",(v['pid'],))
        elif v['cmd']=='insert': 
             db.execute("INSERT INTO shop_orders (products,uid,bid,time) VALUES (?,?,2,DATETIME('NOW'))",(dumps(v['rec']),s.UID))
             oid=db.LASTROWID
             insert(db,oid)
             db.LASTROWID=oid

    if s.GID=='admin':
        if   v['cmd']=='find'  : db.execute("SELECT * FROM shop_products WHERE description LIKE ?",('%'+v['pna']+'%',))
        elif v['cmd']=='pid'   : db.execute("SELECT * FROM shop_products WHERE pid=?",(v['pid'],))
        elif v['cmd']=='insert':
             db.execute("INSERT INTO shop_orders (products,uid,bid,time) VALUES (?,?,2,DATETIME('NOW'))",(dumps(v['rec']),v['uid']))
             oid=db.LASTROWID
             insert(db,oid)
             db.LASTROWID=oid

    j = '{"cmd":"'+str(v['cmd'])+'",\n'
    j+= ' "gid":"'+str(s.GID)+'",\n'
    j+= ' "uid":"'+str(s.UID)+'",\n'
    j+= ' "sid":"'+str(s.SID)+'",\n'
    j+= ' "exp":"'+str(s.EXP)+'",\n'
    j+= ' "rid":"'+str(db.LASTROWID)+'",\n'
    j+= ' "rec":'+db.json()+',\n'
    j+= ' "des":'+db.jdes()+'}\n'
    
    j = j.encode('utf-8')
    response('200 OK', [('Content-type', 'text/javascript;charset=utf-8'), ('Content-Length', str(len(j))), ('Set-Cookie', s.COOKIE)])
    return [j]

def insert(db,oid):
    db.execute('SELECT products FROM shop_orders WHERE oid=?',(oid,))
    p = loads(db.fetch()[0][0])
    for i in p:
        v=i[0]
        q=i[3]
        db.execute('UPDATE shop_products SET qty=qty-? WHERE pid=?',(q,v))
        db.execute('SELECT qty FROM shop_products WHERE pid=?',(v,))
        qty = db.fetch()[0][0]
        if qty < 0: db.execute('UPDATE shop_orders SET bid=1 WHERE oid=?',(oid,))

