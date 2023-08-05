// Copyright(c) gert.cuykens@gmail.com
productsadmin=
{

 'select':function()
 {
  http.fml=function(xml)
  {
   var c;if(c=document.getElementById('cproducts'))while(c.lastChild)c.removeChild(c.lastChild)
   products=
   {
    'id':'products',
    'onselect':function()
    {
     document.getElementById('pid').value=products.selection[1]
     document.getElementById('txt').value=products.selection[2]
     document.getElementById('price').value=products.selection[3]
     document.getElementById('qty').value=products.selection[4]
    }
   }
   dg.init(products,xml)
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>select</cmd>\n'
  http.xml+=' <pid>'+document.getElementById('pid').value+'</pid>\n'
  http.xml+=' <txt>'+document.getElementById('txt').value+'</txt>\n'
  http.xml+=' <price>'+document.getElementById('price').value+'</price>\n'
  http.xml+=' <qty>'+document.getElementById('qty').value+'</qty>\n'
  http.xml+='</root>'
  http.send()
 },
 
 'update':function()
 {
  http.fml=function(xml){productsadmin.select()}
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>update</cmd>\n'
  http.xml+=' <pid>'+document.getElementById('pid').value+'</pid>\n'
  http.xml+=' <txt>'+document.getElementById('txt').value+'</txt>\n'
  http.xml+=' <price>'+document.getElementById('price').value+'</price>\n'
  http.xml+=' <qty>'+document.getElementById('qty').value+'</qty>\n'
  http.xml+='</root>'
  http.send()
 },

 'remove':function()
 {
  http.fml=function(xml)
  {
   var c;if(c=document.getElementById('cproducts'))while(c.lastChild)c.removeChild(c.lastChild)
   document.getElementById('pid').value=''
   document.getElementById('txt').value=''
   document.getElementById('price').value=''
   document.getElementById('qty').value=''
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>delete</cmd>\n'
  http.xml+=' <pid>'+document.getElementById('pid').value+'</pid>\n'
  http.xml+='</root>'
  http.send()
 },

  'insert':function()
 {
  http.fml=function(xml){productsadmin.select()}
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>insert</cmd>\n'
  http.xml+=' <txt>'+document.getElementById('txt').value+'</txt>\n'
  http.xml+=' <price>'+document.getElementById('price').value+'</price>\n'
  http.xml+=' <qty>'+document.getElementById('qty').value+'</qty>\n'
  http.xml+='</root>'
  http.send()
 }

}

