// Copyright(c) gert.cuykens@gmail.com
http=
{
 'xml':'',
 'fml':function(){},
 'url':'',
 'req':'POST',
 'send':function()
 {
  var xmlHttp
  xmlHttp=new XMLHttpRequest()
  xmlHttp.open(http.req,http.url,true)
  xmlHttp.setRequestHeader('Content-Type','text/plain;charset=utf-8')
  xmlHttp.onreadystatechange=function()
  {
   switch(xmlHttp.readyState)
   {
    case 1:
     var v
     if(v=document.getElementById('status')){v.appendChild(document.createTextNode('processing...'));break}
     v=document.createElement('div')
     v.className='status'
     v.id='status'
     v.appendChild(document.createTextNode('processing...'))
     document.body.appendChild(v)
    break
    case 4:
     var v
     if(v=document.getElementById('status')){v.innerHTML=''}
     try{v=JSON.parse(xmlHttp.responseText)}catch(e){alert(e);break}
     if(v.gid=='login'){session.init();break}
     if(v.error){alert(v.error);break}
     http.fml(v)
    break
   }
  }
  xmlHttp.send(http.xml)
 }
}

Http=function()
{
 this.xml=''
 this.fml=function(){}
 this.url=''
 this.req='POST'
 this.send=function()
 {
  XMLHttpRequest.prototype.fml=this.fml
  var xmlHttp=new XMLHttpRequest()
  xmlHttp.open(this.req,this.url,true)
  xmlHttp.setRequestHeader('Content-Type','text/plain;charset=utf-8')
  xmlHttp.onreadystatechange=function()
  {
   switch(xmlHttp.readyState)
   {
    case 1:
     var v
     if (v=document.getElementById('status')){v.appendChild(document.createTextNode('processing...'));break}
     v=document.createElement('div')
     v.className='status'
     v.id='status'
     v.appendChild(document.createTextNode('processing...'))
     document.body.appendChild(v)
    break
    case 4:
     var v
     if(v=document.getElementById('status')){v.innerHTML=''}
     try{v=JSON.parse(xmlHttp.responseText)}catch(e){alert(e);break}
     if(v.gid=='login'){session.init();break}
     if(v.error){alert(v.error);break}
     http.fml(v)
    break
   }
  }
  xmlHttp.send(this.xml)
 }
}
