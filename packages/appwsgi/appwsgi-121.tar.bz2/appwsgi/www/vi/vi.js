// Copyright(c) gert.cuykens@gmail.com
init=function()
{
 document.getElementsByTagName('textarea')[0].style.height=document.body.clientHeight-25+'px'
 vi.read()
}

vi=
{
 'read':function()
 {
  var p='vi.txt'; try{p=document.URL.match(/\?(.*)/)[1]}catch(e){}
  http.fml =function(v){document.getElementById('text').value=v.txt}
  http.xml ='{"cmd":"read",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"admin",\n'
  http.xml+=' "path":"'+p+'"}'
  http.url ='../../wsgi/vi.wsgi'
  http.req ='POST'
  http.send()
 },
 'write':function()
 {
  var p='vi.txt'; try{p=document.URL.match(/\?(.*)/)[1]}catch(e){}
  http.fml =function(v){document.getElementById('text').value=v.txt}
  http.xml ='{"cmd":"write",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"admin",\n'
  http.xml+=' "path":"'+p+'",\n'
  http.xml+=' "txt":"'+document.getElementById('text').value+'"}'
  http.url ='../../wsgi/vi.wsgi'
  http.req ='POST'
  http.send()
 }
}
