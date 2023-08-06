// Copyright(c) gert.cuykens@gmail.com
vi=
{
 'read':function()
 {
  http.fml=function(xml)
  {
   if (xml.getElementsByTagName('error')[0]) alert(xml.getElementsByTagName('error')[0].childNodes[0].nodeValue)
   document.getElementById('text').value=xml.getElementsByTagName('root')[0].childNodes[0].data
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>read</cmd>\n'
  http.xml+=' <gid>admin</gid>\n'
  var p='vi.txt'; try{p=document.URL.match(/\?(.*)/)[1]} catch(e){}
  http.xml+=' <path>'+p+'</path>\n'
  http.xml+='</root>'
  http.url='vi.py'
  http.send()
 },

 'write':function()
 {
  http.fml=function(xml)
  {
   if (xml.getElementsByTagName('error')[0]) alert(xml.getElementsByTagName('error')[0].childNodes[0].nodeValue)
   document.getElementById('text').value=xml.getElementsByTagName('root')[0].childNodes[0].data
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>write</cmd>\n'
  http.xml+=' <gid>admin</gid>\n'
  var p='vi.txt'; try{p=document.URL.match(/\?(.*)/)[1]} catch(e){}
  http.xml+=' <path>'+p+'</path>\n'
  http.xml+=' <txt>'+document.getElementById('text').value+'</txt>\n'
  http.xml+='</root>'
  http.url='vi.py'
  http.send()
 }
}

