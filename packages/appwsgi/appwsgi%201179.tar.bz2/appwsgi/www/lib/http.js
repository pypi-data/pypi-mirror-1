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
  xmlHttp.setRequestHeader('Content-Type','text/xml')
  xmlHttp.onreadystatechange=function()
  {
   switch(xmlHttp.readyState)
   {
    case 1:
     var v
     if (v=document.getElementById('status')){v.appendChild(document.createTextNode('processing...'))}
     else
     {
      v=document.createElement('div')
      v.className='status'
      v.id='status'
      v.appendChild(document.createTextNode('processing...'))
      document.body.appendChild(v)
     }
    break
    case 4:
     var v
     if (v=document.getElementById('status')){v.innerHTML=''}
     v=JSON.parse(xmlHttp.responseText)
     if (v.error){alert(v.error)}else{http.fml(v)}
    break 
   } 
  } 
  xmlHttp.send(http.xml)
 }
}

