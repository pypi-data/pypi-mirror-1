// Copyright(c) gert.cuykens@gmail.com
init=function()
{
 order.uid=''; try{order.uid=unescape(document.URL.match(/\?(.*)-/)[1])} catch(e){}
 order.gid='guest'; try{order.gid=document.URL.match(/\?.*-(.*)/)[1]} catch(e){}
 order.oid='new'; try{order.oid=unescape(document.URL.match(/\?.*-.*-(.*)/)[1])} catch(e){} 
 order.init()
 gui('i')
}

cart=
{
 'id':'cart',
 'rec':[],
 'des':['pid','txt','price','qty'],
 'onselect':function(){if(document.getElementById('products'))dg.select(products,-1);gui('c')}
}

products=
{
 'id':'products',
 'rec':[],
 'des':['pid','txt','price','qty'],
 'onselect':function(){if(document.getElementById('cart'))dg.select(cart,-1);gui('p')}
}

order=
{
 'total':function()
 {
  if(document.getElementById('cart'))
  {
   var r,s,c,t=0
   for(r in cart.rec){t+=(cart.rec[r][2]*cart.rec[r][3])}
   s='total: '+t
   s=document.createTextNode(s)
   c=document.getElementById('cart-dg')
   if(c.childNodes[1])c.removeChild(c.childNodes[1])
   document.getElementById('cart-dg').appendChild(s)
  }
 },
 
 'qty':function(v,q)
 {
  var cmd='insert'
  if(q==0)cmd='delete'
  http.fml =function(v){order.init();gui('i')}
  http.xml ='{"cmd":"'+cmd+'",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"'+order.gid+'",\n'
  http.xml+=' "pid":'+v+',\n'
  http.xml+=' "qty":'+q+'}'
  http.url ='../../wsgi/order.wsgi'
  http.req ='POST'
  http.send()
 },

 'init':function()
 {
  http.fml =function(v)
  {
   var bar = new Code128()
   bar.code = order.oid
   document.getElementById('barcode-d').innerHTML=bar.draw()
   document.getElementById('products-dg').innerHTML=''
   document.getElementById('cart-dg').innerHTML=''
   cart.rec=v['rec']
   dg.init(cart)
   order.total()
  }
  http.xml ='{"cmd":"order",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "uid":"'+order.uid+'",\n'
  http.xml+=' "gid":"'+order.gid+'",\n'
  http.xml+=' "oid":"'+order.oid+'"}'
  http.url ='../../wsgi/order.wsgi'
  http.req ='POST'
  http.send()
 }
}

gui=function(m)
{
 var f1=document.createElement('span')
 f1.id='f1'
 f1.innerHTML=order.oid
 f1.onclick=function(){order.init()}

 var f2=document.createElement('input')
 f2.id='f2'
 f2.onfocus=function(){this.value=''}

 var f3=document.createElement('input')
 f3.id='f3'
 f3.type='button'
 f3.value='find'
 f3.onclick=function()
 {
  http.fml =function(v)
  {
   document.getElementById('products-dg').innerHTML=''
   products.rec=v['rec']
   dg.init(products)
   //if(v.rec.length==1&&order.scan==true){order.qty(v.rec[0][0],1)}
  }
  http.xml ='{"cmd":"find",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"'+order.gid+'",\n'
  http.xml+=' "txt":"'+document.getElementById('f2').value+'"}'
  http.url ='../../wsgi/order.wsgi'
  http.req ='POST'
  http.send()
  document.getElementById('f2').focus()
 }

 var f4=document.createElement('input')
 f4.id='f4'
 f4.type='button'
 f4.value='pay'
 f4.onclick=function()
 {
  http.fml =function(v){order.init()}
  http.xml ='{"cmd":"pay",\n'
  http.xml+=' "sid":"'+session.sid+'",\n'
  http.xml+=' "gid":"'+order.gid+'"}'
  http.url ='../../wsgi/order.wsgi'
  http.req ='POST'
  http.send()
  document.getElementById('f2').focus()
 }

 var qty=document.createElement('input')
 qty.id='qty'
 qty.onkeydown=function(){this.value='';this.onkeydown='';}

 var yes=document.createElement('input')
 yes.id='yes'
 yes.type='button'
 yes.value='yes'

 var no=document.createElement('input')
 no.id='no'
 no.type='button'
 no.value='no'
 no.onclick=function(){gui('i')}

 var view=document.createElement('input')
 view.id='view'
 view.type='button'
 view.value='view'
 view.onclick=function(){document.location='../product/'+products.selection[0]+'.htm'} 
 
 var menu=document.getElementById('menu')
 menu.id='menu'
 menu.innerHTML=''
 menu.appendChild(f1)

 switch(m)
 {
  case 'p':
   qty.value=1
   yes.onclick=function(){order.qty(products.selection[0],document.getElementById('qty').value)}
   menu.appendChild(document.createTextNode('qty'))
   menu.appendChild(qty)
   menu.appendChild(yes)
   menu.appendChild(no)
   menu.appendChild(view)
   document.getElementById('qty').focus()
  break;
  case 'c':
   qty.value=0
   yes.onclick=function(){order.qty(cart.selection[0],document.getElementById('qty').value)}
   menu.appendChild(document.createTextNode('qty'))
   menu.appendChild(qty)
   menu.appendChild(yes)
   menu.appendChild(no)
   menu.appendChild(view)
   document.getElementById('qty').focus()
  break;
  case 'i':
   menu.appendChild(f2)
   menu.appendChild(f3)
   menu.appendChild(f4)
   document.getElementById('f2').focus()
  break;
 }
}
