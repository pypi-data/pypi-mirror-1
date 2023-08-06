# Copyright(c) gert.cuykens@gmail.com
from frame import Frame
from session import Session
from db import Db
from xml.dom import minidom

def application(environ, response):
    cookie = environ.get('HTTP_COOKIE','')
    document = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    db = Db()
    v = Frame.read(document)
    s = Session(db,cookie,v['gid'])

    if s.GID=='guest':
        if   v['cmd']=='invoice': db.execute("SELECT * FROM shop_orders WHERE oid=? AND uid=?",(v['oid'],s.UID))
        elif v['cmd']=='comments':
             db.execute("UPDATE shop_orders SET comments=CONCAT(IFNULL(comments,''),?) WHERE oid=? AND uid=?",(v['com'],v['oid'],s.UID))
             db.execute("SELECT comments FROM shop_orders WHERE oid=? AND uid=?",(v['oid'],s.UID))
        elif v['cmd']=='stats': db.execute("SELECT * FROM shop_status")
                              
    if s.GID=='admin':
        if   v['cmd']=='invoice': db.execute("SELECT * FROM shop_orders WHERE oid=?",(v['oid'],))
        elif v['cmd']=='comments': #CONCAT(IFNULL(comments,''),?) coalesce(comments,'')||?
             db.execute("UPDATE shop_orders SET comments=comments||? WHERE oid=?",(v['com'],v['oid']))
             db.execute("SELECT comments FROM shop_orders WHERE oid=?",(v['oid'],))
        elif v['cmd']=='stats': db.execute("SELECT * FROM shop_status")
        elif v['cmd']=='status':
             if v['bid'] == '1': remove(db,v['oid'])
             else: db.execute("UPDATE shop_orders SET bid=? WHERE oid=?",(v['bid'],v['oid']))

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

def remove(db,oid):
    db.execute("SELECT products FROM shop_orders WHERE oid=?",(oid,))
    document = minidom.parseString(db.fetch()[0][0])
    for i,pid in enumerate(document.getElementsByTagName('pid')):
        p=pid.childNodes[0].nodeValue
        q=document.getElementsByTagName('qty')[i].childNodes[0].nodeValue
        db.execute("UPDATE shop_products SET qty=qty+? WHERE pid=?",(q,p))
    db.execute("UPDATE shop_orders SET bid=1 WHERE oid=?",(oid,))

