# Copyright(c) gert.cuykens@gmail.com
from appwsgi.db import Db
from appwsgi.session import Session
import os

class FileWrapper(object):
    def __init__(self, fp, blksize=8192):
        self.fp=fp
        self.blksize=blksize
    def __getitem__(self, key):
        data = self.fp.read(self.blksize)
        if data: return data
        raise IndexError
    def close(self):
        self.fp.close() 

def application(environ, response):
    db=Db()
    v ={'sid':environ['QUERY_STRING'][0:16],'gid':'guest'}
    s =Session(db,v['sid'],v['gid'])

    try:
        if not s.UID: raise
        db.execute('SELECT picture FROM users WHERE uid=?',(s.UID,))
        f=db.fetch()
        if not f[0][0]: raise
        l=len(f[0][0])
        response('200 OK', [('Content-type', 'image/png'), ('Content-Length', str(l))])
        return [f[0][0]]

    except:
        f=open(os.path.join(os.path.dirname(__file__),'../www/bin/picture.png'), 'rb')
        l=os.fstat(f.fileno()).st_size
        response('200 OK', [('Content-type', 'image/png'), ('Content-Length', str(l))])
        if 'wsgi.file_wrapper' in environ: return environ['wsgi.file_wrapper'](f, 8192)
        else: return FileWrapper(f, 8192)

