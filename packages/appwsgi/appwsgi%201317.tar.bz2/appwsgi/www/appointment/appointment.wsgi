# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.session import Session
from appwsgi.db import Db

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read().decode('utf-8'))
    s = Session(db,environ.get('HTTP_COOKIE',''),v['gid'])
    response('200 OK', [('Content-type', 'text/plain;charset=utf-8'), ('Set-Cookie', s.COOKIE)])

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

    j = '{"cmd":"'+str(v['cmd'])+'",\n'
    j+= ' "sid":"'+str(s.SID)+'",\n'
    j+= ' "exp":"'+str(s.EXP)+'",\n'
    j+= ' "uid":"'+str(s.UID)+'",\n'
    j+= ' "gid":"'+str(s.GID)+'",\n'
    j+= ' "rid":"'+str(db.LASTROWID)+'",\n'
    j+= ' "rec":'+db.json()+',\n'
    j+= ' "des":'+db.jdes()+'}'
    return [j.encode('utf-8')]

