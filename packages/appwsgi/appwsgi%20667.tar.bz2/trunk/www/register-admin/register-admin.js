// Copyright(c) gert.cuykens@gmail.com
registeradmin=
{

 'select':function()
 {
  http.fml=function(xml)
  {
   var c
   if(c=document.getElementById('cregister'))while(c.lastChild)c.removeChild(c.lastChild)
   register=
   {
    'id':'register',
    'onselect':function()
    {
     document.getElementById('email').value=register.selection[1]
     document.getElementById('name').value=register.selection[2]
     document.getElementById('adress').value=register.selection[3]
     document.getElementById('city').value=register.selection[4]
     document.getElementById('country').value=register.selection[5]
     document.getElementById('phone').value=register.selection[6]
     document.getElementById('uid').value=register.selection[7]
     document.getElementById('gid').value=register.selection[8]
    }
   }
   dg.init(register,xml)
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>select</cmd>\n'
  http.xml+=' <email>'+document.getElementById('email').value+'</email>\n'
  http.xml+=' <name>'+document.getElementById('name').value+'</name>\n'
  http.xml+=' <adress>'+document.getElementById('adress').value+'</adress>\n'
  http.xml+=' <city>'+document.getElementById('city').value+'</city>\n'
  http.xml+=' <country>'+document.getElementById('country').value+'</country>\n'
  http.xml+=' <phone>'+document.getElementById('phone').value+'</phone>\n'
  http.xml+=' <uida>'+document.getElementById('uid').value+'</uida>\n'
  http.xml+=' <gida>'+document.getElementById('gid').value+'</gida>\n'
  http.xml+='</root>'
  http.send()
 },
 
 'update':function()
 {
  http.fml=function(xml)
  {
   if(c=document.getElementById('cregister'))while(c.lastChild)c.removeChild(c.lastChild)
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>update</cmd>\n'
  http.xml+=' <email>'+document.getElementById('email').value+'</email>\n'
  http.xml+=' <name>'+document.getElementById('name').value+'</name>\n'
  http.xml+=' <adress>'+document.getElementById('adress').value+'</adress>\n'
  http.xml+=' <city>'+document.getElementById('city').value+'</city>\n'
  http.xml+=' <country>'+document.getElementById('country').value+'</country>\n'
  http.xml+=' <phone>'+document.getElementById('phone').value+'</phone>\n'
  http.xml+=' <uida>'+document.getElementById('uid').value+'</uida>\n'
  http.xml+=' <gida>'+document.getElementById('gid').value+'</gida>\n'
  http.xml+='</root>'
  http.send()
 },

 'remove':function()
 {
  http.fml=function(xml)
  {
   if(c=document.getElementById('cregister'))while(c.lastChild)c.removeChild(c.lastChild)
   document.getElementById('email').value=''
   document.getElementById('name').value=''
   document.getElementById('adress').value=''
   document.getElementById('city').value=''
   document.getElementById('country').value=''
   document.getElementById('phone').value=''
   document.getElementById('uid').value=''
   document.getElementById('gid').value=''
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>delete</cmd>\n'
  http.xml+=' <uida>'+document.getElementById('uid').value+'</uida>\n'
  http.xml+='</root>'
  http.send()
 }

}

