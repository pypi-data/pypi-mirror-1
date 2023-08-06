// Copyright(c) gert.cuykens@gmail.com

upload=
{

 'progress':function(n,s,t)
 {
  document.getElementById('status').innerHTML="uploading "+n+" "+s+" "+t
 },

 'complete':function(n)
 {
  document.getElementById('status').innerHTML=n+" complete"
 },

 'select':function()
 {
  document.getElementById('status').innerHTML="connecting..."
  document.getElementById('status').style.display="block"
 },

 'cancel':function()
 {
  document.getElementById('status').innerHTML="canceled"
  document.getElementById('status').style.display="none"
 },

 'error':function(e)
 {
  alert(e)
  upload.cancel()
 }

}

