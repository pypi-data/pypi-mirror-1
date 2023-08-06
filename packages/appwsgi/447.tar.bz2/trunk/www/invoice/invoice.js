// Copyright(c) gert.cuykens@gmail.com

invoice=
{

 't':0,

 'print':function()
 {

  http.fml=function(xml)
  {

   if(xml.getElementsByTagName('products')[0])
   {
    document.getElementById('cproducts').innerHTML=''
    products=
    {
     'id':'products',
     'onselect':function(){}
    }
    dg.init(products,dom.parser(xml.getElementsByTagName('products')[0].childNodes[0].nodeValue))
    invoice.t=0
    var r,s,c,i
    for(r in products.table){invoice.t+=(products.table[r][3]*products.table[r][4])}
    s=xml.getElementsByTagName('uid')[0].childNodes[0].nodeValue
    s+='/'+xml.getElementsByTagName('oid')[0].childNodes[0].nodeValue
    s+='/'+xml.getElementsByTagName('bid')[0].childNodes[0].nodeValue
    s+=' total:'+invoice.t
    s=document.createTextNode(s)
    c=document.getElementById('cproducts')
    if(c.childNodes[1])c.removeChild(c.childNodes[1])
    document.getElementById('cproducts').appendChild(s)
    document.getElementById('cbarcode').innerHTML=''
    i=new Image()
    i.src='/barcode/servlet?'+document.URL.match(/\?(.*)/)[1]
    document.getElementById('cbarcode').appendChild(i)
    invoice.stats(xml.getElementsByTagName('bid')[0].childNodes[0].nodeValue)
   }

   switch(xml.getElementsByTagName('gid')[0].childNodes[0].nodeValue)
   {
    case '1':if(xml.getElementsByTagName('products')[0]) document.body.style.display='block'; break
    case '2':if(xml.getElementsByTagName('products')[0])
    {
     document.body.style.display='block'
     document.getElementById('select').disabled=false
     document.getElementById('dpayment').style.display='block'
    }break
    default :window.location='../register/register.htm';break;
   }

  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>invoice</cmd>\n'
  var oid=0; try{oid=document.URL.match(/\?(.*)/)[1]} catch(e){}
  http.xml+=' <oid>'+oid+'</oid>\n'
  http.xml+='</root>'
  http.send()
 },

 'comments':function()
 {
  http.fml=function(xml){try{document.getElementById('dcom').innerHTML=xml.getElementsByTagName('comments')[0].childNodes[0].nodeValue}catch(e){}}
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>comments</cmd>\n'
  var text=''; if(document.getElementById('com').value)text=document.getElementById('com').value+'\n'
  http.xml+=' <com>'+text+'</com>\n'
  document.getElementById('com').value=''
  var oid=0; try{oid=document.URL.match(/\?(.*)/)[1]} catch(e){}
  http.xml+=' <oid>'+oid+'</oid>\n'
  http.xml+='</root>'
  http.send()
 },

 'stats':function(s)
 {
  http.fml=function(xml)
  {
   select=document.createElement('select')
   select.onchange=invoice.status
   select.id='select'
   for (var i=0;i<xml.getElementsByTagName('description').length;i++)
   {
    option=document.createElement('option')
    option.innerHTML=xml.getElementsByTagName('description')[i].childNodes[0].nodeValue
    select.appendChild(option)
   }
   select.selectedIndex=s-1
   select.disabled=true
   document.getElementById('dstatus').appendChild(select)
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>stats</cmd>\n'
  http.xml+='</root>'
  http.send()
 },

 'status':function()
 {
  http.fml=function(xml) {try{document.getElementById('dstatus').value=xml.getElementsByTagName('bid')[0].childNodes[0].nodeValue}catch(e){}}
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>status</cmd>\n'
  http.xml+=' <bid>'+(document.getElementById('select').selectedIndex+1)+'</bid>\n'
  var oid=0; try{oid=document.URL.match(/\?(.*)/)[1]} catch(e){}
  http.xml+=' <oid>'+oid+'</oid>\n'
  http.xml+='</root>'
  http.send()
 },

 'payment':function()
 {
  http.fml=function(xml){document.getElementById('return').innerHTML='return '+(document.getElementById('value').value-invoice.t)}
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>payment</cmd>\n'
  http.xml+=' <value>'+document.getElementById('value').value+'</value>\n'
  http.xml+=' <oid>'+document.URL.match(/\?(.*)/)[1]+'</oid>\n'
  http.xml+='</root>'
  http.send()
 }

}

