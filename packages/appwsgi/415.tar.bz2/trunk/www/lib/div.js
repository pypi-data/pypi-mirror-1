// Copyright(c) gert.cuykens@gmail.com
div=
{
 'load':function(d,u)
 {
  http.fml=function(xml)
  {
   if(xml.getElementsByTagName('root'))
   {
    var x=xml.getElementsByTagName('root')[0].childNodes[0].data
    d.innerHTML=x
   }
  }
  http.url=u
  http.req='GET'
  http.send()
 }
}

