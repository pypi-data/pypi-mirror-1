// Copyright(c) gert.cuykens@gmail.com

invoice=
{
 'print':function()
 {
  http.fml=function(xml)
  {
   var r,t,s,c,i
   if(!xml.getElementsByTagName('products')[0])return 0
   document.getElementById('cproducts').innerHTML=''
   products=
   {
    'id':'products',
    'onselect':function(){}
   }
   dg.init(products,dom.parser(xml.getElementsByTagName('products')[0].childNodes[0].nodeValue))
   t=0
   for(r in products.table){t+=(products.table[r][3]*products.table[r][4])}
   s=xml.getElementsByTagName('uid')[0].childNodes[0].nodeValue
   s+='/'+xml.getElementsByTagName('oid')[0].childNodes[0].nodeValue
   s+='/'+xml.getElementsByTagName('bid')[0].childNodes[0].nodeValue
   s+=' total:'+t
   s=document.createTextNode(s)
   c=document.getElementById('cproducts')
   if(c.childNodes[1])c.removeChild(c.childNodes[1])
   document.getElementById('cproducts').appendChild(s)
   document.getElementById('cbarcode').innerHTML=''
   i=new Image()
   i.src='/barcode/servlet?'+document.URL.match(/\?(.*)/)[1]
   document.getElementById('cbarcode').appendChild(i)
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>invoice</cmd>\n'
  http.xml+=' <oid>'+document.URL.match(/\?(.*)/)[1]+'</oid>\n'
  http.xml+='</root>'
  http.post()
 }
}
