# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.db import Db
from appwsgi.session import Session
from appwsgi.out import text
from time import strftime, gmtime, time
from binascii import hexlify
from os import urandom

def application(environ, response):
    db= Db()
    v = loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8'))
    s = Session(db,v['sid'],v['gid'])

    def mailpwd(db,v,s):
        db.execute('SELECT pwd FROM sessions WHERE uid=?',(v['uid'],))
        mail(v['uid'],'password',db)
    def logout(db,v,s): 
        db.execute('UPDATE sessions SET exp=? WHERE sid=?',(strftime('%Y-%m-%d %H:%M:%S', gmtime(time())),s.SID))
        s.GID='login'
    def login(db,v,s):
        db.execute('INSERT INTO sessions (uid, pwd, sid, exp) SELECT ?,?,?,? WHERE ? NOT IN (SELECT uid FROM sessions)',(v['uid'],v['pwd'],v['sid'],strftime('%Y-%m-%d %H:%M:%S',gmtime(time()+3600)),v['uid']))
        for i in range(3):
            s.SID=hexlify(urandom(8)).decode('ascii')
            try: db.execute('UPDATE sessions SET sid=?, exp=? WHERE uid=? AND pwd=?',(s.SID,strftime('%Y-%m-%d %H:%M:%S',gmtime(time()+3600)),v['uid'],v['pwd']))
            except IntegrityError: continue
            break
        else: raise RuntimeError('Failed to generate unique session ID')
        db.execute("INSERT INTO users (uid) SELECT ? WHERE ? NOT IN (SELECT uid FROM users)",(v['uid'],v['uid']))
        db.execute("INSERT INTO groups (uid, gid) SELECT ?,'guest' WHERE 'guest' NOT IN (SELECT gid FROM groups WHERE uid=?)",(v['uid'],v['uid']))
        db.execute("INSERT INTO groups (uid, gid) SELECT ?,'admin' WHERE 'admin' NOT IN (SELECT gid FROM groups WHERE uid=?)",(v['uid'],v['uid']))
        s.GID='guest'
    def delete(db,v,s): 
        db.execute('DELETE FROM users WHERE uid=?',(s.UID,))
        db.execute('DELETE FROM sessions WHERE uid=?',(s.UID,)) # sqlite no foreign key yet
        s.GID='login'
    def update(db,v,s): db.execute('UPDATE users SET name=?, adress=?, city=?, country=?, phone=? WHERE uid=?',(v['name'],v['adress'],v['city'],v['country'],v['phone'],s.UID))
    def passwd(db,v,s): db.execute('UPDATE sessions SET pwd=? WHERE sid=?',(v['pwd'],s.SID))
    def email(db,v,s):
        db.TRANSACTION=True
        db.execute('UPDATE users SET uid=? WHERE uid=?',(v['uid'],s.UID))
        db.execute('UPDATE sessions SET uid=? WHERE sid=?',(v['uid'],s.SID))
        db.execute('UPDATE groups SET uid=? WHERE uid=?',(v['uid'],s.UID)) # at all foreign databases for manual uid update
        if db.ERROR == None: db.commit()
        else: db.rollback()
        db.execute('SELECT uid FROM sessions WHERE sid=?',(s.SID,))
    def select(db,v,s): db.execute('SELECT uid,name,adress,city,country,phone FROM users WHERE uid=?',(s.UID,))

    func = {('delete', 'guest'): delete,
            ('update', 'guest'): update,
            ('passwd', 'guest'): passwd,
            ('email',  'guest'): email,
            ('select', 'guest'): select,
            ('mailpwd','login'): mailpwd,
            ('login',  'login'): login,
            ('logout', 'guest'): logout}
 
    try: func[(v['cmd'],s.GID)](db,v,s)
    except KeyError: pass
    return text(response,db,s)

"""
# http://groups.google.be/group/comp.lang.python/browse_thread/thread/be5a9575d7dbf8f3#
# First copy the row if it exists 
db.execute('''insert into "users"
              select ?, "name", adress, city, country, phone, picture
              from "users" where "uid" = ? ''', (v['uid'],s.UID) )

# Second update foriegn key tables to point to the new row
# (but only if the new row exists )
db.execute('''update "sessions" set "uid" = ?
              where "uid" = ?
              and exists(select * from "users" where "uid" = ?) ''', (v['uid'],s.SID, v['uid']) )

#Do the same for the "groups" table, then
# finally delete the original row (again only if the new row exists )
db.execute('''delete from "users"
              where "uid" = ? and exists( select * from "users" where "uid" = ?) ''', (s.SID, v['uid']) ) 
"""

