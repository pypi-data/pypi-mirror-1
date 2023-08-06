# Copyright(c) gert.cuykens@gmail.com
import os

class FileWrapper(object):
    def __init__(self, fp, blksize=8192):
        self.fp = fp
        self.blksize=blksize
    def __getitem__(self, key):
        data = self.fp.read(self.blksize)
        if data: return data
        raise IndexError
    def close(self):
        self.fp.close() 

def application(environ, response):
    #query=environ.get['QUERY_STRING']
    #print (query, file=environ['wsgi.errors'])
    query=os.path.join(os.path.dirname(__file__),'download2.wsgi')
    range=environ.get('HTTP_RANGE','bytes=0-').replace('bytes=','').split(',')
    offset=[]
    for r in range: offset.append(r.split('-'))
    f=open(query, 'rb')
    f.seek(int(offset[0][0]))
    lengthF=os.fstat(f.fileno()).st_size
    lengthC=str(lengthF-int(offset[0][0]))
    bitS=int(offset[0][0])
    bitE=lengthF-1
    bytes='bytes '+str(bitS)+'-'+str(bitE)+'/'+str(lengthF)
    response('200 OK', [('Content-Type', 'text/plain'), ('Content-Length', lengthC), ('Content-Range', bytes)])
    if 'wsgi.file_wrapper' in environ: return environ['wsgi.file_wrapper'](f, 8192)
    else: return FileWrapper(f, 8192)

