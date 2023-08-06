// Copyright(c) gert.cuykens@gmail.com
smtp=
{
 'send':function()
 {
  http.fml=function(xml)
  {
   //alert(xml.getElementsByTagName('error')[0].childNodes[0].nodeValue)
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <user>'+document.getElementById('user').value+'</user>\n'
  http.xml+=' <password>'+document.getElementById('password').value+'</password>\n'
  http.xml+=' <to>'+document.getElementById('to').value+'</to>\n'
  http.xml+=' <subject>'+document.getElementById('subject').value+'</subject>\n'
  http.xml+=' <message>'+document.getElementById('message').value+'</message>\n'
  http.xml+='</root>'
  http.send()
 }
}

