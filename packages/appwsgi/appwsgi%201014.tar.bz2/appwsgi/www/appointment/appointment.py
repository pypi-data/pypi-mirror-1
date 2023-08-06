# Copyright(c) gert.cuykens@gmail.com
from frame import Frame
from session import Session
from db import Db

def application(environ, response):
    cookie = environ.get('HTTP_COOKIE','')
    document = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    db = Db()
    v = Frame.read(document)
    s = Session(db,cookie,v['gid'])

    if v['cmd'] == 'overview':
                               db.execute("SELECT calendar,appointment FROM appointments WHERE appointments.calendar >= %s AND appointments.calendar < %s",(v['from'],v['to']))
    elif v['cmd'] == 'insert':      
        if s.GID  == 'admin' : db.execute("INSERT INTO appointments VALUES (%s,0,%s,%s)",(v['uid'],v['calendar'],v['appointment']))
        elif s.GID == 'guest': db.execute("INSERT INTO appointments VALUES (%s,0,%s,%s)",(v['uid'],v['calendar'],v['appointment']))
    elif v['cmd'] == 'update':
        if s.GID  == 'admin':  db.execute("UPDATE appointments SET calendar=%s, appointment=%s WHERE aid=%s AND uid=%s",(v['calendar'],v['appointment'],v['aid'],v['uid']))
        elif s.GID == 'guest': db.execute("UPDATE appointments SET uid=%s, calendar=%s, appointment=%s WHERE aid=%s",(v['uid'],v['calendar'],v['appointment'],v['aid']))
    elif v['cmd'] == 'remove':
        if s.GID  == 'admin':  db.execute("DELETE FROM appointments WHERE aid=%s AND uid=%s",(v['aid'],v['uid']))
        elif s.GID == 'guest': db.execute("DELETE FROM appointments WHERE aid=%s",(v['aid']))
    elif v['cmd'] == 'name':
        if s.GID  == 'admin':  db.execute("SELECT uid,name,adress,city,country,phone FROM users WHERE name LIKE %s AND uid=%s",('%'+v['name']+'%',v['uid']))
        elif s.GID == 'guest': db.execute("SELECT uid,name,adress,city,country,phone FROM users WHERE name LIKE %s",("%"+v['name']+"%"))
    elif v['cmd'] == 'find':
                               db.execute("SELECT users.name, appointments.* FROM users, appointments WHERE users.uid = appointments.uid AND appointments.calendar >= %s AND appointments.appointment LIKE %s GROUP BY appointments.aid",(v['calendar'],"%"+v['appointment']+"%"))
    elif v['cmd'] == 'ca':
                               db.execute("SELECT users.name, appointments.* FROM users, appointments WHERE users.uid = appointments.uid AND appointments.calendar >= %s AND appointments.appointment LIKE %s AND appointments.uid=%s GROUP BY appointments.aid",(v['calendar'],"%"+v['appointment']+"%",v['uid']))

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml+= '<root>\n'
    xml+= ' <cmd>'+str(v['cmd'])+'</cmd>\n'
    xml+= ' <sid>'+str(s.SID)+'</sid>\n'
    xml+= ' <exp>'+str(s.EXP)+'</exp>\n'
    xml+= ' <uid>'+str(s.UID)+'</uid>\n'
    xml+= ' <gid>'+str(s.GID)+'</gid>\n'
    xml+= Frame.write(db)
    xml+= '</root>'

    response('200 OK', [('Content-type', 'text/xml'), ('Set-Cookie', s.COOKIE)])
    return [xml]

