// Copyright(c) gert.cuykens@gmail.com
appointment=
{
 'name':function()
 {
  http.fml=function(v)
  {
   document.getElementById('appointments-dg').innerHTML=''
   appointments=
   {
    'id':'appointments',
    'rec':v['rec'],
    'des':v['des'],
    'onselect':function()
    {
     document.getElementById('uid').value=appointments.selection[0]
     appointment.ca()
    }
   }
   dg.init(appointments)
  }
  http.xml ='{"cmd":"name",\n'
  http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
  http.xml+=' "name":"'+document.getElementById('appointment').value+'"}\n'
  http.url ='appointment.wsgi'
  http.send()
 },

 'ca':function()
 {
  http.fml=function(v)
  {
   document.getElementById('appointments-dg').innerHTML=''
   appointments=
   {
    'id':'appointments',
    'rec':v['rec'],
    'des':v['des'],
    'onselect':function()
    {
     document.getElementById('uid').value=appointments.selection[1]
     document.getElementById('aid').value=appointments.selection[2]
     document.getElementById('calendar').value=appointments.selection[3]
     document.getElementById('appointment').value=appointments.selection[4]
     if(appointments.selection[3]=='None')document.getElementById('calendar').value='0000-00-00 00:00:00'
     calendar.display()
    }
   }
   dg.init(appointments)
  }
  http.xml ='{"cmd":"ca",\n'
  http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
  http.xml+=' "uid":"'+document.getElementById('uid').value+'",\n'
  http.xml+=' "calendar":"'+document.getElementById('calendar').value+'",\n'
  http.xml+=' "appointment":"'+document.getElementById('appointment').value+'"}\n'
  http.url ='appointment.wsgi'
  http.send()
 },

 'find':function()
 {
  http.fml=function(v)
  {
   document.getElementById('appointments-dg').innerHTML=''
   appointments=
   {
    'id':'appointments',
    'rec':v['rec'],
    'des':v['des'],
    'onselect':function()
    {
     document.getElementById('uid').value=appointments.selection[1]
     document.getElementById('aid').value=appointments.selection[2]
     document.getElementById('calendar').value=appointments.selection[3]
     document.getElementById('appointment').value=appointments.selection[4]
     if(appointments.selection[3]=='None')document.getElementById('calendar').value='0000-00-00 00:00:00'
     calendar.display()
    }
   }
   dg.init(appointments)
  }
  http.xml ='{"cmd":"find",\n'
  http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
  http.xml+=' "calendar":"'+document.getElementById('calendar').value+'",\n'
  http.xml+=' "appointment":"'+document.getElementById('appointment').value+'"}\n'
  http.url ='appointment.wsgi'
  http.send()
 },
 
 'save':function()
 {
  var cmd
  if(document.getElementById('aid').value=='new'){cmd='insert'}else{cmd='update'}
  http.fml=function(v)
  {
   document.getElementById('appointments-dg').innerHTML=''
   if(document.getElementById('aid').value=='new')document.getElementById('aid').value=v['rid']
  }
  http.xml ='{"cmd":"'+cmd+'",\n'
  http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
  http.xml+=' "aid":"'+document.getElementById('aid').value+'",\n'
  http.xml+=' "uid":"'+document.getElementById('uid').value+'",\n'
  http.xml+=' "calendar":"'+document.getElementById('calendar').value+'",\n'
  http.xml+=' "appointment":"'+document.getElementById('appointment').value+'"}\n'
  http.url ='appointment.wsgi'
  http.send()
 },

 'remove':function()
 {
  http.fml=function(v)
  {
   document.getElementById('aid').value='new'
   document.getElementById('appointment').value=''
   if(c=document.getElementById('appointments'))while(c.lastChild)c.removeChild(c.lastChild)
  }
  http.xml ='{"cmd":"remove",\n'
  http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
  http.xml+=' "aid":"'+document.getElementById('aid').value+'"}'
  http.url ='appointment.wsgi'
  if(document.getElementById('aid').value!='new'){http.send()}
 }
}

