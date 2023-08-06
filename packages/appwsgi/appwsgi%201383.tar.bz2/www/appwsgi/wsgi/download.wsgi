# Copyright(c) gert.cuykens@gmail.com
from appwsgi.db import Db
from appwsgi.session import Session

class FileWrapper(object):
    def __init__(self, fp, blksize=8192):
        self.fp = fp
        self.blksize=blksize
    def __getitem__(self, key):
        data = self.fp.read(self.blksize)
        if data:
            return data
        raise IndexError
    def close(self):
        self.fp.close() 

def application(environ, response):
    db = Db()
    session = Session(db,environ.get('HTTP_COOKIE',''),'guest')
    try:
        if not session.GID: raise
        db.execute('SELECT picture FROM users WHERE uid=?',(session.UID,))
        f = db.fetch()
        bin = f[0][0]
        if not bin: raise
        response('200 OK', [('Content-type', 'image/png'), ('Content-Length', str(len(bin))), ('Set-Cookie', session.COOKIE)])
        return [bin]
    except:
        import os
        f=open(os.path.join(os.path.dirname(__file__),'../www/bin/picture.png'), 'rb')
        l = os.fstat(f.fileno()).st_size
        response('200 OK', [('Content-type', 'image/png'), ('Content-Length', str(l)), ('Set-Cookie', session.COOKIE)])
        if 'wsgi.file_wrapper' in environ: return environ['wsgi.file_wrapper'](f, 8192)
        else: return FileWrapper(f, 8192)
