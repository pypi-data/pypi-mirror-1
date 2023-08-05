# Copyright(c) gert.cuykens@gmail.com

from xmlframe import xmlframe

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    doc = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    data,size,sid = xmlframe(doc,sid,any,user,admin)
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', size),('Set-Cookie', sid)])
    return [data]

def any(db,v):
    if   v['cmd']=='find topics'     : db.execute("SELECT uid,hid,topic  FROM forum_topics WHERE topic LIKE %s",('%'+v['txt']+'%'))
    elif v['cmd']=='find threads'    : db.execute("SELECT uid,tid,thread FROM forum_threads WHERE hid=%s AND thread LIKE %s",(v['hid'],'%'+v['txt']+'%'))
    elif v['cmd']=='find messages'   : db.execute("SELECT uid,mid,message,time FROM forum_messages WHERE tid=%s AND message LIKE %s",(v['tid'],'%'+v['txt']+'%'))
    elif v['cmd']=='find all'        : db.execute("SELECT forum_topics.hid,forum_topics.topic,forum_threads.tid,forum_threads.thread,forum_messages.mid,forum_messages.message,forum_messages.time "
                                                  "FROM   forum_topics, forum_threads, forum_messages "
                                                  "WHERE  forum_messages.message LIKE %s "
                                                  "AND    forum_topics.hid=forum_threads.hid "
                                                  "AND    forum_threads.tid=forum_messages.tid "
                                                  "GROUP BY forum_messages.mid",('%'+v['txt']+'%'))

def user(db,v):
    if   v['cmd']=='insert topics'   : db.execute("INSERT INTO forum_topics (uid,topic) VALUES (%s,%s)",(v['uid'],v['txt']))
    elif v['cmd']=='insert threads'  : db.execute("INSERT INTO forum_threads (uid,hid,thread) VALUES (%s,%s,%s)",(v['uid'],v['hid'],v['txt']))
    elif v['cmd']=='insert messages' : db.execute("INSERT INTO forum_messages (uid,tid,time,message) VALUES (%s,%s,NOW(),%s)",(v['uid'],v['tid'],v['txt']))
    elif v['cmd']=='update topics'   : db.execute("UPDATE forum_topics SET topic=%s WHERE hid=%s AND uid=%s",(v['txt'],v['hid'],v['uid']))
    elif v['cmd']=='update threads'  : db.execute("UPDATE forum_threads SET thread=%s WHERE tid=%s AND uid=%s",(v['txt'],v['tid'],v['uid']))
    elif v['cmd']=='update messages' : db.execute("UPDATE forum_messages SET message=%s WHERE mid=%s AND uid=%s",(v['txt'],v['mid'],v['uid']))
    elif v['cmd']=='remove topics'   : db.execute("DELETE FROM forum_topics WHERE hid=%s AND uid=%s",(v['hid'],v['uid']))
    elif v['cmd']=='remove threads'  : db.execute("DELETE FROM forum_threads WHERE tid=%s AND uid=%s",(v['tid'],v['uid']))
    elif v['cmd']=='remove messages' : db.execute("DELETE FROM forum_messages WHERE mid=%s AND uid=%s",(v['mid'],v['uid']))
    elif v['cmd']=='find topics'     : db.execute("SELECT uid,hid,topic  FROM forum_topics WHERE topic LIKE %s",('%'+v['txt']+'%'))
    elif v['cmd']=='find threads'    : db.execute("SELECT uid,tid,thread FROM forum_threads WHERE hid=%s AND thread LIKE %s",(v['hid'],'%'+v['txt']+'%'))
    elif v['cmd']=='find messages'   : db.execute("SELECT uid,mid,message,time FROM forum_messages WHERE tid=%s AND message LIKE %s",(v['tid'],'%'+v['txt']+'%'))
    elif v['cmd']=='find all'        : db.execute("SELECT forum_topics.hid,forum_topics.topic,forum_threads.tid,forum_threads.thread,forum_messages.mid,forum_messages.message,forum_messages.time "
                                                  "FROM   forum_topics, forum_threads, forum_messages "
                                                  "WHERE  forum_messages.message LIKE %s "
                                                  "AND    forum_topics.hid=forum_threads.hid "
                                                  "AND    forum_threads.tid=forum_messages.tid "
                                                  "GROUP BY forum_messages.mid",('%'+v['txt']+'%'))

def admin(db,v):
    if   v['cmd']=='insert topics'   : db.execute("INSERT INTO forum_topics (uid,topic) VALUES (%s,%s)",(v['uid'],v['txt']))
    elif v['cmd']=='insert threads'  : db.execute("INSERT INTO forum_threads (uid,hid,thread) VALUES (%s,%s,%s)",(v['uid'],v['hid'],v['txt']))
    elif v['cmd']=='insert messages' : db.execute("INSERT INTO forum_messages (uid,tid,time,message) VALUES (%s,%s,NOW(),%s)",(v['uid'],v['tid'],v['txt']))
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
    

