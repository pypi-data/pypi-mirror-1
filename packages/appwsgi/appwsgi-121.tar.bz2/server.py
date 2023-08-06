from wsgiref.simple_server import make_server
import site,os,imp

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

def static(url, mime):
    def application(environ, response):
        f=open(os.path.join(os.path.dirname(__file__), url),'rb')
        l=os.fstat(f.fileno()).st_size
        response('200 OK', [('Content-type', mime+';charset=utf-8'), ('Content-Length', str(l))])
        if 'wsgi.file_wrapper' in environ: return environ['wsgi.file_wrapper'](f, 8192)
        return FileWrapper(f, 8192)
    return application

def wsgi(url):
    path = os.path.join(os.path.dirname(__file__), url)
    imp.load_source('wsgi', path)
    import wsgi
    return wsgi.application

def server(environ, response):
    url = environ['PATH_INFO'][1:]
    mime = environ['PATH_INFO'][-3:]
    if   mime=='sgi': app = wsgi(url)
    elif mime=='css': app = static(url,'text/css')
    elif mime=='.js': app = static(url,'text/javascript')
    elif mime=='png': app = static(url,'image/png')
    elif mime=='ico': app = static(url,'image/x-icon')
    elif mime=='flv': app = static(url,'video/x-flv')
    elif mime=='mp3': app = static(url,'audio/mpeg')
    elif mime=='htm': app = static(url,'application/xhtml+xml')
    elif mime=='swf': app = static(url,'application/x-shockwave-flash')
    else: app = static(url,'text/plain')
    return app(environ, response)

if __name__ == '__main__':
    site.addsitedir(os.path.dirname(__file__))
    httpd = make_server('', 80, server)
    httpd.serve_forever()
