# Copyright(c) gert.cuykens@gmail.com

import sessions
from db import MySql

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    db  = MySql()
    d   = sessions.get(db,'picture',sid)
    if  not d:
        import os
        f=open(os.path.join(os.path.dirname(__file__),'../www/bin/picture.png'),'rb')
        length = os.fstat(f.fileno()).st_size
        response('200 OK',[('Content-type','image/png'),('Content-Length', str(length))])
        if 'wsgi.file_wrapper' in environ: return environ['wsgi.file_wrapper'](f, 8192)
        else: return iter(lambda: f.read(8192), '')
         
    response('200 OK',[('Content-type', 'image/png'),('Content-Length', str(len(d)))])
    return [d]
