// Copyright(c) gert.cuykens@gmail.com
ssh=
{
 'send':function()
 {
  http.fml=function(xml)
  {
   document.getElementById('std').style.display='block'
   document.getElementById('std').innerHTML=xml.getElementsByTagName('root')[0].childNodes[0].data
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <fn>'+document.getElementById('firstname').value+'</fn>\n'
  http.xml+=' <ln>'+document.getElementById('lastname').value+'</ln>\n'
  http.xml+='</root>'
  http.url='ssh.py'
  http.send()
 }
}

