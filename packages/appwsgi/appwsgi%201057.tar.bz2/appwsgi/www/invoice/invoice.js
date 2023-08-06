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
    document.getElementById('dg-products').innerHTML=''
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
    c=document.getElementById('dg-products')
    if(c.childNodes[1])c.removeChild(c.childNodes[1])
    document.getElementById('dg-products').appendChild(s)

    bar = new Code128()
    bar.code = document.URL.match(/\?(.*)-/)[1]
    document.getElementById('d-barcode').innerHTML=bar.draw()

    payment=document.createElement('span')
    payment.id='d-payment'
    payment.innerHTML=" - <input id=\"value\" value=\""+invoice.t+"\"/><span id=\"return\" onclick=\"this.innerHTML=' = '+(invoice.t-document.getElementById('value').value)\"> = 0 </span>"
    document.getElementById('dg-products').appendChild(payment)

   }

   switch(xml.getElementsByTagName('gid')[0].childNodes[0].nodeValue)
   {
    case 'guest':if(xml.getElementsByTagName('products')[0]){document.body.style.display='block';}break;
    case 'admin':if(xml.getElementsByTagName('products')[0]){document.body.style.display='block';document.getElementById('d-payment').style.display='inline';}break
    default :window.location='../register/register.htm'; break;
   }

   if(xml.getElementsByTagName('bid')[0])invoice.stats(xml.getElementsByTagName('bid')[0].childNodes[0].nodeValue)

  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>invoice</cmd>\n'
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  http.xml+=' <gid>'+gid+'</gid>\n'
  var oid=0; try{oid=document.URL.match(/\?(.*)-/)[1]} catch(e){}
  http.xml+=' <oid>'+oid+'</oid>\n'
  http.xml+='</root>'
  http.url='invoice.py'
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
   if(xml.getElementsByTagName('gid')[0].childNodes[0].nodeValue=='guest')select.disabled=true
   document.getElementById('d-status').appendChild(select)
   invoice.comments()
  }
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>stats</cmd>\n'
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  http.xml+=' <gid>'+gid+'</gid>\n'
  http.xml+='</root>'
  http.url='invoice.py'
  http.send()
 },

 'comments':function()
 {
  http.fml=function(xml){try{document.getElementById('d-com').innerHTML=xml.getElementsByTagName('comments')[0].childNodes[0].nodeValue}catch(e){}}
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>comments</cmd>\n'
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  http.xml+=' <gid>'+gid+'</gid>\n'
  var text=''; if(document.getElementById('com').value)text=document.getElementById('com').value+'\n'
  http.xml+=' <com>'+text+'</com>\n'
  document.getElementById('com').value=''
  var oid=0; try{oid=document.URL.match(/\?(.*)-/)[1]} catch(e){}
  http.xml+=' <oid>'+oid+'</oid>\n'
  http.xml+='</root>'
  http.url='invoice.py'
  http.send()
 },

 'status':function()
 {
  http.fml=function(xml) {try{document.getElementById('d-status').value=xml.getElementsByTagName('bid')[0].childNodes[0].nodeValue}catch(e){}}
  http.xml ='<?xml version="1.0" encoding="UTF-8"?>\n'
  http.xml+='<root>\n'
  http.xml+=' <cmd>status</cmd>\n'
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  http.xml+=' <gid>'+gid+'</gid>\n'
  http.xml+=' <bid>'+(document.getElementById('select').selectedIndex+1)+'</bid>\n'
  var oid=0; try{oid=document.URL.match(/\?(.*)-/)[1]} catch(e){}
  http.xml+=' <oid>'+oid+'</oid>\n'
  http.xml+='</root>'
  http.url='invoice.py'
  http.send()
 }

}

