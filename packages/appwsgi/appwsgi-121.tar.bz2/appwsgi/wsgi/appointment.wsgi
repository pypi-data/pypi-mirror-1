# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.db import Db
from appwsgi.session import Session
from appwsgi.out import text

def application(environ, response):
    db= Db()
    v = loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8'))
    s = Session(db,v['sid'],v['gid'])

    def overview(db,v,s):
        s.GID=''
        db.execute("SELECT calendar,appointment FROM appointments WHERE calendar >= ? AND calendar < ?",(v['from'],v['to']))
    def find(db,v,s):     db.execute("SELECT users.name, appointments.* FROM users, appointments WHERE users.uid = appointments.uid AND appointments.calendar >= ? AND appointments.appointment LIKE ? GROUP BY appointments.aid",(v['calendar'],"%"+v['appointment']+"%"))
    def ca(db,v,s):       db.execute("SELECT users.name, appointments.* FROM users, appointments WHERE users.uid = appointments.uid AND appointments.calendar >= ? AND appointments.appointment LIKE ? AND appointments.uid=? GROUP BY appointments.aid",(v['calendar'],"%"+v['appointment']+"%",v['uid']))
    def insert1(db,v,s):  db.execute("INSERT INTO appointments VALUES (?,?,NULL,?,?)",(v['uid'],v['gid'],v['calendar'],v['appointment']))
    def insert2(db,v,s):  db.execute("INSERT INTO appointments VALUES (?,?,NULL,?,?)",(s.UID,s.GID,v['calendar'],v['appointment']))
    def update1(db,v,s):  db.execute("UPDATE appointments SET uid=?, gid=?, calendar=?, appointment=? WHERE aid=?",(v['uid'],v['gid'],v['calendar'],v['appointment'],v['aid']))
    def update2(db,v,s):  db.execute("UPDATE appointments SET calendar=?, appointment=? WHERE aid=? AND uid=?",(v['calendar'],v['appointment'],v['aid'],s.UID))
    def remove1(db,v,s):  db.execute("DELETE FROM appointments WHERE aid=?",(v['aid'],))
    def remove2(db,v,s):  db.execute("DELETE FROM appointments WHERE aid=? AND uid=?",(v['aid'],s.UID))
    def name1(db,v,s):    db.execute("SELECT uid,name,adress,city,country,phone FROM users WHERE name LIKE ?",("%"+v['name']+"%",))
    def name2(db,v,s):    db.execute("SELECT uid,name,adress,city,country,phone FROM users WHERE name LIKE ? AND uid=?",('%'+v['name']+'%',s.UID))

    func = {('overview', 'login') : overview,
            ('find',     'guest') : find,
            ('ca',       'guest') : ca,
            ('insert',   'admin') : insert1,
            ('insert',   'guest') : insert2,
            ('update',   'admin') : update1,
            ('update',   'guest') : update2,
            ('remove',   'admin') : remove1, 
            ('remove',   'guest') : remove2,
            ('name',     'admin') : name1,
            ('name',     'guest') : name2}

    try: func[(v['cmd'],s.GID)](db,v,s)
    except KeyError: pass
    return text(response,db,s)

