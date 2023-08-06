// Copyright(c) gert.cuykens@gmail.com
fx=
{

 's':function(v)
 {
  var i
  for(i in v)
  {
   var sc=document.createElement('div')
   sc.style.margin="32px 32px 32px 32px"
   document.getElementById(v[i]).parentNode.insertBefore(sc,document.getElementById(v[i]))
   document.getElementById(v[i]).style.background='#b0b0b0'
  
   var s1=document.createElement('div')
   var s2=document.createElement('div')
   var s3=document.createElement('div')
   var s4=document.createElement('div')
   var s5=document.createElement('div')
   var s6=document.createElement('div')
   var s7=document.createElement('div')
   var s8=document.createElement('div')

   s1.id='s1'+i
   s2.id='s2'+i
   s3.id='s3'+i
   s4.id='s4'+i
   s5.id='s5'+i
   s6.id='s6'+i
   s7.id='s7'+i
   s8.id='s8'+i

   sc.appendChild(s1)
   sc.appendChild(s2)
   sc.appendChild(s3)
   sc.appendChild(s4)
   sc.appendChild(s5)
   sc.appendChild(s6)  
   sc.appendChild(s7)
   sc.appendChild(s8)
   sc.appendChild(document.getElementById(v[i]))
  }
  shader.sthread(v);
 },

 'c':function(v)
 {
  var obj=document.getElementById(v[0]).childNodes
  var i,t=0
  var o=[]
  for(i in obj)
  {
   if(obj[i].nodeType==1)
   {
    o[t]=obj[i].childNodes[0]
    o[t].style.color='rgb(0,0,0)'
    t++
   }
  }
  setTimeout(function(){shader.cthread(o[0],255,0,0)},500)
  setTimeout(function(){shader.cthread(o[1],255,0,0)},1000)
  setTimeout(function(){shader.cthread(o[2],255,0,0)},1500)
  setTimeout(function(){shader.cthread(o[3],255,0,0)},2000)
  setTimeout(function(){shader.cthread(o[4],255,0,0)},2500)
 },

 'o':function(v)
 {
  var obj=document.getElementById(v[0])
  obj.style.opacity=0
  setTimeout(function(){shader.othread(obj,0.5)},0)
 }

}
