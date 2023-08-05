// Copyright(c) gert.cuykens@gmail.com
forum=
{
 'page':'topics',
 'topic':'-1',
 'thread':'-1',
 'message':'-1',

 'newnr':function()
 {
  document.getElementById(forum.page).innerHTML=forum.page
  document.getElementById('nr').value='new'
  if(data)dg.select(data,-1)
 },

 'find':function(v)
 {
  data=''
  if (v) forum.page=v
  http.fml=function(xml)
  {
   var c
   if(c=document.getElementById('cdata'))while(c.lastChild)c.removeChild(c.lastChild)
   switch(forum.page)
   {
    case'topics':
     document.getElementById('topics').innerHTML='topics';
     document.getElementById('threads').innerHTML='threads';
     document.getElementById('messages').innerHTML='messages';
    break;
    case'threads':
     document.getElementById('threads').innerHTML='threads';
     document.getElementById('messages').innerHTML='messages';
    break;
    case'messages':
     document.getElementById('messages').innerHTML='messages';
    break;
   }
   data=
   {
    'id':'data',
    'onselect':function()
    {
     document.getElementById('nr').value=data.selection[2]
     document.getElementById('text').value=data.selection[3]
     document.getElementById(forum.page).innerHTML=forum.page.substring(0,forum.page.length-1)+': '+data.selection[3]
     switch(forum.page)
     {
      case'topics':
       forum.topic=data.selection[2]
       forum.thread='-1'
       forum.message='-1'
      break;
      case'threads':
       forum.thread=data.selection[2]
       forum.message='-1'
      break;
      case'messages':
       forum.message=data.selection[2]
      break;
     }
    }
   }
   dg.init(data,xml)
  }
  var txt=document.getElementById('text').value
  txt=txt.replace(/&/g,'&amp;')
  txt=txt.replace(/</g,'&lt;')
  txt=txt.replace(/>/g,'&gt;')
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>find '+forum.page+'</cmd>\n'
  http.xml+=' <hid>'+forum.topic+'</hid>\n'
  http.xml+=' <tid>'+forum.thread+'</tid>\n'
  http.xml+=' <txt>'+txt+'</txt>\n'
  http.xml+='</root>'
  http.send()
 },
 
 'save':function()
 {
  var cmd
  if(document.getElementById('nr').value=='new'){cmd='insert'}else{cmd='update'}
  http.fml=function(xml)
  {
   if(document.getElementById('nr').value=='new')document.getElementById('nr').value=xml.getElementsByTagName('id')[0].childNodes[0].nodeValue
   if(c=document.getElementById('cdata'))while(c.lastChild)c.removeChild(c.lastChild)
   document.getElementById('nr').value='new'
   document.getElementById('text').value=''
   forum.find()
  }
  var txt=document.getElementById('text').value
  txt=txt.replace(/&/g,'&amp;')
  txt=txt.replace(/</g,'&lt;')
  txt=txt.replace(/>/g,'&gt;')
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>'+cmd+' '+forum.page+'</cmd>\n'
  http.xml+=' <hid>'+forum.topic+'</hid>\n'
  http.xml+=' <tid>'+forum.thread+'</tid>\n'
  http.xml+=' <mid>'+forum.message+'</mid>\n'
  http.xml+=' <txt>'+txt+'</txt>\n'
  http.xml+='</root>'
  http.send()
 },

 'remove':function()
 {
  http.fml=function(xml)
  {
   var c
   document.getElementById('nr').value='new'
   if(c=document.getElementById('cdata'))while(c.lastChild)c.removeChild(c.lastChild)
   document.getElementById('nr').value='new'
   document.getElementById('text').value=''
   document.getElementById(forum.page).value=forum.page
   forum.find()
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>remove '+forum.page+'</cmd>\n'
  http.xml+=' <hid>'+forum.topic+'</hid>\n'
  http.xml+=' <tid>'+forum.thread+'</tid>\n'
  http.xml+=' <mid>'+forum.message+'</mid>\n'
  http.xml+='</root>'
  if(document.getElementById('nr').value!='new'){http.send()}
 },

 'findAll':function()
 {
  http.fml=function(xml)
  {
   forum.page='messages'
   document.getElementById('topics').innerHTML='topics'
   document.getElementById('threads').innerHTML='threads'
   document.getElementById('messages').innerHTML='messages'
   var c=document.getElementById('cdata')
   if(c)while(c.lastChild)c.removeChild(c.lastChild)
   data=
   {
    'id':'data',
    'onselect':function()
    {
     forum.topic=data.selection[1]
     document.getElementById('topics').innerHTML='topic: '+data.selection[2]
     forum.thread=data.selection[3]
     document.getElementById('threads').innerHTML='thread: '+data.selection[4]
     forum.message=data.selection[5]
     document.getElementById('messages').innerHTML='message: '+data.selection[6]
     document.getElementById('nr').value=data.selection[5]
     document.getElementById('text').value=data.selection[6]
    }
   }
   dg.init(data,xml)
  }
  var txt=document.getElementById('text').value
  txt=txt.replace(/&/g,'&amp;')
  txt=txt.replace(/</g,'&lt;')
  txt=txt.replace(/>/g,'&gt;')
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>find all</cmd>\n'
  http.xml+=' <txt>'+txt+'</txt>\n'
  http.xml+='</root>'
  http.send()
 }

}
