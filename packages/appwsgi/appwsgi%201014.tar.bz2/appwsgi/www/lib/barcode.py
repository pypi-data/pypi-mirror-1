# Copyright(c) gert.cuykens@gmail.com

from code128 import code128
from xml.sax.saxutils import escape

def application(environ, response):
    bnr = environ['QUERY_STRING']
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml+= '<root>\n'
    try :
        data=code128(bnr)
        response('200 OK',[('Content-type', 'image/png'),('Content-Length', str(len(data)))])
        return [data]
    except IOError, (errno, strerror):
        xml+=' <error>Can not find font files</error>\n'
    except ImportError, (errno, strerror):
        xml+=' <error>python-imaging not installed</error>\n'
    xml+= ' <bnr>'+escape(str(bnr))+'</bnr>\n'
    xml+= '</root>'
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', str(len(xml)))])
    return [xml]

