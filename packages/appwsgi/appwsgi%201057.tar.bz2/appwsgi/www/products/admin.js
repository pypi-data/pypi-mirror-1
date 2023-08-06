// Copyright(c) gert.cuykens@gmail.com
admin=
{

 'select':function()
 {
  http.fml=function(xml)
  {
   document.getElementById('dg-products').innerHTML=''
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
  http.xml+=' <gid>admin</gid>\n'
  http.xml+=' <pid>'+document.getElementById('pid').value+'</pid>\n'
  http.xml+=' <txt>'+document.getElementById('txt').value+'</txt>\n'
  http.xml+=' <price>'+document.getElementById('price').value+'</price>\n'
  http.xml+=' <qty>'+document.getElementById('qty').value+'</qty>\n'
  http.xml+='</root>'
  http.url='admin.py'
  http.send()
 },
 
 'update':function()
 {
  http.fml=function(xml){admin.select()}
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>update</cmd>\n'
  http.xml+=' <gid>admin</gid>\n'
  http.xml+=' <pid>'+document.getElementById('pid').value+'</pid>\n'
  http.xml+=' <txt>'+document.getElementById('txt').value+'</txt>\n'
  http.xml+=' <price>'+document.getElementById('price').value+'</price>\n'
  http.xml+=' <qty>'+document.getElementById('qty').value+'</qty>\n'
  http.xml+='</root>'
  http.url='admin.py'
  http.send()
 },

 'remove':function()
 {
  http.fml=function(xml)
  {
   document.getElementById('dg-products').innerHTML=''
   document.getElementById('pid').value=''
   document.getElementById('txt').value=''
   document.getElementById('price').value=''
   document.getElementById('qty').value=''
  }
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>delete</cmd>\n'
  http.xml+=' <gid>admin</gid>\n'
  http.xml+=' <pid>'+document.getElementById('pid').value+'</pid>\n'
  http.xml+='</root>'
  http.url='admin.py'
  http.send()
 },

 'insert':function()
 {
  http.fml=function(xml){admin.select()}
  http.xml='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>insert</cmd>\n'
  http.xml+=' <gid>admin</gid>\n'
  http.xml+=' <pid>'+document.getElementById('pid').value+'</pid>\n'
  http.xml+=' <txt>'+document.getElementById('txt').value+'</txt>\n'
  http.xml+=' <price>'+document.getElementById('price').value+'</price>\n'
  http.xml+=' <qty>'+document.getElementById('qty').value+'</qty>\n'
  http.xml+='</root>'
  http.url='admin.py'
  http.send()
 }

}

