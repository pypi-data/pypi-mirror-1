# Copyright(c) gert.cuykens@gmail.com
from json import loads
from appwsgi.session import Session
from appwsgi.db import Db

def application(environ, response):
    db = Db()
    v = loads(environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('utf-8'))
    s = Session(db,environ.get('HTTP_COOKIE',''), v['gid'])
  
    if s.GID == 'guest':
        if   v['cmd']=='insert topics'   : db.execute("INSERT INTO forum_topics (uid,topic) VALUES (?,?)",(s.UID,v['txt']))
        elif v['cmd']=='insert threads'  : db.execute("INSERT INTO forum_threads (uid,hid,thread) VALUES (?,?,?)",(s.UID,v['hid'],v['txt']))
        elif v['cmd']=='insert messages' : db.execute("INSERT INTO forum_messages (uid,tid,time,message) VALUES (?,?,DATETIME('NOW'),?)",(s.UID,v['tid'],v['txt']))
        elif v['cmd']=='update topics'   : db.execute("UPDATE forum_topics SET topic=? WHERE hid=? AND uid=?",(v['txt'],v['hid'],s.UID))
        elif v['cmd']=='update threads'  : db.execute("UPDATE forum_threads SET thread=? WHERE tid=? AND uid=?",(v['txt'],v['tid'],s.UID))
        elif v['cmd']=='update messages' : db.execute("UPDATE forum_messages SET message=? WHERE mid=? AND uid=?",(v['txt'],v['mid'],s.UID))
        elif v['cmd']=='remove topics'   : db.execute("DELETE FROM forum_topics WHERE hid=? AND uid=?",(v['hid'],s.UID))
        elif v['cmd']=='remove threads'  : db.execute("DELETE FROM forum_threads WHERE tid=? AND uid=?",(v['tid'],s.UID))
        elif v['cmd']=='remove messages' : db.execute("DELETE FROM forum_messages WHERE mid=? AND uid=?",(v['mid'],s.UID))
        elif v['cmd']=='find topics'     : db.execute("SELECT uid,hid,topic  FROM forum_topics WHERE topic LIKE ?",('%'+v['txt']+'%',))
        elif v['cmd']=='find threads'    : db.execute("SELECT uid,tid,thread FROM forum_threads WHERE hid=? AND thread LIKE ?",(v['hid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find messages'   : db.execute("SELECT uid,mid,message,time FROM forum_messages WHERE tid=? AND message LIKE ?",(v['tid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find all'        : db.execute("SELECT forum_topics.hid,forum_topics.topic,forum_threads.tid,forum_threads.thread,forum_messages.mid,forum_messages.message,forum_messages.time "
                                                      "FROM   forum_topics, forum_threads, forum_messages "
                                                      "WHERE  forum_messages.message LIKE ? "
                                                      "AND    forum_topics.hid=forum_threads.hid "
                                                      "AND    forum_threads.tid=forum_messages.tid "
                                                      "GROUP BY forum_messages.mid",('%'+v['txt']+'%',))
    elif s.GID == 'admin':
        if   v['cmd']=='insert topics'   : db.execute("INSERT INTO forum_topics (uid,topic) VALUES (?,?)",(s.UID,v['txt']))
        elif v['cmd']=='insert threads'  : db.execute("INSERT INTO forum_threads (uid,hid,thread) VALUES (?,?,?)",(s.UID,v['hid'],v['txt']))
        elif v['cmd']=='insert messages' : db.execute("INSERT INTO forum_messages (uid,tid,time,message) VALUES (?,?,DATETIME('NOW'),?)",(s.UID,v['tid'],v['txt']))
        elif v['cmd']=='update topics'   : db.execute("UPDATE forum_topics SET topic=? WHERE hid=?",(v['txt'],v['hid']))
        elif v['cmd']=='update threads'  : db.execute("UPDATE forum_threads SET thread=? WHERE tid=?",(v['txt'],v['tid']))
        elif v['cmd']=='update messages' : db.execute("UPDATE forum_messages SET message=? WHERE mid=?",(v['txt'],v['mid']))
        elif v['cmd']=='remove topics'   : db.execute("DELETE FROM forum_topics WHERE hid=?",(v['hid'],))
        elif v['cmd']=='remove threads'  : db.execute("DELETE FROM forum_threads WHERE tid=?",(v['tid'],))
        elif v['cmd']=='remove messages' : db.execute("DELETE FROM forum_messages WHERE mid=?",(v['mid'],))
        elif v['cmd']=='find topics'     : db.execute("SELECT uid,hid,topic  FROM forum_topics WHERE topic LIKE ?",('%'+v['txt']+'%',))
        elif v['cmd']=='find threads'    : db.execute("SELECT uid,tid,thread FROM forum_threads WHERE hid=? AND thread LIKE ?",(v['hid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find messages'   : db.execute("SELECT uid,mid,message,time FROM forum_messages WHERE tid=? AND message LIKE ?",(v['tid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find all'        : db.execute("SELECT forum_topics.hid,forum_topics.topic,forum_threads.tid,forum_threads.thread,forum_messages.mid,forum_messages.message,forum_messages.time "
                                                      "FROM   forum_topics, forum_threads, forum_messages "
                                                      "WHERE  forum_messages.message LIKE ? "
                                                      "AND    forum_topics.hid=forum_threads.hid "
                                                      "AND    forum_threads.tid=forum_messages.tid "
                                                      "GROUP BY forum_messages.mid",('%'+v['txt']+'%',))
    else: 
        if   v['cmd']=='find topics'     : db.execute("SELECT uid,hid,topic  FROM forum_topics WHERE topic LIKE ?",('%'+v['txt']+'%',))
        elif v['cmd']=='find threads'    : db.execute("SELECT uid,tid,thread FROM forum_threads WHERE hid=? AND thread LIKE ?",(v['hid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find messages'   : db.execute("SELECT uid,mid,message,time FROM forum_messages WHERE tid=? AND message LIKE ?",(v['tid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find all'        : db.execute("SELECT forum_topics.hid,forum_topics.topic,forum_threads.tid,forum_threads.thread,forum_messages.mid,forum_messages.message,forum_messages.time "
                                                      "FROM   forum_topics, forum_threads, forum_messages "
                                                      "WHERE  forum_messages.message LIKE ? "
                                                      "AND    forum_topics.hid=forum_threads.hid "
                                                      "AND    forum_threads.tid=forum_messages.tid "
                                                      "GROUP BY forum_messages.mid",('%'+v['txt']+'%',))

    j = '{"cmd":"'+str(v['cmd'])+'",\n'
    j+= ' "gid":"'+str(s.GID)+'",\n'
    j+= ' "uid":"'+str(s.UID)+'",\n'
    j+= ' "sid":"'+str(s.SID)+'",\n'
    j+= ' "exp":"'+str(s.EXP)+'",\n'
    j+= ' "rec":'+db.json()+',\n'
    j+= ' "des":'+db.jdes()+'}'
    
    j = j.encode('utf-8')
    response('200 OK', [('Content-type', 'text/javascript;charset=utf-8'), ('Content-Length', str(len(j))), ('Set-Cookie', s.COOKIE)])
    return [j]
