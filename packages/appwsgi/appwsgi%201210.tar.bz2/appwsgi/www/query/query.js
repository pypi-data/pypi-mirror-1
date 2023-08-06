// Copyright(c) gert.cuykens@gmail.com
query=
{ 
 'submit':function()
 {
  http.xml='{"sql":"'+document.getElementById('sql').value+'"}\n'
  http.fml=function(v){dg.init({'id':'result','rec':v.rec,'des':v.des,'onselect':function(){}})}
  http.url='query.wsgi'
  http.send()
 }
}

