// Copyright(c) gert.cuykens@gmail.com
session=
{
 'init':function(auto)
 {
  var s=document.getElementById('session')
  if(!s){s=document.createElement('input');document.body.appendChild(s)}
  s.id='session'
  s.style.display='inline'
  s.type='button'
  s.value='logout'
  s.onclick=function(){session.logout()}
  if(document.cookie)return 0
  s.value='login'
  s.onclick=function(){session.init(true)}
  if(auto==false)return 0
  s.value='logout'
  s.onclick=function(){session.logout()}
  http.fml=function(v)
  {
   var login=document.getElementById('login')
   if(!login){login=document.createElement('div');document.body.appendChild(login)}
   login.id='login'
   login.style.display='block'
   login.innerHTML=v
   var s1=document.getElementById('s1')
   var s2=document.getElementById('s2')
   var s3=document.getElementById('s3')
   var s4=document.getElementById('s4')
   var s5=document.getElementById('s5')
   var s6=document.getElementById('s6')
   var s7=document.getElementById('s7')
   var s8=document.getElementById('s8')
   var main=document.getElementById('main')
   shader.sthread(main,s1,s2,s3,s4,s5,s6,s7,s8)
   center.obj(login)
   window.onresize=function(){if(login=document.getElementById('login'))center.obj(login)}
  }
  http.url='../lib/session.htm'
  http.req='GET'
  http.send()
 },
 'login':function()
 {
  http.fml=function(v)
  {
   if(!document.cookie){alert('Access denied!');return 0}
   window.location=window.location
  }
  http.xml ='{"cmd":"login",\n'
  http.xml+=' "uid":"'+document.getElementById('uid').value+'",\n'
  http.xml+=' "pwd":"'+sha1.msg(document.getElementById('pwd').value)+'",\n'
  http.xml+=' "gid":"guest"}'
  http.url ='../lib/session.wsgi'
  http.req='POST'
  if(document.getElementById('uid').value)http.send()
 },
 'logout':function()
 {
  http.fml =function(v){window.location=window.location}
  http.xml ='{"cmd":"logout",\n'
  http.xml+=' "gid":"guest"}'
  http.url ='../lib/session.wsgi'
  http.req='POST'
  http.send()
 }
}
