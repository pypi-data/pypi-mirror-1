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

    if s.GID == 'guest':
        if   v['cmd']=='insert topics'   : db.execute("INSERT INTO forum_topics (uid,topic) VALUES (%s,%s)",(s.UID,v['txt']))
        elif v['cmd']=='insert threads'  : db.execute("INSERT INTO forum_threads (uid,hid,thread) VALUES (%s,%s,%s)",(s.UID,v['hid'],v['txt']))
        elif v['cmd']=='insert messages' : db.execute("INSERT INTO forum_messages (uid,tid,time,message) VALUES (%s,%s,NOW(),%s)",(s.UID,v['tid'],v['txt']))
        elif v['cmd']=='update topics'   : db.execute("UPDATE forum_topics SET topic=%s WHERE hid=%s AND uid=%s",(v['txt'],v['hid'],s.UID))
        elif v['cmd']=='update threads'  : db.execute("UPDATE forum_threads SET thread=%s WHERE tid=%s AND uid=%s",(v['txt'],v['tid'],s.UID))
        elif v['cmd']=='update messages' : db.execute("UPDATE forum_messages SET message=%s WHERE mid=%s AND uid=%s",(v['txt'],v['mid'],s.UID))
        elif v['cmd']=='remove topics'   : db.execute("DELETE FROM forum_topics WHERE hid=%s AND uid=%s",(v['hid'],s.UID))
        elif v['cmd']=='remove threads'  : db.execute("DELETE FROM forum_threads WHERE tid=%s AND uid=%s",(v['tid'],s.UID))
        elif v['cmd']=='remove messages' : db.execute("DELETE FROM forum_messages WHERE mid=%s AND uid=%s",(v['mid'],s.UID))
        elif v['cmd']=='find topics'     : db.execute("SELECT uid,hid,topic  FROM forum_topics WHERE topic LIKE %s",('%'+v['txt']+'%'))
        elif v['cmd']=='find threads'    : db.execute("SELECT uid,tid,thread FROM forum_threads WHERE hid=%s AND thread LIKE %s",(v['hid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find messages'   : db.execute("SELECT uid,mid,message,time FROM forum_messages WHERE tid=%s AND message LIKE %s",(v['tid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find all'        : db.execute("SELECT forum_topics.hid,forum_topics.topic,forum_threads.tid,forum_threads.thread,forum_messages.mid,forum_messages.message,forum_messages.time "
                                                      "FROM   forum_topics, forum_threads, forum_messages "
                                                      "WHERE  forum_messages.message LIKE %s "
                                                      "AND    forum_topics.hid=forum_threads.hid "
                                                      "AND    forum_threads.tid=forum_messages.tid "
                                                      "GROUP BY forum_messages.mid",('%'+v['txt']+'%'))
    elif s.GID == 'admin':
        if   v['cmd']=='insert topics'   : db.execute("INSERT INTO forum_topics (uid,topic) VALUES (%s,%s)",(s.UID,v['txt']))
        elif v['cmd']=='insert threads'  : db.execute("INSERT INTO forum_threads (uid,hid,thread) VALUES (%s,%s,%s)",(s.UID,v['hid'],v['txt']))
        elif v['cmd']=='insert messages' : db.execute("INSERT INTO forum_messages (uid,tid,time,message) VALUES (%s,%s,NOW(),%s)",(s.UID,v['tid'],v['txt']))
        elif v['cmd']=='update topics'   : db.execute("UPDATE forum_topics SET topic=%s WHERE hid=%s",(v['txt'],v['hid']))
        elif v['cmd']=='update threads'  : db.execute("UPDATE forum_threads SET thread=%s WHERE tid=%s",(v['txt'],v['tid']))
        elif v['cmd']=='update messages' : db.execute("UPDATE forum_messages SET message=%s WHERE mid=%s",(v['txt'],v['mid']))
        elif v['cmd']=='remove topics'   : db.execute("DELETE FROM forum_topics WHERE hid=%s",(v['hid']))
        elif v['cmd']=='remove threads'  : db.execute("DELETE FROM forum_threads WHERE tid=%s",(v['tid']))
        elif v['cmd']=='remove messages' : db.execute("DELETE FROM forum_messages WHERE mid=%s",(v['mid']))
        elif v['cmd']=='find topics'     : db.execute("SELECT uid,hid,topic  FROM forum_topics WHERE topic LIKE %s",('%'+v['txt']+'%'))
        elif v['cmd']=='find threads'    : db.execute("SELECT uid,tid,thread FROM forum_threads WHERE hid=%s AND thread LIKE %s",(v['hid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find messages'   : db.execute("SELECT uid,mid,message,time FROM forum_messages WHERE tid=%s AND message LIKE %s",(v['tid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find all'        : db.execute("SELECT forum_topics.hid,forum_topics.topic,forum_threads.tid,forum_threads.thread,forum_messages.mid,forum_messages.message,forum_messages.time "
                                                      "FROM   forum_topics, forum_threads, forum_messages "
                                                      "WHERE  forum_messages.message LIKE %s "
                                                      "AND    forum_topics.hid=forum_threads.hid "
                                                      "AND    forum_threads.tid=forum_messages.tid "
                                                      "GROUP BY forum_messages.mid",('%'+v['txt']+'%'))
    else: 
        if   v['cmd']=='find topics'     : db.execute("SELECT uid,hid,topic  FROM forum_topics WHERE topic LIKE %s",('%'+v['txt']+'%'))
        elif v['cmd']=='find threads'    : db.execute("SELECT uid,tid,thread FROM forum_threads WHERE hid=%s AND thread LIKE %s",(v['hid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find messages'   : db.execute("SELECT uid,mid,message,time FROM forum_messages WHERE tid=%s AND message LIKE %s",(v['tid'],'%'+v['txt']+'%'))
        elif v['cmd']=='find all'        : db.execute("SELECT forum_topics.hid,forum_topics.topic,forum_threads.tid,forum_threads.thread,forum_messages.mid,forum_messages.message,forum_messages.time "
                                                      "FROM   forum_topics, forum_threads, forum_messages "
                                                      "WHERE  forum_messages.message LIKE %s "
                                                      "AND    forum_topics.hid=forum_threads.hid "
                                                      "AND    forum_threads.tid=forum_messages.tid "
                                                      "GROUP BY forum_messages.mid",('%'+v['txt']+'%'))

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
