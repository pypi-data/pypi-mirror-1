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
  http.fml=function(v)
  {
   var c
   if(c=document.getElementById('data-dg'))while(c.lastChild)c.removeChild(c.lastChild)
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
    'rec':v['rec'],
    'des':v['des'],
    'onselect':function()
    {
     document.getElementById('nr').value=data.selection[1]
     document.getElementById('text').value=data.selection[2]
     document.getElementById(forum.page).innerHTML=forum.page.substring(0,forum.page.length-1)+': '+data.selection[2]
     switch(forum.page)
     {
      case'topics':
       forum.topic=data.selection[1]
       forum.thread='-1'
       forum.message='-1'
      break;
      case'threads':
       forum.thread=data.selection[1]
       forum.message='-1'
      break;
      case'messages':
       forum.message=data.selection[1]
      break;
     }
    }
   }
   dg.init(data)
  }
  http.xml ='{"cmd":"find '+forum.page+'",\n'
  http.xml+=' "gid":"guest",\n'
  http.xml+=' "hid":"'+forum.topic+'",\n'
  http.xml+=' "tid":"'+forum.thread+'",\n'
  http.xml+=' "txt":"'+document.getElementById('text').value+'"}'
  http.url ='forum.wsgi'
  http.send()
 },
 
 'save':function()
 {
  var cmd
  if(document.getElementById('nr').value=='new'){cmd='insert'}else{cmd='update'}
  http.fml=function(v)
  {
   if(document.getElementById('nr').value=='new')document.getElementById('nr').value=v.id
   if(c=document.getElementById('data-dg'))while(c.lastChild)c.removeChild(c.lastChild)
   document.getElementById('nr').value='new'
   document.getElementById('text').value=''
   forum.find()
  }
  http.xml ='{"cmd":"'+cmd+' '+forum.page+'",\n'
  http.xml+=' "gid":"guest",\n'
  http.xml+=' "hid":"'+forum.topic+'",\n'
  http.xml+=' "tid":"'+forum.thread+'",\n'
  http.xml+=' "mid":"'+forum.message+'",\n'
  http.xml+=' "txt":"'+document.getElementById('text').value+'"}'
  http.url ='forum.wsgi'
  http.send()
 },

 'remove':function()
 {
  http.fml=function(v)
  {
   var c
   document.getElementById('nr').value='new'
   if(c=document.getElementById('data-dg'))while(c.lastChild)c.removeChild(c.lastChild)
   document.getElementById('nr').value='new'
   document.getElementById('text').value=''
   document.getElementById(forum.page).value=forum.page
   forum.find()
  }
  http.xml ='{"cmd":"remove '+forum.page+'",\n'
  http.xml+=' "gid":"guest",\n'
  http.xml+=' "hid":"'+forum.topic+'",\n'
  http.xml+=' "tid":"'+forum.thread+'",\n'
  http.xml+=' "mid":"'+forum.message+'"}'
  http.url ='forum.wsgi'
  if(document.getElementById('nr').value!='new'){http.send()}
 },

 'findAll':function()
 {
  http.fml=function(v)
  {
   forum.page='messages'
   document.getElementById('topics').innerHTML='topics'
   document.getElementById('threads').innerHTML='threads'
   document.getElementById('messages').innerHTML='messages'
   var c=document.getElementById('data-dg')
   if(c)while(c.lastChild)c.removeChild(c.lastChild)
   data=
   {
    'id':'data',
    'rec':v['rec'],
    'des':v['des'],
    'onselect':function()
    {
     forum.topic=data.selection[0]
     document.getElementById('topics').innerHTML='topic: '+data.selection[1]
     forum.thread=data.selection[2]
     document.getElementById('threads').innerHTML='thread: '+data.selection[3]
     forum.message=data.selection[4]
     document.getElementById('messages').innerHTML='message: '+data.selection[5]
     document.getElementById('nr').value=data.selection[4]
     document.getElementById('text').value=data.selection[5]
    }
   }
   dg.init(data)
  }
  http.xml ='{"cmd":"find all",\n'
  http.xml+=' "gid":"guest",\n'
  http.xml+=' "txt":"'+document.getElementById('text').value+'"}'
  http.url ='forum.wsgi'
  http.send()
 }

}

