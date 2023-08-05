# Copyright(c) gert.cuykens@gmail.com

from xmlframe import xmlframe

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
    elif v['cmd']=='remove': db.execute("DELETE FROM shop_orders WHERE oid=%s AND uid=%s",(v['oid'],v['uid']))
    elif v['cmd']=='insert': db.execute("INSERT INTO shop_orders (products,uid,bid,time) VALUES (%s,%s,%s,NOW())",(v['rec'],v['uid'],v['bid']))
    elif v['cmd']=='update': db.execute("UPDATE shop_orders SET products=%s, bid=%s WHERE oid=%s AND uid=%s",(v['rec'],v['bid'],v['oid'],v['uid']))

def admin(db,v):
    if   v['cmd']=='list'  : db.execute("SELECT uid,oid,bid,time FROM shop_orders WHERE uid=%s",(v['uid']))
    elif v['cmd']=='name'  : db.execute("SELECT uid,email,name,adress,city,country,phone FROM register WHERE name LIKE %s",('%'+v['una']+'%'))
    elif v['cmd']=='cart'  : db.execute("SELECT products FROM shop_orders WHERE oid=%s",(v['oid']))
    elif v['cmd']=='find'  : db.execute("SELECT * FROM shop_products WHERE description LIKE %s",('%'+v['pna']+'%'))
    elif v['cmd']=='pid'   : db.execute("SELECT * FROM shop_products WHERE pid=%s",(v['pid']))
    elif v['cmd']=='status': db.execute("SELECT * FROM shop_status",())
    elif v['cmd']=='remove': db.execute("DELETE FROM shop_orders WHERE oid=%s",(v['oid']))
    elif v['cmd']=='insert': db.execute("INSERT INTO shop_orders (products,uid,bid,time) VALUES (%s,%s,%s,NOW())",(v['rec'],v['uid'],v['bid']))
    elif v['cmd']=='update': db.execute("UPDATE shop_orders SET products=%s, bid=%s, uid=%s WHERE oid=%s",(v['rec'],v['bid'],v['uid'],v['oid']))

