// Copyright(c) gert.cuykens@gmail.com
vi=
{
 'read':function()
 {
  http.json=true
  http.fml=function(v){document.getElementById('text').value=v.txt}
  http.xml ='{"cmd":"read",\n'
  http.xml+=' "gid":"admin",\n'
  var p='vi.txt'; try{p=document.URL.match(/\?(.*)/)[1]} catch(e){}
  http.xml+=' "path":"'+p+'"}'
  http.url='vi.wsgi'
  http.send()
 },
 'write':function()
 {
  http.json=true
  http.fml=function(v){document.getElementById('text').value=v.txt}
  http.xml ='{"cmd":"write",\n'
  http.xml+=' "gid":"admin",\n'
  var p='vi.txt'; try{p=document.URL.match(/\?(.*)/)[1]} catch(e){}
  http.xml+=' "path":"'+p+'",\n'
  http.xml+=' "txt":"'+document.getElementById('text').value+'"}'
  http.url='vi.wsgi'
  http.send()
 }
}

