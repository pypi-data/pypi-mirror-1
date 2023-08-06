// Copyright(c) gert.cuykens@gmail.com
register=
{

 'login':function()
 {
  http.fml=function(xml)
  {

   if(!xml.getElementsByTagName('record')[0])
   {
    alert('wrong password')
    return 0
   }

   var c
   document.getElementById('email').readonly=true
   document.getElementById('email').style.border='2px solid white'
   
   document.getElementById('pwd').readOnly=true
   document.getElementById('pwd').style.border='2px solid white'
   
   document.getElementById('form').appendChild(document.createTextNode('password: '))
   var pwn=document.createElement('input')
   pwn.type='password'
   pwn.id='pwn'
   pwn.value=document.getElementById('pwd').value
   document.getElementById('form').appendChild(pwn)
   document.getElementById('form').appendChild(document.createElement('br'))
   
   document.getElementById('form').appendChild(document.createTextNode('name: '))
   var name=document.createElement('input')
   if(c=xml.getElementsByTagName('name')[0].childNodes[0])name.value=c.nodeValue
   name.id='name'
   document.getElementById('form').appendChild(name)
   document.getElementById('form').appendChild(document.createElement('br'))
   
   document.getElementById('form').appendChild(document.createTextNode('adress: '))
   var adress=document.createElement('input')
   adress.id='adress'
   if(c=xml.getElementsByTagName('adress')[0].childNodes[0])adress.value=c.nodeValue
   document.getElementById('form').appendChild(adress)
   document.getElementById('form').appendChild(document.createElement('br'))
   
   document.getElementById('form').appendChild(document.createTextNode('city: '))
   var city=document.createElement('input')
   city.id='city'
   if(c=xml.getElementsByTagName('city')[0].childNodes[0])city.value=c.nodeValue
   document.getElementById('form').appendChild(city)
   document.getElementById('form').appendChild(document.createElement('br'))
   
   document.getElementById('form').appendChild(document.createTextNode('country:'))
   var country=document.createElement('input')
   country.id='country'
   if(c=xml.getElementsByTagName('country')[0].childNodes[0])country.value=c.nodeValue
   document.getElementById('form').appendChild(country)
   document.getElementById('form').appendChild(document.createElement('br'))
   
   document.getElementById('form').appendChild(document.createTextNode('phone:'))
   var phone=document.createElement('input')
   phone.id='phone'
   if(c=xml.getElementsByTagName('phone')[0].childNodes[0])phone.value=c.nodeValue
   document.getElementById('form').appendChild(phone)
   document.getElementById('form').appendChild(document.createElement('br'))
    
   if(c=document.getElementById('menu'))while(c.lastChild)c.removeChild(c.lastChild)
   
   var remove=document.createElement('input')
   remove.type='button'
   remove.id='delete'
   remove.value='remove'
   remove.onclick=function(){register.remove()}
   document.getElementById('menu').appendChild(remove)
   
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

   var img=document.createElement('img')
   img.id='picture'
   img.src='../download/download.py?picture='+Math.random()
   img.onclick=function()
   {
    if(document.getElementById('iframe'))document.getElementById('iframe').parentNode.removeChild(document.getElementById('iframe'))
    var obj=document.createElement('object')
    obj.id='iframe'
    obj.data='../upload/upload.htm'
    document.body.appendChild(obj)
   }
   document.body.appendChild(img)

   link=['appointment','forum','order']
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
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>login</cmd>\n'
  http.xml+=' <email>'+document.getElementById('email').value+'</email>\n'
  http.xml+=' <pwd>'+sha1.msg(document.getElementById('pwd').value)+'</pwd>\n'
  http.xml+='</root>'
  http.url='register.py'
  if(document.getElementById('email').value)http.send()
 },
 
 'update':function()
 {
  http.fml =function(xml){document.getElementById('pwd').value=document.getElementById('pwn').value}
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>update</cmd>\n'
  http.xml+=' <email>'+document.getElementById('email').value+'</email>\n'
  http.xml+=' <pwd>'+sha1.msg(document.getElementById('pwd').value)+'</pwd>\n'
  http.xml+=' <pwn>'+sha1.msg(document.getElementById('pwn').value)+'</pwn>\n'
  http.xml+=' <name>'+document.getElementById('name').value+'</name>\n'
  http.xml+=' <adress>'+document.getElementById('adress').value+'</adress>\n'
  http.xml+=' <city>'+document.getElementById('city').value+'</city>\n'
  http.xml+=' <country>'+document.getElementById('country').value+'</country>\n'
  http.xml+=' <phone>'+document.getElementById('phone').value+'</phone>\n'
  http.xml+='</root>'
  http.url='register.py'
  if(document.getElementById('email').value)http.send()
 },

 'remove':function()
 {
  http.fml=function(xml)
  {
   document.location='register.htm';
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>delete</cmd>\n'
  http.xml+=' <email>'+document.getElementById('email').value+'</email>\n'
  http.xml+=' <pwd>'+sha1.msg(document.getElementById('pwd').value)+'</pwd>\n'
  http.xml+='</root>'
  http.url='register.py'
  if(document.getElementById('email').value)http.send()
 },
 
 'logout':function()
 {
  http.fml=function(xml)
  {
   document.location='register.htm';
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>logout</cmd>\n'
  http.xml+=' <email></email>\n'
  http.xml+=' <pwd></pwd>\n'
  http.xml+='</root>'
  http.url='register.py'
  http.send()
 }

}
