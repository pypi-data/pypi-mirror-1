# Copyright(c) gert.cuykens@gmail.com

from xmlframe import read
from SOAPpy import SOAPProxy

def application(environ, response):
    doc = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    v   = read(doc)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml+= '<root>\n'
    xml+= soap('10')
    xml+= '</root>'
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', str(len(xml)))])
    return [xml]

def soap(v):
    try :
        url = 'http://services.xmethods.net:80/soap/servlet/rpcrouter'
        urn = 'urn:xmethods-Temperature'
        server = SOAPProxy(url, urn)
        server.config.dumpSOAPOut = 1
        server.config.dumpSOAPIn  = 1
        out=server.getTemp(v)
    except :
        out = "http://services.xmethods.net:80/soap/servlet/rpcrouter is broken"
    return ' <error>'+escape(str(out))+'</error>\n'

if  __name__ == '__main__' :
    ## METHOD1
    print soap('10')
    
    ## METHOD2
    import httplib
    m = '<?xml version="1.0" encoding="UTF-8"?>\n'
    m+= '<SOAP-ENV:Envelope\n'
    m+= ' SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"\n'
    m+= ' SOAP-ENC:root="1"\n'
    m+= ' xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"\n'
    m+= ' xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"\n'
    m+= ' xmlns:ns1="urn:xmethods-Temperature"\n'
    m+= ' xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"\n'
    m+= ' xmlns:xsd="http://www.w3.org/1999/XMLSchema">\n'
    m+= ' <SOAP-ENV:Body>\n'
    m+= '  <ns1:getTemp>\n'
    m+= '   <v1 xsi:type="xsd:string">10</v1>\n'
    m+= '  </ns1:getTemp>\n'
    m+= ' </SOAP-ENV:Body>\n'
    m+= '</SOAP-ENV:Envelope>\n'
    w = httplib.HTTP('services.xmethods.net:80')
    w.putrequest('POST','/soap/servlet/rpcrouter')
    w.putheader('Host','')
    w.putheader('User-Agent','Python')
    w.putheader('Content-type','text/xml; charset="UTF-8"')
    w.putheader('Content-length',str(len(m)))
    w.endheaders()
    w.send(m)
    print m
    print w.getreply()
    print w.getfile().read()
