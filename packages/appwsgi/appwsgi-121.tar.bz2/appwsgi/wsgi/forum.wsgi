# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.db import Db
from appwsgi.session import Session
from appwsgi.out import text

def application(environ, response):
    db= Db()
    v = loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8'))
    s = Session(db,v['sid'],v['gid'])

    def insert_topics(db,v,s):   db.execute("INSERT INTO topics (uid,topic) VALUES (?,?)",(s.UID,v['txt']))
    def insert_threads(db,v,s):  db.execute("INSERT INTO threads (uid,hid,thread) VALUES (?,?,?)",(s.UID,v['hid'],v['txt']))
    def insert_messages(db,v,s): db.execute("INSERT INTO messages (uid,tid,time,message) VALUES (?,?,DATETIME('NOW'),?)",(s.UID,v['tid'],v['txt']))
    def update_topics1(db,v,s):  db.execute("UPDATE topics SET topic=? WHERE hid=?",(v['txt'],v['hid']))
    def update_topics2(db,v,s):  db.execute("UPDATE topics SET topic=? WHERE hid=? AND uid=?",(v['txt'],v['hid'],s.UID))
    def update_threads1(db,v,s): db.execute("UPDATE threads SET thread=? WHERE tid=?",(v['txt'],v['tid']))
    def update_threads2(db,v,s): db.execute("UPDATE threads SET thread=? WHERE tid=? AND uid=?",(v['txt'],v['tid'],s.UID))
    def update_messages1(db,v,s):db.execute("UPDATE messages SET message=? WHERE mid=?",(v['txt'],v['mid']))
    def update_messages2(db,v,s):db.execute("UPDATE messages SET message=? WHERE mid=? AND uid=?",(v['txt'],v['mid'],s.UID))
    def remove_topics1(db,v,s):  db.execute("DELETE FROM topics WHERE hid=?",(v['hid'],))
    def remove_topics2(db,v,s):  db.execute("DELETE FROM topics WHERE hid=? AND uid=?",(v['hid'],s.UID))
    def remove_threads1(db,v,s): db.execute("DELETE FROM threads WHERE tid=?",(v['tid'],))
    def remove_threads2(db,v,s): db.execute("DELETE FROM threads WHERE tid=? AND uid=?",(v['tid'],s.UID))
    def remove_messages1(db,v,s):db.execute("DELETE FROM messages WHERE mid=?",(v['mid'],))
    def remove_messages2(db,v,s):db.execute("DELETE FROM messages WHERE mid=? AND uid=?",(v['mid'],s.UID))
    def desc_topics(db,v,s):
        s.GID=''
        db.execute("SELECT topic FROM topics WHERE hid=?",(v['hid'],))
    def find_topics(db,v,s):     
        s.GID=''
        db.execute("SELECT uid,hid,topic  FROM topics WHERE topic LIKE ?",('%'+v['txt']+'%',))
    def find_threads(db,v,s):    
        s.GID=''
        db.execute("SELECT uid,tid,thread FROM threads WHERE hid=? AND thread LIKE ?",(v['hid'],'%'+v['txt']+'%'))
    def find_messages(db,v,s):   
        s.GID=''
        db.execute("SELECT uid,mid,message,time FROM messages WHERE tid=? AND message LIKE ?",(v['tid'],'%'+v['txt']+'%'))
    def find_all(db,v,s):        
        s.GID=''
        db.execute("SELECT topics.hid,topics.topic,threads.tid,threads.thread,messages.mid,messages.message,messages.time "
                   "FROM topics, threads, messages "
                   "WHERE messages.message LIKE ? "
                   "AND topics.hid=threads.hid "
                   "AND threads.tid=messages.tid "
                   "GROUP BY messages.mid",('%'+v['txt']+'%',))

    func = {('insert topics',   'guest'): insert_topics,
            ('insert threads',  'guest'): insert_threads,
            ('insert messages', 'guest'): insert_messages,
            ('update topics',   'admin'): update_topics1,
            ('update topics',   'guest'): update_topics2,
            ('update threads',  'admin'): update_threads1,
            ('update threads',  'guest'): update_threads2,
            ('update messages', 'admin'): update_messages1,
            ('update messages', 'guest'): update_messages2,
            ('remove topics',   'admin'): remove_topics1,
            ('remove topics',   'guest'): remove_topics2,
            ('remove threads',  'admin'): remove_threads1,
            ('remove threads',  'guest'): remove_threads2,
            ('remove messages', 'admin'): remove_messages1,
            ('remove messages', 'guest'): remove_messages2,
            ('desc topics',     'login'): desc_topics,
            ('find topics',     'login'): find_topics,
            ('find threads',    'login'): find_threads,
            ('find messages',   'login'): find_messages,
            ('find all',        'login'): find_all}

    try: func[(v['cmd'], s.GID)](db,v,s)
    except KeyError: pass
    return text(response,db,s)

