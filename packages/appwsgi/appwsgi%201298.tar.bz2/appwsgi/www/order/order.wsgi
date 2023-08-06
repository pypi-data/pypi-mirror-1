# Copyright(c) gert.cuykens@gmail.com
from json import loads, dumps
from session import Session
from db import Db

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read().decode('utf-8'))
    s = Session(db,environ.get('HTTP_COOKIE',''),v['gid'])
    response('200 OK', [('Content-type', 'text/plain;charset=utf-8'), ('Set-Cookie', s.COOKIE)])

    if s.GID=='guest':
        if   v['cmd']=='list'  : db.execute("SELECT * FROM shop_orders WHERE uid=?",(s.UID,))
        elif v['cmd']=='status': db.execute("SELECT * FROM shop_status")
        elif v['cmd']=='stats' : db.execute("SELECT * FROM shop_orders WHERE bid=? AND uid=?",(v['bid'],s.UID))

    if s.GID=='admin':
        if   v['cmd']=='list'  : db.execute("SELECT * FROM shop_orders WHERE uid=?",(v['uid'],))
        elif v['cmd']=='status': db.execute("SELECT * FROM shop_status")
        elif v['cmd']=='stats' : db.execute("SELECT * FROM shop_orders WHERE bid=?",(v['bid'],))   
        elif v['cmd']=='name'  : db.execute("SELECT uid,name,adress,city,country,phone FROM users WHERE name LIKE ?",('%'+v['una']+'%',))
        
    j = '{"cmd":"'+str(v['cmd'])+'",\n'
    j+= ' "gid":"'+str(s.GID)+'",\n'
    j+= ' "uid":"'+str(s.UID)+'",\n'
    j+= ' "sid":"'+str(s.SID)+'",\n'
    j+= ' "exp":"'+str(s.EXP)+'",\n'
    j+= ' "rec":'+db.json()+',\n'
    j+= ' "des":'+db.jdes()+'}\n'
    return [j]

