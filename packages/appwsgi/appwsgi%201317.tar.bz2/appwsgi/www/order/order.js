// Copyright(c) gert.cuykens@gmail.com
products=
{
 'id':'products',
 'rec':[],
 'des':[],
 'onselect':function(){}
}

order=
{
 'uid':'',
 'list':function(v)
 {
  document.getElementById('products-dg').innerHTML=''
  products.rec=v['rec']
  products.des=v['des']
  products.onselect=function()
  {
   var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
   location.href='../invoice/invoice.htm?'+products.selection[1]+'-'+gid
  }
  dg.init(products)
 },

 'stat':function(v)
 {
  document.getElementById('products-dg').innerHTML=''
  products.rec=v['rec']
  products.des=v['des']
  products.onselect=function()
  {
   var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
   http.fml =function(v)
   {
    document.getElementById('products-dg').innerHTML=''
    products.rec=v['rec']
    products.des=v['des']
    products.onselect=function()
    {
     var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
     location.href='../invoice/invoice.htm?'+products.selection[1]+'-'+gid
    }
    dg.init(products)
   }
   http.xml ='{"cmd":"stats",\n'
   http.xml+=' "gid":"'+gid+'",\n'
   http.xml+=' "bid":"'+products.selection[0]+'"}'
   http.url ='order.wsgi'
   http.req ='POST'
   http.send()
  }
  dg.init(products)
 },

 'name':function(v)
 {
  document.getElementById('products-dg').innerHTML=''
  products.rec=v['rec']
  products.des=v['des']
  products.onselect=function()
  {
   order.uid=products.selection[0]
   var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
   http.fml = function(v)
   {
    document.getElementById('products-dg').innerHTML=''
    products.rec=v['rec']
    products.des=v['des']
    products.onselect=function()
    {
     var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
     location.href='../invoice/invoice.htm?'+products.selection[1]+'-'+gid
    }
    dg.init(products)
   }
   http.xml ='{"cmd":"list",\n'
   http.xml+=' "gid":"'+gid+'",\n'
   http.xml+=' "uid":"'+order.uid+'"}'
   http.url ='order.wsgi'
   http.req ='POST'
   http.send()
  }
  dg.init(products)
 },

 'menu':function()
 {
  var f1=document.createElement('input')
  f1.id='f1'
  f1.type='button'
  f1.value='status'
  f1.onclick=function()
  {
   var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
   http.fml =order.stat
   http.xml ='{"cmd":"status",\n'
   http.xml+=' "gid":"'+gid+'"}'
   http.url ='order.wsgi'
   http.req ='POST'
   http.send()
   if(gid=='admin')document.getElementById('f1').focus()
  }

  var f2=document.createElement('input')
  f2.id='f2'
  f2.type='button'
  f2.value='shop'
  f2.onclick=function()
  {
   var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
   location.href='../shop/shop.htm?'+order.uid+'-'+gid
  }

  var f3=document.createElement('input')
  f3.id='session'
  f3.type='button'
  f3.value='login'

  var menu=document.getElementById('menu')
  menu.id='menu'
  menu.appendChild(f1)
  menu.appendChild(f2)
  menu.appendChild(f3)
 },

 'select':function()
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  var una=''; try{una=document.URL.match(/\?(.*)-/)[1]} catch(e){}
  http.fml =order.name
  http.xml ='{"cmd":"name",\n'
  http.xml+=' "gid":"'+gid+'",\n'
  http.xml+=' "una":"'+una+'"}'
  http.url ='order.wsgi'
  http.req ='POST'
  if(gid=='admin'){http.send();return 0}
  http.fml = function(v)
  {
   document.getElementById('products-dg').innerHTML=''
   products.rec=v['rec']
   products.des=v['des']
   products.onselect=function()
   {
    var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
    location.href='../invoice/invoice.htm?'+products.selection[1]+'-'+gid
   }
   dg.init(products)
  }
  http.xml ='{"cmd":"list",\n'
  http.xml+=' "gid":"guest"}'
  http.url ='order.wsgi'
  http.req ='POST'
  http.send()
 }
}
