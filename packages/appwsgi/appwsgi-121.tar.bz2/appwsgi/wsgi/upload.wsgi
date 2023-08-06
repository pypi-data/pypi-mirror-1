# Copyright(c) gert.cuykens@gmail.com
from appwsgi.db import Db
from appwsgi.session import Session
from appwsgi.out import text
from re import search,DOTALL

def application(environ, response):
    db=Db()
    v ={'cmd':'upload','sid':environ['QUERY_STRING'],'gid':'guest'}
    s =Session(db,v['sid'],v['gid'])

    if s.GID!='login':
        chunk=environ['wsgi.input'].read(int(environ['CONTENT_LENGTH'])).decode('latin1')
        b=environ['CONTENT_TYPE'].split('boundary=')[1]   
        chunk=search(b+r'.*?Content-Type: application/octet-stream\r\n\r\n(.*?)\r\n--'+b,chunk,DOTALL).group(1).encode('latin1') 
        #from cgi import FieldStorage
        #form = FieldStorage(fp=environ['wsgi.input'], environ=environ)
        #chunk = form['Filedata'].file.read()
        db.execute('UPDATE users SET picture=? WHERE uid=?', (chunk, s.UID))
    return text(response,db,s)

