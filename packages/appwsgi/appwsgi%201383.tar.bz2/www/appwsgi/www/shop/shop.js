// Copyright(c) gert.cuykens@gmail.com
products=
{
 'id':'products',
 'rec':[],
 'des':[],
 'onselect':function(){}
}

cart=
{
 'id':'cart',
 'rec':[],
 'des':[],
 'onselect':function(){}
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

 'products':function(v)
 {
  document.getElementById('products-dg').innerHTML=''
  products.rec=v['rec']
  products.des=v['des']
  products.onselect=function()
  { 
   if(document.getElementById('cart'))dg.select(cart,-1)

   var qty=document.createElement('input')
   qty.id='qty'
   qty.value=1
   qty.onkeydown=function(){this.value='';this.onkeydown='';}

   var yes=document.createElement('input')
   yes.id='yes'
   yes.type='button'
   yes.value='yes'
   yes.onclick=function()
   {
    qty=document.getElementById('qty')
    products.selection[3]=qty.value
    cart.des=products.des
    var i
    for(i in cart.rec)
    {
     if(cart.rec[i][0]==products.selection[0])
     {
      if (qty.value > 0)
      {
       cart.rec[i][3]=qty.value
       order.cart(cart)
       order.menu()
       order.total()
       return 0
      }
      else
      {
       dg.remove(cart,i)
       order.total()
       return 0
      }
     }
    }
    if (qty.value<=0) return 0
    cart.rec[cart.rec.length]=products.selection
    order.cart(cart)
    order.total()
    order.menu()
   }

   var no=document.createElement('input')
   no.id='no'
   no.type='button'
   no.value='no'
   no.onclick=function(){order.menu()}

   var view=document.createElement('input')
   view.id='view'
   view.type='button'
   view.value='view'
   view.onclick=function()
   {
    document.getElementById('shop').style.display='block'
    http.fml=function(v){document.getElementById('shop').innerHTML=v}
    http.url=products.selection[0]+'.htm'
    http.req='GET'
    http.send()
   }

   var menu=document.getElementById('menu')
   menu.innerHTML=''
   menu.appendChild(document.createTextNode('add '+products.selection[1]))
   menu.appendChild(qty)
   menu.appendChild(yes)
   menu.appendChild(no)
   menu.appendChild(view)
   document.getElementById('qty').focus()
  }
  dg.init(products)

  if (v.rec.length==1)
  {
   cart.des=v.des
   for(i in cart.rec){if(cart.rec[i][0]==v.rec[0][0]){cart.rec[i][3]++;order.cart(cart);order.total();return 0;}}
   cart.rec[cart.rec.length]=v.rec[0]
   cart.rec[cart.rec.length-1][3]=1
   order.cart(cart)
   order.total()
  }
 },
 
 'cart':function(v)
 {  
  document.getElementById('cart-dg').innerHTML=''
  cart.rec=v['rec']
  cart.des=v['des']
  cart.onselect=function()
  {
   if(document.getElementById('products'))dg.select(products,-1)

   var qty=document.createElement('input')
   qty.id='qty'
   qty.value=0
   qty.onkeydown=function(){this.value='';this.onkeydown='';}
 
   var yes=document.createElement('input')
   yes.id='yes'
   yes.type='button'
   yes.value='yes'
   yes.onclick=function()
   {
    qty=document.getElementById('qty')
    cart.selection[3]=qty.value
    var i
    for(i in cart.rec)
    {
     if(cart.rec[i][0]==cart.selection[0])
     {
      if (qty.value > 0)
      {
       cart.rec[i][3]=qty.value
       order.cart(cart)
       order.menu()
       order.total()
       return 0
      }
      else
      {
       dg.remove(cart,i)
       order.menu()
       order.total()
       return 0
      }
     }
    }
   }

   var no=document.createElement('input')
   no.id='no'
   no.type='button'
   no.value='no'
   no.onclick=function(){order.menu()}

   var view=document.createElement('input')
   view.id='view'
   view.type='button'
   view.value='view'
   view.onclick=function()
   {
    document.getElementById('shop').style.display='block'
    http.fml=function(v){document.getElementById('shop').innerHTML=v}
    http.url=cart.selection[0]+'.htm'
    http.req='GET'
    http.send()
   }

   var menu=document.getElementById('menu')
   menu.innerHTML=''
   menu.appendChild(document.createTextNode('update '+cart.selection[1]))
   menu.appendChild(qty)
   menu.appendChild(yes)
   menu.appendChild(no)
   menu.appendChild(view)
   document.getElementById('qty').focus()
  }
  dg.init(cart)
  order.total()
 },

 'insert':function()
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  var uid=''; try{uid=unescape(document.URL.match(/\?(.*)-/)[1])} catch(e){}
  http.fml =function(v)
  {
   order.menu()
   var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
   location='../invoice/invoice.htm?'+v.rid+'-'+gid
  }
  http.xml ='{"cmd":"insert",\n'
  http.xml+=' "gid":"'+gid+'",\n'
  http.xml+=' "uid":"'+uid+'",\n'
  http.xml+=' "rec":'+JSON.stringify(cart.rec)+'}'
  http.url ='../../wsgi/shop.wsgi'
  http.req ='POST'
  http.send()
 },

 'menu':function()
 {
  document.getElementById('shop').style.display='none'

  var menu=document.getElementById('menu')
  menu.innerHTML=''

  var f1=document.createElement('input')
  f1.id='f1'
  f1.onfocus=function(){this.value=''}

  var f2=document.createElement('input')
  f2.id='f2'
  f2.type='button'
  f2.value='add'
  f2.onfocus=function()
  {
   var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
   http.fml =order.products
   http.xml ='{"cmd":"pid",\n'
   http.xml+=' "gid":"'+gid+'",\n'
   http.xml+=' "pid":"'+document.getElementById('f1').value+'"}'
   http.url ='../../wsgi/shop.wsgi'
   http.req ='post'
   http.send()
   document.getElementById('f1').focus()
   document.getElementById('shop').style.display='none'
  }

  var f3=document.createElement('input')
  f3.id='f3'
  f3.type='button'
  f3.value='find'
  f3.onclick=function()
  {
   var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
   http.fml =order.products
   http.xml ='{"cmd":"find",\n'
   http.xml+=' "gid":"'+gid+'",\n'
   http.xml+=' "pna":"'+document.getElementById('f1').value+'"}'
   http.url ='../../wsgi/shop.wsgi'
   http.req ='POST'
   http.send()
   document.getElementById('f1').focus()
   document.getElementById('shop').style.display='none'
  }

  var f4=document.createElement('input')
  f4.id='f4'
  f4.type='button'
  f4.value='order'
  f4.onclick=function(){if(cart['rec'][0]){order.insert()}else{alert('no products in cart');return 0}}

  var f5=document.createElement('input')
  f5.id='f5'
  f5.type='button'
  f5.value='new'
  f5.onclick=function()
  {
   products.rec=[]
   cart.rec=[]
   document.getElementById('products-dg').innerHTML=''
   document.getElementById('cart-dg').innerHTML=''
   document.getElementById('f1').focus()
  }

  var f6=document.createElement('input')
  f6.id='f6'
  f6.type='button'
  f6.value='shop'
  f6.onclick=function()
  {
   document.getElementById('menu').innerHTML=''
   document.getElementById('shop').style.display='block'
  }

  var f0=document.getElementById('menu')
  f0.id='menu'
  f0.appendChild(f1)
  f0.appendChild(f2)
  f0.appendChild(f3)
  f0.appendChild(f4)
  f0.appendChild(f5)
  f0.appendChild(f6)
  document.getElementById('f1').focus()
 }
}
