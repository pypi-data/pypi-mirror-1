// Copyright(c) gert.cuykens@gmail.com
init=function()
{
 user.select()
 document.getElementById('picture').style.background='url(../../wsgi/download.wsgi?'+session.sid+Math.random()+') no-repeat'
}
 
user=
{
 'select':function(cmd)
 {
  http.fml=function(v)
  {
   document.getElementById('email').value=v['rec'][0][0]
   document.getElementById('name').value=v['rec'][0][1]
   document.getElementById('adress').value=v['rec'][0][2]
   document.getElementById('city').value=v['rec'][0][3]
   document.getElementById('country').value=v['rec'][0][4]
   document.getElementById('phone').value=v['rec'][0][5]
  }
  http.xml ='{"cmd":"select",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"guest"}'
  http.url ='../../wsgi/user.wsgi'
  http.req ='POST'
  http.send()
 },

 'update':function()
 {
  http.fml =function(v){}
  http.xml ='{"cmd":"update",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"guest",\n'
  http.xml+=' "name":"'+document.getElementById('name').value+'",\n'
  http.xml+=' "adress":"'+document.getElementById('adress').value+'",\n'
  http.xml+=' "city":"'+document.getElementById('city').value+'",\n'
  http.xml+=' "country":"'+document.getElementById('country').value+'",\n'
  http.xml+=' "phone":"'+document.getElementById('phone').value+'"}\n'
  http.url ='../../wsgi/user.wsgi'
  http.req ='POST'
  http.send()
 },

 'del':function()
 {
  http.fml=function(v){}
  http.xml ='{"cmd":"delete",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"guest"}'
  http.url ='../../wsgi/user.wsgi'
  http.req ='POST'
  http.send()
 },

 'passwd':function()
 {
  var pwd=prompt('Please enter password')
  if (pwd==''||pwd==null) return 0
  http.fml =function(v){}
  http.xml ='{"cmd":"passwd",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"guest",\n'
  http.xml+=' "pwd":"'+sha1.msg(pwd)+'"}'
  http.url ='../../wsgi/user.wsgi'
  http.req ='POST'
  http.send()
 },

 'email':function()
 {
  var email=prompt('Please enter new email')
  if (email==''||email==null) return 0
  http.fml=function(v){document.getElementById('email').value=v['rec'][0][0]}
  http.xml ='{"cmd":"email",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"guest",\n'
  http.xml+=' "uid":"'+email+'"}'
  http.url ='../../wsgi/user.wsgi'
  http.req ='POST'
  http.send()
 }
}

upload=
{
 'progress':function(n,s,t){document.getElementById('status').innerHTML="uploading "+n+" "+s+" "+t},
 'complete':function(n){document.getElementById('status').innerHTML=n+" complete";document.getElementById('picture').style.background='url(../../wsgi/download.wsgi?'+session.sid+Math.random()+') no-repeat'},
 'select':function(){document.getElementById('status').innerHTML="connecting...";document.getElementById('status').style.display="block";return session.sid},
 'cancel':function(){document.getElementById('status').innerHTML="canceled";document.getElementById('status').style.display="none"},
 'error':function(v){alert(v)},
 'server':function(v){try{v=JSON.parse(v);if(v.gid=='login'){session.init()}if(v.error){alert(v.error)}}catch(e){alert(e)}}
}

