// Copyright(c) gert.cuykens@gmail.com
vi=
{
 'read':function()
 {
  http.fml=function(xml)
  {
   if (xml.getElementsByTagName('error')[0]) alert(xml.getElementsByTagName('error')[0].childNodes[0].nodeValue)
   document.getElementsByTagName('textarea')[0].value=xml.getElementsByTagName('root')[0].childNodes[0].data
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <vi>read</vi>\n'
  http.xml+=' <txt>'+document.getElementsByTagName('textarea')[0].value+'</txt>\n'
  http.xml+='</root>'
  http.send()
 },

 'write':function()
 {
  http.fml=function(xml)
  {
   if (xml.getElementsByTagName('error')[0]) alert(xml.getElementsByTagName('error')[0].childNodes[0].nodeValue)
   document.getElementsByTagName('textarea')[0].value=xml.getElementsByTagName('root')[0].childNodes[0].data
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <vi>write</vi>\n'
  http.xml+=' <txt>'+document.getElementsByTagName('textarea')[0].value+'</txt>\n'
  http.xml+='</root>'
  http.send()
 }
}

