// Copyright(c) gert.cuykens@gmail.com
register=
{

 'session':function(cmd)
 {

  http.fml=function(v)
  {

   if(!v['rec'][0]){alert('Access denied!');return 0}
   document.getElementById('form').innerHTML=''

   document.getElementById('form').appendChild(document.createTextNode('name: '))
   var name=document.createElement('input')
   name.id='name'
   name.value=v['rec'][0][1]
   document.getElementById('form').appendChild(name)
   document.getElementById('form').appendChild(document.createElement('br'))
   
   document.getElementById('form').appendChild(document.createTextNode('adress: '))
   var adress=document.createElement('input')
   adress.id='adress'
   adress.value=v['rec'][0][2]
   document.getElementById('form').appendChild(adress)
   document.getElementById('form').appendChild(document.createElement('br'))
   
   document.getElementById('form').appendChild(document.createTextNode('city: '))
   var city=document.createElement('input')
   city.id='city'
   city.value=v['rec'][0][3]
   document.getElementById('form').appendChild(city)
   document.getElementById('form').appendChild(document.createElement('br'))
   
   document.getElementById('form').appendChild(document.createTextNode('country:'))
   var country=document.createElement('input')
   country.id='country'
   country.value=v['rec'][0][4]
   document.getElementById('form').appendChild(country)
   document.getElementById('form').appendChild(document.createElement('br'))
   
   document.getElementById('form').appendChild(document.createTextNode('phone:'))
   var phone=document.createElement('input')
   phone.id='phone'
   phone.value=v['rec'][0][5]
   document.getElementById('form').appendChild(phone)
   document.getElementById('form').appendChild(document.createElement('br'))
    
   if(c=document.getElementById('menu'))while(c.lastChild)c.removeChild(c.lastChild)
   
   var del=document.createElement('input')
   del.type='button'
   del.id='delete'
   del.value='delete'
   del.onclick=function(){register.del()}
   document.getElementById('menu').appendChild(del)
   
   var update=document.createElement('input')
   update.type='button'
   update.id='update'
   update.value='save'
   update.onclick=function(){register.update()}
   document.getElementById('menu').appendChild(update)
 
   var logout=document.createElement('input')
   logout.type='button'
   logout.id='logout'
   logout.value='logout'
   logout.onclick=function(){register.logout()}
   document.getElementById('menu').appendChild(logout)

   var passwd=document.createElement('input')
   passwd.type='button'
   passwd.id='passwd'
   passwd.value='change password'
   passwd.onclick=function(){register.passwd()}
   document.getElementById('menu').appendChild(passwd)

   var obj=document.createElement('object')
   obj.id='picture'
   obj.style.background='url(../lib/download.wsgi?picture='+Math.random()+') no-repeat'
   obj.type="application/x-shockwave-flash"
   obj.data="../lib/upload.swf?url=../lib/upload.wsgi"
   var param = document.createElement("param");
   param.setAttribute('name','movie');
   param.setAttribute('value','../lib/upload.swf?url=../lib/upload.wsgi');
   obj.appendChild(param) 
   param = document.createElement("param");
   param.setAttribute('name','allowScriptAccess');
   param.setAttribute('value','always');
   obj.appendChild(param)
   param = document.createElement("param");
   param.setAttribute('name','wmode');
   param.setAttribute('value','transparent');
   obj.appendChild(param)
   document.body.appendChild(obj)

   link=['appointment','forum','shop']
   for(i in link)
   {
    var l=document.createElement('a')
    l.id=link[i]
    l.href='../'+link[i]+'/'+link[i]+'.htm'
    l.appendChild(document.createTextNode(link[i]))
    document.getElementById('links').appendChild(l)
    document.getElementById('links').appendChild(document.createElement('br'))
   }

  }
  http.xml ='{"cmd":"'+cmd+'",\n'
  if (cmd=='login')
  {
   http.xml+=' "uid":"'+document.getElementById('uid').value+'",\n'
   http.xml+=' "pwd":"'+sha1.msg(document.getElementById('pwd').value)+'",\n'
  }
  http.xml+=' "gid":"guest"}'
  http.url ='register.wsgi'
  if(document.getElementById('uid').value || document.cookie)http.send()
 },
 
 'update':function()
 {
  http.fml =function(xml){}
  http.xml ='{"cmd":"update",\n'
  http.xml+=' "gid":"guest",\n'
  http.xml+=' "name":"'+document.getElementById('name').value+'",\n'
  http.xml+=' "adress":"'+document.getElementById('adress').value+'",\n'
  http.xml+=' "city":"'+document.getElementById('city').value+'",\n'
  http.xml+=' "country":"'+document.getElementById('country').value+'",\n'
  http.xml+=' "phone":"'+document.getElementById('phone').value+'"}\n'
  http.url ='register.wsgi'
  http.send()
 },

 'del':function()
 {
  http.fml=function(xml)
  {
   var t=new Date()
   t.setDate(t.getDate()-1)
   document.cookie="SID=; expires="+t.toGMTString()+"; path=/"
   window.location='register.htm'
  }
  http.xml ='{"cmd":"delete",\n'
  http.xml+=' "gid":"guest"}'
  http.url ='register.wsgi'
  http.send()
 },
 
 'logout':function()
 {
  http.fml =function(xml){window.location='register.htm'}
  http.xml ='{"cmd":"logout",\n'
  http.xml+=' "gid":"guest"}\n'
  http.url ='register.wsgi'
  http.send()
 },

 'passwd':function()
 {
  var pwd=prompt('Please enter password')
  if (pwd==''||pwd==null) return 0
  http.fml =function(xml){}
  http.xml ='{"cmd":"passwd",\n'
  http.xml+=' "gid":"guest",\n'
  http.xml+=' "pwd":"'+sha1.msg(pwd)+'"}'
  http.url ='register.wsgi'
  http.send()
 }

}

upload=
{

 'progress':function(n,s,t)
 {
  document.getElementById('status').innerHTML="uploading "+n+" "+s+" "+t
 },

 'complete':function(n)
 {
  document.getElementById('status').innerHTML=n+" complete"
  document.getElementById('picture').style.background='url(../lib/download.wsgi?picture='+Math.random()+') no-repeat'
 },

 'select':function()
 {
  document.getElementById('status').innerHTML="connecting..."
  document.getElementById('status').style.display="block"
 },

 'cancel':function()
 {
  document.getElementById('status').innerHTML="canceled"
  document.getElementById('status').style.display="none"
 },

 'error':function(e)
 {
  alert(e)
  upload.cancel()
 }

}

