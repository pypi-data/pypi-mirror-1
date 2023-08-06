# Copyright(c) gert.cuykens@gmail.com
from os import path
from db import Db
from session import Session

def application(environ, response):
    cookie = environ.get('HTTP_COOKIE','')
    db = Db()
    session = Session(db,cookie,'guest')
    response('200 OK', [('Content-type', 'image/png'), ('Set-Cookie', session.COOKIE)])
    try:
        if not session.GID: raise
        db.execute('SELECT picture FROM users WHERE uid=%s',(session.UID))
        f = db.fetch()
        bin = f[0][0]
        if not bin: raise
        return [bin]
    except:
        f=open(path.join(path.dirname(__file__),'../bin/picture.png'),'rb')
        #length = fstat(f.fileno()).st_size
        if 'wsgi.file_wrapper' in environ: return environ['wsgi.file_wrapper'](f, 8192)
        else: return iter(lambda: f.read(8192), '')
