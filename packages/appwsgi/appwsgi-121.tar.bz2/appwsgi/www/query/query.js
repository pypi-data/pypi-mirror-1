// Copyright(c) gert.cuykens@gmail.com
init=function(){document.getElementById('sql').onblur=function(){query.submit()}}
query=
{
 'submit':function()
 {
  http.xml='{"sql":"'+document.getElementById('sql').value.replace(/\n/g,' ')+'"}'
  http.fml=function(v){dg.init({'id':'result','rec':v.rec,'des':v.des,'onselect':function(){}})}
  http.url='../../wsgi/query.wsgi'
  http.send()
 }
}
