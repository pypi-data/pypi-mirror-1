// Copyright(c) gert.cuykens@gmail.com
ck=
{

 'set':function(n,v)
 {
  var d= new Date((new Date().setDate(new Date().getDate()+1))).toGMTString()
  document.cookie=n+"="+escape(v)+";expires="+d+";path=/;"
 },

 'get':function(n)
 {
  var e = new RegExp(n+"=(.*?)(?:;|$)")
  if(document.cookie.match(e))return unescape(document.cookie.match(e)[1])
 }

}

