// Copyright(c) gert.cuykens@gmail.com
init=function()
{
 calendar.pickTodaysDate()
 window.onresize=function()
 {
  document.getElementById('appointment').style.width=document.body.offsetWidth-289+'px';
  document.getElementById('appointments-dg').style.width=document.body.offsetWidth+'px';
  document.getElementById('appointments-dg').style.height=document.body.offsetHeight-177+'px';
 }
 window.onresize()
}

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
     document.getElementById('nid').value=appointments.selection[0]
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
        document.getElementById('nid').value=appointments.selection[1]
        document.getElementById('aid').value=appointments.selection[3]
        calendar.set(appointments.selection[4])
        document.getElementById('appointment').value=appointments.selection[5]
        calendar.display()
       }
      }
      dg.init(appointments)
     }
     http.xml ='{"cmd":"ca",\n'
     http.xml+=' "sid":"'+session.sid+'",\n'
     http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
     http.xml+=' "uid":"'+document.getElementById('nid').value+'",\n'
     http.xml+=' "calendar":"'+calendar.get()+'",\n'
     http.xml+=' "appointment":"'+document.getElementById('appointment').value+'"}'
     http.url ='../../wsgi/appointment.wsgi'
     http.send()
    }
   }
   dg.init(appointments)
  }
  http.xml ='{"cmd":"name",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
  http.xml+=' "name":"'+document.getElementById('appointment').value+'"}'
  http.url ='../../wsgi/appointment.wsgi'
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
     document.getElementById('nid').value=appointments.selection[1]
     document.getElementById('aid').value=appointments.selection[3]
     calendar.set(appointments.selection[4])
     document.getElementById('appointment').value=appointments.selection[5]
     calendar.display()
    }
   }
   dg.init(appointments)
  }
  http.xml ='{"cmd":"find",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
  http.xml+=' "calendar":"'+calendar.get()+'",\n'
  http.xml+=' "appointment":"'+document.getElementById('appointment').value+'"}'
  http.url ='../../wsgi/appointment.wsgi'
  http.send()
 },
 
 'save':function()
 {
  var cmd
  if(document.getElementById('aid').value=='new'){cmd='insert'}else{cmd='update'}
  http.fml=function(v)
  {
   if(document.getElementById('aid').value=='new')document.getElementById('aid').value=v['row']
   document.getElementById('appointments-dg').innerHTML=''
  }
  http.xml ='{"cmd":"'+cmd+'",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
  http.xml+=' "aid":"'+document.getElementById('aid').value+'",\n'
  http.xml+=' "uid":"'+document.getElementById('nid').value+'",\n'
  http.xml+=' "calendar":"'+calendar.get()+'",\n'
  http.xml+=' "appointment":"'+document.getElementById('appointment').value+'"}'
  http.url ='../../wsgi/appointment.wsgi'
  http.send()
 },

 'remove':function()
 {
  http.fml=function(v)
  {
   document.getElementById('aid').value='new'
   document.getElementById('appointment').value=''
   document.getElementById('appointments-dg').innerHTML=''
  }
  http.xml ='{"cmd":"remove",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"'+document.getElementById('view').innerHTML+'",\n'
  http.xml+=' "aid":"'+document.getElementById('aid').value+'"}'
  http.url ='../../wsgi/appointment.wsgi'
  if(document.getElementById('aid').value!='new'){http.send()}
 }
}

