# Copyright(c) gert.cuykens@gmail.com
from xml.dom import minidom
from xml.sax.saxutils import escape

class Frame(object):
    
    @classmethod 
    def read(cls,document):
        document = minidom.parseString(document)
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

    @classmethod
    def write(cls,db):
        xml = ' <id>'+str(db.LASTROWID)+'</id>\n'
        f = db.fetch()
        if  f:
            for i,r in enumerate(f):
                xml+= ' <record index="'+str(i)+'">\n'
                for j,c in enumerate(r):
                    xml+= '  <'+db.DESCRIPTION[j][0]+'>'+escape(str(c))+'</'+db.DESCRIPTION[j][0]+'>\n'
                xml+= ' </record>\n'
        if db.ERROR: xml+=' <error>'+escape(db.ERROR)+'</error>\n'
        return xml

