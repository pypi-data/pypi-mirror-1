// Copyright(c) gert.cuykens@gmail.com
http=
{
 'xml':'',
 'fml':function(){},
 'url':'servlet',
 'asy':false,
 'req':'POST',
 'send':function()
 {
  var xmlHttp
  xmlHttp=new XMLHttpRequest()
  xmlHttp.open(http.req,http.url,http.asy)
  xmlHttp.setRequestHeader('Content-Type','text/xml')
  xmlHttp.onreadystatechange=function()
  {
   switch(xmlHttp.readyState)
   {
    case 1:
     var v
     v=document.createElement('div')
     v.className='status'
     v.id='status'
     v.appendChild(document.createTextNode('processing...'))
     document.body.appendChild(v)
    break
    case 4:
     var v
     if (v=document.getElementById('status')){v.parentNode.removeChild(v)}
     if (xmlHttp.responseXML)
     {
      if(v=xmlHttp.responseXML.getElementsByTagName('error')[0]){alert(v.childNodes[0].nodeValue)}
      else{http.fml(xmlHttp.responseXML)}
     }
    break 
   } 
  } 
  xmlHttp.send(http.xml)
 }
}
   
