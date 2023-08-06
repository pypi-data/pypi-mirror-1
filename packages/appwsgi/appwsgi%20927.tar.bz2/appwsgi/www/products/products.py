# Copyright(c) gert.cuykens@gmail.com

import os

def application(environ, response):
    p=environ.get('QUERY_STRING','0')
    f=open(os.path.join(os.path.dirname(__file__),p+'.xml'),'r')
    # length = os.fstat(f.fileno()).st_size
    # ('Content-Length', str(length))
    response('200 OK',[('Content-type','text/xml')])
    if 'wsgi.file_wrapper' in environ: return environ['wsgi.file_wrapper'](f, 8192)
    else: return iter(lambda: f.read(8192), '')

