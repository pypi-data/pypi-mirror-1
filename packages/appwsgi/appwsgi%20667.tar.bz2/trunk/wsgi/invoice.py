# Copyright(c) gert.cuykens@gmail.com

from xmlframe import xmlframe
from order import remove

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    doc = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    data,size,sid = xmlframe(doc,sid,any,user,admin)
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', size),('Set-Cookie', sid)])
    return [data]

def any(db,v):
    pass

def user(db,v):
    if   v['cmd']=='invoice': db.execute("SELECT * FROM shop_orders WHERE oid=%s AND uid=%s",(v['oid'],v['uid']))
    elif v['cmd']=='comments': 
         db.execute("UPDATE shop_orders SET comments=CONCAT(IFNULL(comments,''),%s) WHERE oid=%s AND uid=%s",(v['com'],v['oid'],v['uid']))
         db.execute("SELECT comments FROM shop_orders WHERE oid=%s AND uid=%s",(v['oid'],v['uid']))
    elif v['cmd']=='stats'  : db.execute("SELECT * FROM shop_status",())
                          
def admin(db,v):
    if   v['cmd']=='invoice': db.execute("SELECT * FROM shop_orders WHERE oid=%s",(v['oid']))
    elif v['cmd']=='comments': 
         db.execute("UPDATE shop_orders SET comments=CONCAT(IFNULL(comments,''),%s) WHERE oid=%s",(v['com'],v['oid']))
         db.execute("SELECT comments FROM shop_orders WHERE oid=%s",(v['oid']))
    elif v['cmd']=='stats'  : db.execute("SELECT * FROM shop_status",())
    elif v['cmd']=='status' :
         if v['bid'] == '1': remove(db,v['oid'])
         else: db.execute("UPDATE shop_orders SET bid=%s WHERE oid=%s",(v['bid'],v['oid']))

