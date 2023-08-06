// Copyright(c) gert.cuykens@gmail.com
session=
{
 'sid':document.cookie,
 'init':function()
 {
  document.cookie=''
  session.sid=''
  var login=document.createElement('div')
  var l;if(l=document.getElementById('login'))login=l
  login.id='login'
  login.style.display='block'
  login.innerHTML='\
<div id="shadow"/>\
<div id="main">\
 <div id="s1"/>\
 <div id="s2"/>\
 <div id="s3"/>\
 <div id="s4"/>\
 <div id="s5"/>\
 <div id="s6"/>\
 <div id="s7"/>\
 <div id="s8"/>\
 email:    <input id="uid"  type="text"     value=""/><br/>\
 password: <input id="pwd"  type="password" value=""/><br/>\
 <input id="sid" type="button" value="login" onclick="session.login()"/>\
</div>'
  document.body.appendChild(login)
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
 },

 'login':function()
 {
  http.fml=function(v)
  {
   if(v.gid=='login'){if(confirm('Access denied, mail password?')){session.mailpwd()}return 0}
   session.sid=v.sid
   document.cookie=v.sid
   document.getElementById('login').parentNode.removeChild(document.getElementById('login'))
   init()
  }
  http.xml ='{"cmd":"login",\n'
  http.xml+=' "sid":"",\n'
  http.xml+=' "uid":"'+document.getElementById('uid').value+'",\n'
  http.xml+=' "pwd":"'+sha1.msg(document.getElementById('pwd').value)+'",\n'
  http.xml+=' "gid":"guest"}'
  http.url ='../../wsgi/user.wsgi'
  http.req='POST'
  if(document.getElementById('uid').value)http.send()
 },

 'logout':function()
 {
  http.fml =function(v){}
  http.xml ='{"cmd":"logout",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"guest"}'
  http.url ='../../wsgi/user.wsgi'
  http.req='POST'
  http.send()
 },

 'mailpwd':function()
 {
  http.fml =function(v){}
  http.xml ='{"cmd":"mailpwd",\n'
  http.xml+=' "sid":"",\n'
  http.xml+=' "gid":"login",\n'
  http.xml+=' "uid":"'+document.getElementById('uid').value+'"}'
  http.url ='../../wsgi/user.wsgi'
  http.req='POST'
  http.send()
 }
}
