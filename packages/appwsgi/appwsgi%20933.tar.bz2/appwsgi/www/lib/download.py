# Copyright(c) gert.cuykens@gmail.com
import os,sessions
from db import Db

def application(environ, response):
    sid = environ.get('HTTP_COOKIE','')
    db  = Db()
    bin = sessions.get(db,'picture',sid)
    response('200 OK',[('Content-type','image/png')])
    if  not bin:
        f=open(os.path.join(os.path.dirname(__file__),'../bin/picture.png'),'rb')
        #length = os.fstat(f.fileno()).st_size
        if 'wsgi.file_wrapper' in environ: return environ['wsgi.file_wrapper'](f, 8192)
        else: return iter(lambda: f.read(8192), '')
    return [bin]
