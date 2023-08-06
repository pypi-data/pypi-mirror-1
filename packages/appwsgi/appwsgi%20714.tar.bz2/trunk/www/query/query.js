// Copyright(c) gert.cuykens@gmail.com
query=
{ 

 'submit':function()
 {
  var server=document.getElementById('server').value
  var user=document.getElementById('user').value
  var password=document.getElementById('password').value
  var database=document.getElementById('database').value
  var sql=document.getElementById('sql').value
  sql=sql+''
  sql=sql.replace(/&/g,'&amp;')
  sql=sql.replace(/</g,'&lt;')
  sql=sql.replace(/>/g,'&gt;')
  http.xml ='<?xml version="1.0" encoding="UTF-8" ?>\n'
  http.xml+='<root>\n'
  http.xml+=' <server>'+server+'</server>\n'
  http.xml+=' <user>'+user+'</user>\n'
  http.xml+=' <password>'+password+'</password>\n'
  http.xml+=' <database>'+database+'</database>\n'
  http.xml+=' <sql>'+sql+'</sql>\n'
  http.xml+='</root>'
  http.fml=function(xml)
  {
   var v
   if ( v=document.getElementById('result') ) v.parentNode.removeChild(v)
   result={'id':'result','onselect':function(){}}
   dg.init(result,xml)
  }
  http.url='query.py'
  http.send()
 }

}
