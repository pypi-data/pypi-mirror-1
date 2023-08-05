// Copyright(c) gert.cuykens@gmail.com
shader=
{

 'sthread':function(obj)
 {  
  var i
  for(i in obj)
  {
   var l=document.getElementById(obj[i]).offsetLeft
   var t=document.getElementById(obj[i]).offsetTop
   var r=document.getElementById(obj[i]).offsetLeft+document.getElementById(obj[i]).offsetWidth
   var w=document.getElementById(obj[i]).offsetWidth
   var h=document.getElementById(obj[i]).offsetHeight
   var b=document.getElementById(obj[i]).offsetTop+document.getElementById(obj[i]).offsetHeight

   var s1=document.getElementById('s1'+i)
   var s2=document.getElementById('s2'+i)
   var s3=document.getElementById('s3'+i)
   var s4=document.getElementById('s4'+i)
   var s5=document.getElementById('s5'+i)
   var s6=document.getElementById('s6'+i)
   var s7=document.getElementById('s7'+i)
   var s8=document.getElementById('s8'+i)

   s1.style.width="30px"
   s2.style.width=w+"px"
   s3.style.width="33px"
   s4.style.width="33px"
   s5.style.width="33px"
   s6.style.width=w+"px"
   s7.style.width="30px"
   s8.style.width="30px"

   s1.style.height="30px"
   s2.style.height="30px"
   s3.style.height="30px"
   s4.style.height=h+"px"
   s5.style.height="40px"
   s6.style.height="40px"
   s7.style.height="40px"
   s8.style.height=h+"px"

   s1.style.left=(l-30)+"px"
   s2.style.left=l+"px"
   s3.style.left=r+"px"
   s4.style.left=r+"px"
   s5.style.left=r+"px"
   s6.style.left=l+"px"
   s7.style.left=(l-30)+"px"
   s8.style.left=(l-30)+"px"

   s1.style.top=(t-29)+"px"
   s2.style.top=(t-29)+"px"
   s3.style.top=(t-29)+"px"
   s4.style.top=t+"px"
   s5.style.top=b+"px"
   s6.style.top=b+"px"
   s7.style.top=b+"px"
   s8.style.top=t+"px"

   s1.style.background="url('../bin/1.png') no-repeat 0px 0px"
   s2.style.background="url('../bin/2.png') repeat-x  0px 0px"
   s3.style.background="url('../bin/3.png') no-repeat 0px 0px"
   s4.style.background="url('../bin/4.png') repeat-y  0px 0px"
   s5.style.background="url('../bin/5.png') no-repeat 0px 0px"
   s6.style.background="url('../bin/6.png') repeat-x  0px 0px"
   s7.style.background="url('../bin/7.png') no-repeat 0px 0px"
   s8.style.background="url('../bin/8.png') repeat-y  0px 0px"

   s1.style.position="absolute"
   s2.style.position="absolute"
   s3.style.position="absolute"
   s4.style.position="absolute"
   s5.style.position="absolute"
   s6.style.position="absolute"
   s7.style.position="absolute"
   s8.style.position="absolute"
  }
 },

 'cthread':function(obj,r,g,b)
 {
  var x=obj.style.color.match(/rgb\((.+?),.+?,.+?\)/)[1]
  var y=obj.style.color.match(/rgb\(.+?,(.+?),.+?\)/)[1]
  var z=obj.style.color.match(/rgb\(.+?,.+?,(.+?)\)/)[1]
  if(x<r){x=x*1+1}else if(x!=r){x=x*1-1}
  if(y<g){y=y*1+1}else if(y!=g){y=y*1-1}
  if(z<b){z=z*1+1}else if(z!=b){z=z*1-1}
  obj.style.color='rgb('+x+','+y+','+z+')'
  if(x!=r || y!=g || z!=b){setTimeout(function(){shader.cthread(obj,r,g,b)},0)}
 },
 
 'othread':function(obj,x)
 {
  o=obj.style.opacity*1
  if (o<x) {o=o+0.005} else if (o>x) {x=o-0.005}
  obj.style.opacity=o
  if (o!=x) {setTimeout(function(){shader.othread(obj,x)},0)}
 },

 'pthread':function(obj,x,y)
 {
  var l=obj.style.left.substr(0,obj.style.left.length-2)*1
  var t=obj.style.top.substring(0,obj.style.top.length-2)*1
  if (l<x) {l=l+1} else if (l>x) {l=l-1}
  if (t<y) {t=t+1} else if (t>y) {t=t-1}
  obj.style.left=l+'px'
  obj.style.top=t+'px'
  if(x!=l || y!=t){setTimeout(function(){shader.pthread(obj,x,y)},0)}
 }
 
}
