# Copyright(c) gert.cuykens@gmail.com

import sessions
from xml.dom import minidom
from xml.sax.saxutils import escape
from db import MySql

def xmlframe(doc,sid,*arg):
    v=read(doc)

    try: 
        if v['cmd']: db = MySql()
    except: return 'no cmd','6',''

    if   v['cmd']=='login': sid = sessions.set(db,'login',v['email'],v['pwd'])
    elif v['cmd']=='logout': sid = sessions.set(db,'logout','sid',sid)
    else: sid = sessions.set(db,'timeout','sid',sid)

    v['uid']=sessions.get(db,'uid',sid)
    v['gid']=sessions.get(db,'gid',sid)

    try: arg[v['gid']](db,v)
    except: arg[0](db,v)

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml+= '<root>\n'
    xml+= ' <uid>'+str(v['uid'])+'</uid>\n'
    xml+= ' <gid>'+str(v['gid'])+'</gid>\n'
    xml+= write(db)
    xml+= '</root>'
    data=xml
    size=str(len(xml))
    return data,size,sid

def read(doc):
    document = minidom.parseString(doc)
    xml='<?xml version="1.0" encoding="UTF-8"?>\n<root>\n'
    for r in document.getElementsByTagName('record'):
        xml+=' <record index="'+r.getAttribute('index')+'">\n'
        for b in r.childNodes:
            if  b.nodeType==b.ELEMENT_NODE:
                name=b.nodeName
                xml+='  <'+name+'>'
                v=''
                for c in b.childNodes:
                    v=v+c.nodeValue
                xml+=escape(str(v))
                xml+='</'+name+'>\n'
        xml+=' </record>\n'
    xml+='</root>'
    v={'rec':xml}
    for e in document.childNodes[0].childNodes:
        if  e.nodeType==e.ELEMENT_NODE:
            v[e.nodeName]=''
            for c in e.childNodes:
                v[e.nodeName]+=str(c.nodeValue)
    return v

def write(db):
    xml = ' <id>'+str(db.INSERTID)+'</id>\n'
    f = db.fetch()
    if  f:
        for i,r in enumerate(f):
            xml+= ' <record index="'+str(i)+'">\n'
            for j,c in enumerate(r):
                xml+= '  <'+db.DESCRIPTION[j][0]+'>'+escape(str(c))+'</'+db.DESCRIPTION[j][0]+'>\n'
            xml+= ' </record>\n'
    if db.ERROR: xml+=' <error>'+escape(db.ERROR)+'</error>\n'
    return xml

