// Copyright(c) gert.cuykens@gmail.com
products=
{
 'id':'products',
 'des':['pid','description','price','qty'],
 'rec':[],
 'onselect':function()
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  http.fml =function(v){alert('stock = '+v.rec[0][0])}
  http.xml ='{"cmd":"stock",\n'
  http.xml+=' "gid":"'+gid+'",\n'
  http.xml+=' "pid":"'+products.selection[0]+'"}'
  http.url ='invoice.wsgi'
  http.send()
 }
}

invoice=
{
 't':0,
 'print':function()
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  var oid=0; try{oid=document.URL.match(/\?(.*)-/)[1]} catch(e){}
  http.fml=function(v)
  {
   if(v.rec[0])
   {
    products.rec=JSON.parse(v.rec[0][4])
    dg.init(products)
    var r,s,t=0
    for(r in products.rec){t+=(products.rec[r][2]*products.rec[r][3])}
    s ='total:'+t
    s =document.createTextNode(s)
    document.getElementById('products-dg').appendChild(s)

    bar = new Code128()
    bar.code = document.URL.match(/\?(.*)-/)[1]
    document.getElementById('d-barcode').innerHTML=bar.draw()

    payment=document.createElement('span')
    payment.id='d-payment'
    payment.innerHTML=" - <input id=\"value\" value=\""+invoice.t+"\"/><span id=\"return\" onclick=\"this.innerHTML=' = '+(invoice.t-document.getElementById('value').value)\"> = 0 </span>"
    document.getElementById('products-dg').appendChild(payment)
   }
   switch(v.gid)
   {
    case 'guest':if(v.rec[0]){document.body.style.display='block';}break;
    case 'admin':if(v.rec[0]){document.body.style.display='block';document.getElementById('d-payment').style.display='inline';}break
    default :location='../register/register.htm'; break;
   }
   if(v.rec[0][2])invoice.stat(v.rec[0][2])
  }
  http.xml ='{"cmd":"invoice",\n'
  http.xml+=' "gid":"'+gid+'",\n'
  http.xml+=' "oid":"'+oid+'"}'
  http.url ='invoice.wsgi'
  http.req ='post'
  http.send()
 },

 'stat':function(s)
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  http.fml=function(v)
  {
   select=document.createElement('select')
   select.id='select'
   select.onchange=function()
   {
    var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
    var oid=0; try{oid=document.URL.match(/\?(.*)-/)[1]} catch(e){}
    http.fml =function(v){document.getElementById('select').selectedIndex=v.rec[0][0]-1}
    http.xml ='{"cmd":"status",\n'
    http.xml+=' "gid":"'+gid+'",\n'
    http.xml+=' "bid":"'+(document.getElementById('select').selectedIndex+1)+'",\n'
    http.xml+=' "oid":"'+oid+'"}\n'
    http.url ='invoice.wsgi'
    http.send()
   }
   var i
   for (i=0;i<v.rec.length;i++)
   {
    option=document.createElement('option')
    option.innerHTML=v.rec[i][1]
    select.appendChild(option)
   }
   select.selectedIndex=s-1
   document.getElementById('d-status').appendChild(select)
   invoice.comments()
  }
  http.xml ='{"cmd":"stats",\n'
  http.xml+=' "gid":"'+gid+'"}\n'
  http.url ='invoice.wsgi'
  http.req ='post'
  http.send()
 },

 'comments':function()
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  var oid=0; try{oid=document.URL.match(/\?(.*)-/)[1]} catch(e){}
  var txt=document.getElementById('com').value
  if(txt){txt=escape(txt)+'%0A'}
  http.fml =function(v){try{document.getElementById('d-com').innerHTML=unescape(v.rec[0][0])}catch(e){}document.getElementById('com').value=''}
  http.xml ='{"cmd":"comments",\n'
  http.xml+=' "gid":"'+gid+'",\n'
  http.xml+=' "com":"'+txt+'",\n'
  http.xml+=' "oid":"'+oid+'"}'
  http.url ='invoice.wsgi'
  http.send()
 },

 'status':function()
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  var oid=0; try{oid=document.URL.match(/\?(.*)-/)[1]} catch(e){}
  http.fml =function(v){try{document.getElementById('d-status').value=v['bid']}catch(e){}}
  http.xml ='{"cmd":"status",\n'
  http.xml+=' "gid":"'+gid+'",\n'
  http.xml+=' "bid":"'+(document.getElementById('select').selectedIndex+1)+'",\n'
  http.xml+=' "oid":"'+oid+'"}\n'
  http.url ='invoice.wsgi'
  http.send()
 }

}
