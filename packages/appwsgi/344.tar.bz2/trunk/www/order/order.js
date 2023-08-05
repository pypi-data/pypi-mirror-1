// Copyright(c) gert.cuykens@gmail.com
cart=''
products=''
order=
{
 'nr':'new',
 'id':'',
 'status':1,

 'total':function()
 {
  if(document.getElementById('cart'))
  {
   var r,t,s,c
   t=0
   for(r in cart.table){t+=(cart.table[r][3]*cart.table[r][4])}
   s=order.id
   s+='/'+order.nr
   s+='/'+order.status
   s+=' total: '+t
   s=document.createTextNode(s)
   c=document.getElementById('ccart')
   if(c.childNodes[1])c.removeChild(c.childNodes[1])
   document.getElementById('ccart').appendChild(s)
  }
 },

 'products':function(xml)
 {
  var v,i
  if ( v=document.getElementById('products') ) v.parentNode.removeChild(v)
  
  products=
  {
   'id':'products',
   'onselect':function()
   {
    if(cart)dg.select(cart,'-1')
    
    var qty=document.createElement('input')
    qty.id='qty'
    qty.value=1
    qty.onkeydown=function(){this.value='';this.onkeydown='';}
 
    var yes=document.createElement('input')
    yes.id='yes'
    yes.type='button'
    yes.value='yes'
    yes.onfocus=function()
    {

     var a=new Array()
     var i
     for(i in products.selection)
     {
      a[i]=products.selection[i]
      if(i==4)a[i]=qty.value
      if(i==0)
      {
       if(document.getElementById('cart'))
       {
        a[0]=cart.table.length+''
        for (j in cart.table){if(cart.table[j][1]==products.selection[1]){a[0]=cart.table[j][0]}}
       }
       else {a[0]=0+''}
      }
     }

     qty=document.getElementById('qty')

     if(qty.value>0)
     {
      if(!document.getElementById('cart'))
      {
       var xml='<?xml version="1.0" encoding="UTF-8"?>\n'
       xml+='<root>\n'
       for (i in products.selection)
       {
        if(i==0){xml+=' <record index="0">\n'}
        if(i==4){v=qty.value}else{v=products.selection[i]}
        if(i!=0){xml+='  <'+products.header[i]+'>'+v+'</'+products.header[i]+'>\n'}
       }
       xml+=' </record>\n'
       xml+='</root>'
       xml=dom.parser(xml)
       order.cart(xml)
       order.total()
       dg.select(products,'-1')
       order.menu()
       document.getElementById('iframe').style.display='none';
       return 0
      }
      dg.insert(cart,a)
      order.total()
      dg.select(products,'-1')
      order.menu()
      document.getElementById('iframe').style.display='none';
      return 0
     }

     var t
     if(t=document.getElementById('ccart'))
     {
      dg.remove(cart,a[0])
      if(cart.table.length==0)
      {
       var n
       while(n=t.childNodes[0]){t.removeChild(n)}
      }
      dg.select(products,'-1')
      order.menu()
      document.getElementById('iframe').style.display='none';  
     }

    }

    var no=document.createElement('input')
    no.id='no'
    no.type='button'
    no.value='no'
    no.onfocus=function(){dg.select(products,'-1');order.menu();document.getElementById('iframe').style.display='none';}

    var view=document.createElement('input')
    view.id='view'
    view.type='button'
    view.value='view'
    view.onclick=function()
    {
     document.getElementById('iframe').data=products.selection[1]+".htm"
     if (document.getElementById('iframe').style.display=='block') document.getElementById('iframe').style.display='none';
     else document.getElementById('iframe').style.display='block'
    }

    var menu=document.getElementById('menu')
    menu.innerHTML=''
    menu.appendChild(document.createTextNode('add '+products.selection[2]))
    menu.appendChild(qty)
    menu.appendChild(yes)
    menu.appendChild(no)
    menu.appendChild(view)
    document.getElementById('qty').focus()

   }
  }

  dg.init(products,xml)

  if ( xml.getElementsByTagName('record').length  == 1 )
  {
   if (!document.getElementById('cart'))
   {
    xml.getElementsByTagName('qty')[0].childNodes[0].nodeValue='1'
    order.cart(xml)
   }
   else
   {
    var a=new Array()
    var x=xml.getElementsByTagName('record')[0].childNodes
    var j=1
    var i
    a[0]=cart.table.length+''
    for(i=0;i<x.length;i++) //IE7
    {
     if(x[i].nodeType==1)
     {
      a[j]=x[i].childNodes[0].nodeValue
      if(j==4)a[j]=1
      j++
     }
    }
    for(i in cart.table)
    {
     if(a[1]==cart.table[i][1]){a=false}
    }
    if(a)dg.insert(cart,a)
    order.total()
   }
  }
   
 },
 
 'cart':function(xml)
 {  
  var v
  if(v=document.getElementById('ccart'))while(v.lastChild)v.removeChild(v.lastChild)
   
  cart=
  {

   'id':'cart',

   'onselect':function()
   {
    if(products)dg.select(products,'-1')

    var qty=document.createElement('input')
    qty.id='qty'
    qty.value=0
    qty.onkeydown=function(){this.value='';this.onkeydown='';}
 
    var yes=document.createElement('input')
    yes.id='yes'
    yes.type='button'
    yes.value='yes'
    yes.onfocus=function()
    {

     qty=document.getElementById('qty')
     var a=new Array()
     var i
     for(i in cart.selection)
     {
      a[i]=cart.selection[i]
      if(i==4)a[i]=qty.value
     }

     if(qty.value<=0){dg.remove(cart,a[0])}else{dg.insert(cart,a)}
     var n,c
     if(cart.table.length==0){if(c=document.getElementById('ccart')){while (n=c.childNodes[0]){c.removeChild(n);}}}

     order.total()
     if(cart)dg.select(cart,'-1')
     order.menu()
     document.getElementById('iframe').style.display='none';

    }

    var no=document.createElement('input')
    no.id='no'
    no.type='button'
    no.value='no'
    no.onfocus=function(){if(cart)dg.select(cart,'-1');order.menu();document.getElementById('iframe').style.display='none';}

    var view=document.createElement('input')
    view.id='view'
    view.type='button'
    view.value='view'
    view.onclick=function()
    {
     document.getElementById('iframe').data=cart.selection[1]+".htm"
     if (document.getElementById('iframe').style.display=='block') document.getElementById('iframe').style.display='none';
     else document.getElementById('iframe').style.display='block'
    }

    var menu=document.getElementById('menu')
    menu.innerHTML=''
    menu.appendChild(document.createTextNode('update '+cart.selection[2]))
    menu.appendChild(qty)
    menu.appendChild(yes)
    menu.appendChild(no)
    menu.appendChild(view)
    document.getElementById('qty').focus()
   
   }

  }
  
  dg.init(cart,xml)

  order.total()
 
 },

 'list':function(xml)
 {
  var n,c
  if(c=document.getElementById('cproducts')){while(n=c.childNodes[0]){c.removeChild(n)}}
  products=
  {
   'id':'products',
   'onselect':function()
   {
    http.fml=function(xml){order.cart(dom.parser(xml.getElementsByTagName('products')[0].childNodes[0].nodeValue))}
    http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
    http.xml+='<root>\n' 
    http.xml+=' <cmd>cart</cmd>\n'
    http.xml+=' <oid>'+products.selection[2]+'</oid>\n'
    http.xml+='</root>'
    order.id=products.selection[1]
    order.nr=products.selection[2]
    order.status=products.selection[3]
    http.post()
    var yes=document.createElement('input')
    yes.id='yes'
    yes.type='button'
    yes.value='yes'
    yes.onfocus=function()
    {
     order.remove()
     order.menu()
     if(v=document.getElementById('ccart'))while(v.lastChild)v.removeChild(v.lastChild)
    }
    var no=document.createElement('input')
    no.id='yes'
    no.type='button'
    no.value='no'
    no.onfocus=function(){order.menu()}
    var menu=document.getElementById('menu')
    menu.innerHTML=''
    menu.appendChild(document.createTextNode('remove '+products.selection[2]+' '))
    menu.appendChild(no)
    menu.appendChild(yes)
   }
  }
  dg.init(products,xml)
 },

 'stat':function(xml)
 {
  var n,c
  if(c=document.getElementById('cproducts')){while(n=c.childNodes[0]){c.removeChild(n)}}
  products=
  {
   'id':'products',
   'onselect':function(){order.status=products.selection[1];order.total()}
  }
  dg.init(products,xml)
 },

 'name':function(xml)
 {
  var n,c
  if(c=document.getElementById('cproducts')){while(n=c.childNodes[0]){c.removeChild(n)}}
  products=
  {
   'id':'products',
   'onselect':function()
   {
    order.id=products.selection[1]
    order.total()
    http.fml=order.list
    http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
    http.xml+='<root>\n'
    http.xml+=' <cmd>list</cmd>\n' 
    http.xml+=' <uid>'+order.id+'</uid>\n'
    http.xml+='</root>'
    http.post()
   }
  }
  dg.init(products,xml)
 },

 'insert':function()
 {
  http.fml=function(xml)
  {
   order.menu();
   order.nr=xml.getElementsByTagName('id')[0].childNodes[0].nodeValue
   window.location='../invoice/invoice.htm?'+order.nr
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>insert</cmd>\n'
  http.xml+=' <uid>'+order.id+'</uid>\n'
  http.xml+=' <bid>'+order.status+'</bid>\n'
  http.xml+=dg.xml(cart)
  http.xml+='</root>'
  http.post()
 },

 'update':function()
 {
  http.fml =function(xml)
  {
   order.menu();
   window.location='../invoice/invoice.htm?'+order.nr
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>update</cmd>\n'
  http.xml+=' <oid>'+order.nr+'</oid>\n'
  http.xml+=' <uid>'+order.id+'</uid>\n'
  http.xml+=' <bid>'+order.status+'</bid>\n'
  http.xml+=dg.xml(cart)
  http.xml+='</root>'
  http.post()
 },

 'remove':function()
 {
  http.fml=function(xml)
  {
   var n,c
   order.nr='new'
   dg.remove(products,products.selection[0])
   if(products.table.length==0){if(c=document.getElementById('cproducts')){while (n=c.childNodes[0]){c.removeChild(n)}}}
   alert('removed succesfully')
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>remove</cmd>\n'
  http.xml+=' <oid>'+order.nr+'</oid>\n'
  http.xml+='</root>'
  http.post()
 },

 'menu':function()
 {

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
   http.fml=order.products
   http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
   http.xml+='<root>\n'
   http.xml+=' <cmd>pid</cmd>\n'
   http.xml+=' <pid>'+document.getElementById('f1').value+'</pid>\n'
   http.xml+='</root>'
   http.post()
   document.getElementById('f1').focus()
   document.getElementById('iframe').style.display='none'
  }

  var f3=document.createElement('input')
  f3.id='f3'
  f3.type='button'
  f3.value='find'
  f3.onfocus=function()
  {
   http.fml=order.products
   http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
   http.xml+='<root>\n'
   http.xml+=' <cmd>find</cmd>\n'
   http.xml+=' <pna>'+document.getElementById('f1').value+'</pna>\n'
   http.xml+='</root>'
   http.post()
   document.getElementById('f1').focus()
   document.getElementById('iframe').style.display='none'
  }

  var f4=document.createElement('input')
  f4.id='f4'
  f4.type='button'
  f4.value='save'
  f4.onfocus=function()
  {
   if(document.getElementById('cart'))
   {
    if (order.nr=='new'){order.insert()}
    else {order.update()}
   }
   document.getElementById('iframe').style.display='none'
  }

  var f5=document.createElement('input')
  f5.id='f5'
  f5.type='button'
  f5.value='client'
  f5.onfocus=function()
  {
   http.fml=order.name;
   http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
   http.xml+='<root>\n'
   http.xml+=' <cmd>name</cmd>\n'
   http.xml+=' <una>'+document.getElementById('f1').value+'</una>\n'
   http.xml+='</root>';
   http.post()
   document.getElementById('f1').focus()
   document.getElementById('iframe').style.display='none'
  }

  var f6=document.createElement('input')
  f6.id='f6'
  f6.type='button'
  f6.value='status'
  f6.onfocus=function()
  {
   http.fml=order.stat
   http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
   http.xml+='<root>\n'
   http.xml+=' <cmd>status</cmd>\n'
   http.xml+='</root>'
   http.post()
   document.getElementById('f1').focus()
   document.getElementById('iframe').style.display='none'
  }

  var f7=document.createElement('input')
  f7.id='f7'
  f7.type='button'
  f7.value='new'
  f7.onclick=function()
  {
   var c,n
   order.nr='new'
   products=''
   cart=''
   if(c=document.getElementById('cproducts')){while(n=c.childNodes[0]){c.removeChild(n)}}
   if(c=document.getElementById('ccart')){while(n=c.childNodes[0]){c.removeChild(n)}}
   document.getElementById('f1').focus()
   document.getElementById('iframe').style.display='none'
  }
  
  var f8=document.createElement('input')
  f8.id='f8'
  f8.type='button'
  f8.value='login'
  f8.onclick=function(){window.location='../register/register.htm'}

  var f9=document.createElement('input')
  f9.id='f9'
  f9.type='button'
  f9.value='index'
  f9.onclick=function()
  {
   document.getElementById('iframe').style.display='block'
   document.getElementById('iframe').data='0.htm'
  }

  var f0=document.getElementById('menu')
  f0.id='menu'
  f0.appendChild(f1)
  f0.appendChild(f2)
  f0.appendChild(f3)
  f0.appendChild(f4)
  f0.appendChild(f5)
  f0.appendChild(f6)
  f0.appendChild(f7)
  f0.appendChild(f8)
  f0.appendChild(f9)
  document.getElementById('f1').focus()
 
 }

}
