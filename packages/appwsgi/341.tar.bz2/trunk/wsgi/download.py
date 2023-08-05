# Copyright(c) gert.cuykens@gmail.com

import session
from db import MySql

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    q   = environ.get('QUERY_STRING','')
    db  = MySql()
    d   = session.get(db,'picture',sid)
    if  not d:
        import os
        f=open(os.path.join(os.path.dirname(__file__),'../www/bin/picture.png'),'rb')
        length = os.fstat(f.fileno()).st_size
        response('200 OK',[('Content-type','image/png'),('Content-Length', str(length))])
        return environ['wsgi.file_wrapper'](f) 

    response('200 OK',[('Content-type', 'image/png'),('Content-Length', str(len(d)))])
    return [d]
