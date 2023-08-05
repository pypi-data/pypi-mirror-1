// Copyright(c) gert.cuykens@gmail.com
map=
{

 'close':function()
 {
  this.nextSibling.nextSibling.style.display='none'
  this.innerHTML=this.innerHTML.replace(/^./,'+')
  this.onclick=map.open
 },

 'open':function()
 {
  this.nextSibling.nextSibling.style.display=''
  this.innerHTML=this.innerHTML.replace(/^./,'-')
  this.onclick=map.close
 },

 'init':function()
 {
  x=document.getElementsByTagName('span')
  for (i in x)
  {
   x[i].onclick=map.close
   x[i].innerHTML='- '+x[i].innerHTML
  }
 },

 'search':function(v){document.location='http://www.google.com/search?sitesearch=www.w3schools.com&as_q='+v}

}

