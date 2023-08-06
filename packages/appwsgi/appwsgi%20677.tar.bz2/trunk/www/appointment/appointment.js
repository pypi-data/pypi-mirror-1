// Copyright(c) gert.cuykens@gmail.com
appointment=
{
 'name':function()
 {
  http.fml=function(xml)
  {
   document.getElementById('cappointments').innerHTML=''
   appointments=
   {
    'id':'appointments',
    'onselect':function()
    {
     document.getElementById('uid').value=appointments.selection[1]
     appointment.ca()
    }
   }
   dg.init(appointments,xml)
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>name</cmd>\n'
  http.xml+=' <name>'+document.getElementById('appointment').value+'</name>\n'
  http.xml+='</root>'
  http.send()
 },

 'ca':function()
 {
  http.fml=function(xml)
  {
   document.getElementById('cappointments').innerHTML=''
   appointments=
   {
    'id':'appointments',
    'onselect':function()
    {
     document.getElementById('uid').value=appointments.selection[2]
     document.getElementById('aid').value=appointments.selection[3]
     document.getElementById('calendar').value=appointments.selection[4]
     document.getElementById('appointment').value=appointments.selection[5]
     if(appointments.selection[4]=='None')document.getElementById('calendar').value='0000-00-00 00:00:00'
     calendar.display()
    }
   }
   dg.init(appointments,xml)
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>ca</cmd>\n'
  http.xml+=' <uid>'+document.getElementById('uid').value+'</uid>\n'
  http.xml+=' <calendar>'+document.getElementById('calendar').value+'</calendar>\n'
  http.xml+='</root>'
  http.send()
 },

 'find':function()
 {
  http.fml=function(xml)
  {
   document.getElementById('cappointments').innerHTML=''
   appointments=
   {
    'id':'appointments',
    'onselect':function()
    {
     document.getElementById('uid').value=appointments.selection[2]
     document.getElementById('aid').value=appointments.selection[3]
     document.getElementById('calendar').value=appointments.selection[4]
     document.getElementById('appointment').value=appointments.selection[5]
     if(appointments.selection[4]=='None')document.getElementById('calendar').value='0000-00-00 00:00:00'
     calendar.display()
    }
   }
   dg.init(appointments,xml)
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>find</cmd>\n'
  http.xml+=' <calendar>'+document.getElementById('calendar').value+'</calendar>\n'
  http.xml+=' <appointment>'+document.getElementById('appointment').value+'</appointment>\n'
  http.xml+='</root>'
  http.send()
 },
 
 'save':function()
 {
  var cmd
  if(document.getElementById('aid').value=='new'){cmd='insert'}else{cmd='update'}
  http.fml=function(xml)
  {
   if(document.getElementById('aid').value=='new')document.getElementById('aid').value=xml.getElementsByTagName('id')[0].childNodes[0].nodeValue
   if(c=document.getElementById('cappointments'))while(c.lastChild)c.removeChild(c.lastChild)
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>'+cmd+'</cmd>\n'
  http.xml+=' <aid>'+document.getElementById('aid').value+'</aid>\n'
  http.xml+=' <uid>'+document.getElementById('uid').value+'</uid>\n'
  http.xml+=' <calendar>'+document.getElementById('calendar').value+'</calendar>\n'
  http.xml+=' <appointment>'+document.getElementById('appointment').value+'</appointment>\n'
  http.xml+='</root>'
  http.send()
 },

 'remove':function()
 {
  http.fml=function(xml)
  {
   document.getElementById('aid').value='new'
   document.getElementById('appointment').value=''
   if(c=document.getElementById('appointments'))while(c.lastChild)c.removeChild(c.lastChild)
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>remove</cmd>\n'
  http.xml+=' <aid>'+document.getElementById('aid').value+'</aid>\n'
  http.xml+='</root>'
  if(document.getElementById('aid').value!='new'){http.send()}
 }
}
