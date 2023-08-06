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
    if   v['cmd'] == 'overview': db.execute("SELECT calendar,appointment FROM appointments WHERE appointments.calendar >= %s AND appointments.calendar < %s",(v['from'],v['to']))
    elif v['cmd'] == 'insert'  : db.execute("INSERT INTO appointments VALUES (%s,0,%s,%s)",(v['uid'],v['calendar'],v['appointment']))
    elif v['cmd'] == 'update'  : db.execute("UPDATE appointments SET calendar=%s, appointment=%s WHERE aid=%s AND uid=%s",(v['calendar'],v['appointment'],v['aid'],v['uid']))
    elif v['cmd'] == 'remove'  : db.execute("DELETE FROM appointments WHERE aid=%s AND uid=%s",(v['aid'],v['uid']))
    elif v['cmd'] == 'name'    : db.execute("SELECT uid,email,name,adress,city,country,phone FROM register WHERE name LIKE %s AND uid=%s",('%'+v['name']+'%',v['uid']))
    elif v['cmd'] == 'find'    : db.execute("SELECT register.name, appointments.* FROM register, appointments WHERE register.uid = appointments.uid AND appointments.calendar >= %s AND appointments.appointment LIKE %s                         GROUP BY appointments.aid",(v['calendar'],"%"+v['appointment']+"%"))
    elif v['cmd'] == 'ca'      : db.execute("SELECT register.name, appointments.* FROM register, appointments WHERE register.uid = appointments.uid AND appointments.calendar >= %s AND appointments.appointment LIKE %s AND appointments.uid=%s GROUP BY appointments.aid",(v['calendar'],"%"+v['appointment']+"%",v['uid']))

def admin(db,v):
    if   v['cmd'] == 'overview': db.execute("SELECT calendar,appointment FROM appointments WHERE appointments.calendar >= %s AND appointments.calendar < %s",(v['from'],v['to']))
    elif v['cmd'] == 'insert'  : db.execute("INSERT INTO appointments VALUES (%s,0,%s,%s)",(v['uid'],v['calendar'],v['appointment']))
    elif v['cmd'] == 'update'  : db.execute("UPDATE appointments SET uid=%s, calendar=%s, appointment=%s WHERE aid=%s",(v['uid'],v['calendar'],v['appointment'],v['aid']))
    elif v['cmd'] == 'remove'  : db.execute("DELETE FROM appointments WHERE aid=%s",(v['aid']))
    elif v['cmd'] == 'name'    : db.execute("SELECT uid,email,name,adress,city,country,phone FROM register WHERE name LIKE %s",("%"+v['name']+"%"))
    elif v['cmd'] == 'find'    : db.execute("SELECT register.name, appointments.* FROM register, appointments WHERE register.uid = appointments.uid AND appointments.calendar >= %s AND appointments.appointment LIKE %s                         GROUP BY appointments.aid",(v['calendar'],"%"+v['appointment']+"%"))
    elif v['cmd'] == 'ca'      : db.execute("SELECT register.name, appointments.* FROM register, appointments WHERE register.uid = appointments.uid AND appointments.calendar >= %s AND appointments.appointment LIKE %s AND appointments.uid=%s GROUP BY appointments.aid",(v['calendar'],"%"+v['appointment']+"%",v['uid']))

