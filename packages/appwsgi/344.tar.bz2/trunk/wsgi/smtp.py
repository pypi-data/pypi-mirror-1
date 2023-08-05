# Copyright(c) gert.cuykens@gmail.com

from xmlframe import read
from smtplib import SMTP

def application(environ, response):
    doc = environ['wsgi.input'].read(int(environ.get('CONTENT_LENGTH','0')))
    v   = read(doc)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml+= '<root>\n'
    xml+= mail(v['user'],v['password'],v['to'],v['subject'],v['message'])
    xml+= '</root>'
    response('200 OK',[('Content-type', 'text/xml'),('Content-Length', str(len(xml)))])
    return [xml]

def mail(f,p,t,s,m):
    m = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (f, t, s, m)
    try :
        server = SMTP('smtp.gmail.com', 587)
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(f,p)
        server.sendmail(f,t,m)
        #server.rset()
        #server.quit()
    except :
        return ' <error>mail not send</error>\n'
    return ' <error>send succesfull</error>\n'

if  __name__ == '__main__':
    f=''
    p=''
    t=''
    s='test'
    m='test'
    print mail(f,p,t,s,m)

