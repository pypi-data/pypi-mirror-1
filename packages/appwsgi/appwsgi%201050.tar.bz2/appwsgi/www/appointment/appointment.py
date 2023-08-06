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
                               db.execute("SELECT calendar,appointment FROM appointments WHERE calendar >= ? AND calendar < ?",(v['from'],v['to']))
    elif v['cmd'] == 'insert':      
        if s.GID  == 'guest' : db.execute("INSERT INTO appointments VALUES (?,NULL,?,?)",(s.UID,v['calendar'],v['appointment']))
        elif s.GID == 'admin': db.execute("INSERT INTO appointments VALUES (?,NULL,?,?)",(v['uid'],v['calendar'],v['appointment']))
    elif v['cmd'] == 'update':
        if s.GID  == 'guest':  db.execute("UPDATE appointments SET calendar=?, appointment=? WHERE aid=? AND uid=?",(v['calendar'],v['appointment'],v['aid'],s.UID))
        elif s.GID == 'admin': db.execute("UPDATE appointments SET uid=?, calendar=?, appointment=? WHERE aid=?",(v['uid'],v['calendar'],v['appointment'],v['aid']))
    elif v['cmd'] == 'remove':
        if s.GID  == 'guest':  db.execute("DELETE FROM appointments WHERE aid=? AND uid=?",(v['aid'],s.UID))
        elif s.GID == 'admin': db.execute("DELETE FROM appointments WHERE aid=?",(v['aid'],))
    elif v['cmd'] == 'name':
        if s.GID  == 'guest':  db.execute("SELECT uid,name,adress,city,country,phone FROM users WHERE name LIKE ? AND uid=?",('%'+v['name']+'%',s.UID))
        elif s.GID == 'admin': db.execute("SELECT uid,name,adress,city,country,phone FROM users WHERE name LIKE ?",("%"+v['name']+"%",))
    elif v['cmd'] == 'find':
                               db.execute("SELECT users.name, appointments.* FROM users, appointments WHERE users.uid = appointments.uid AND appointments.calendar >= ? AND appointments.appointment LIKE ? GROUP BY appointments.aid",(v['calendar'],"%"+v['appointment']+"%"))
    elif v['cmd'] == 'ca':
                               db.execute("SELECT users.name, appointments.* FROM users, appointments WHERE users.uid = appointments.uid AND appointments.calendar >= ? AND appointments.appointment LIKE ? AND appointments.uid=? GROUP BY appointments.aid",(v['calendar'],"%"+v['appointment']+"%",v['uid']))

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

