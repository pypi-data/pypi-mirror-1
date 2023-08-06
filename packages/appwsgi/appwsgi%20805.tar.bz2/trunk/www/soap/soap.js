// Copyright(c) gert.cuykens@gmail.com
soap=
{
 'send':function()
 {
  http.fml=function(xml)
  {
   //alert(xml.getElementsByTagName('error')[0].childNodes[0].nodeValue)
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  //http.xml+=' <user>'+ck.get('user')+'</user>\n'
  //http.xml+=' <password>'+ck.get('password')+'</password>\n'
  //http.xml+=' <soap>'+document.getElementById('soap').value+'</soap>\n'
  http.xml+='</root>'
  http.url='soap.py'
  http.send()
 }
}

