# Copyright(c) gert.cuykens@gmail.com
import os

def buffer(f, length=-1, size=8192):
   while length<0:
      chunk = f.read(size)
      if not chunk: return
      yield chunk
   x=divmod(length,size)
   for i in range(x[0]): yield f.read(size)
   yield f.read(x[1])

def application(environ, response):
    #q=environ.get['QUERY_STRING']
    q=os.path.join(os.path.dirname(__file__),'teeeeeeeeeemp')
    o=[]
    for r in environ.get('HTTP_CONTENT_RANGE','bytes 0-').replace('bytes ','').split('/')[0].split(','): o.append(r.split('-'))
    with open(q,'ab+') as f:
        if environ['REQUEST_METHOD']=='PUT':
            f.seek(int(o[0][0]))
            f.truncate()
            if not 'HTTP_TRANSFER_ENCODING' in environ:
                for chunk in buffer(environ['wsgi.input'], int(environ['CONTENT_LENGTH'])): f.write(chunk)
            else:
                for chunk in buffer(environ['wsgi.input']): f.write(chunk)
            f.flush()
        l=str(os.fstat(f.fileno()).st_size)
    response('200 OK', [('Content-Type', 'text/plain'), ('Content-Length', str(len(l)))])
    return [l]

