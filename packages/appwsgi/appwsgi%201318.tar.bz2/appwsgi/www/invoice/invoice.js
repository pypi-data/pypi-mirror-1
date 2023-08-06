// Copyright(c) gert.cuykens@gmail.com
products=
{
 'id':'products',
 'des':['pid','description','price','qty'],
 'rec':[],
 'onselect':function()
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  var pid=products.selection[0]
  http.fml =function(v)
  {
   var price=products.selection[2]
   var stock=v.rec[0][0]
   alert('stock = '+stock)
   if(v.gid!='admin')return 0
   var pr=document.createElement('input')
   pr.id='price'
   pr.value=price
   pr.onblur=function()
   {
    var i=this.parentNode.id.match(/products-row-(.+?)-col-2/)[1]
    products['rec'][i][2]=this.value
    dg.init(products)
    invoice.total(v.gid)
    invoice.update()
   }
   for(var i=0;i<products['rec'].length;i++){if(products['rec'][i][0]==pid){td=document.getElementById('products-row-'+i+'-col-2');break;}}
   td.innerHTML=''
   td.appendChild(pr)
   pr.focus()
  }
  http.xml ='{"cmd":"stock",\n'
  http.xml+=' "gid":"'+gid+'",\n'
  http.xml+=' "pid":"'+pid+'"}'
  http.url ='invoice.wsgi'
  http.req ='POST'
  http.send()
 }
}

invoice=
{
 'print':function()
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]}catch(e){}
  var oid=0; try{oid=document.URL.match(/\?(.*?)(-|$)/)[1]}catch(e){}
  http.fml=function(v)
  {
   if(v.rec[0])
   {
    products.rec=JSON.parse(v.rec[0][4])
    dg.init(products)
    bar = new Code128()
    bar.code = document.URL.match(/\?(.*?)(-|$)/)[1]
    document.getElementById('d-barcode').innerHTML=bar.draw()
    invoice.total(v.gid)
    invoice.stat(v.rec[0][2])
    document.getElementById('com').value=''
    document.getElementById('comments').style.display='block'
    invoice.comments()
   }
  }
  http.xml ='{"cmd":"invoice",\n'
  http.xml+=' "gid":"'+gid+'",\n'
  http.xml+=' "oid":"'+oid+'"}'
  http.url ='invoice.wsgi'
  http.req ='POST'
  http.send()
 },

 'stat':function(s)
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  http.fml=function(v)
  {
   var select=document.createElement('select')
   select.id='select'
   select.onchange=function()
   {
    var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
    var oid=0; try{oid=document.URL.match(/\?(.*?)(-|$)/)[1]} catch(e){}
    http.fml =function(v){document.getElementById('select').selectedIndex=v.rec[0][0]}
    http.xml ='{"cmd":"status",\n'
    http.xml+=' "gid":"'+gid+'",\n'
    http.xml+=' "bid":"'+(document.getElementById('select').selectedIndex)+'",\n'
    http.xml+=' "oid":"'+oid+'",\n'
    http.xml+=' "rec":'+JSON.stringify(products.rec)+'}'
    http.url ='invoice.wsgi'
    http.req ='POST'
    http.send()
   }
   for (var i=0;i<v.rec.length;i++)
   {
    var option=document.createElement('option')
    option.innerHTML=v.rec[i][1]
    select.appendChild(option)
   }
   select.selectedIndex=s
   document.getElementById('d-status').appendChild(select)
  }
  http.xml ='{"cmd":"stats",\n'
  http.xml+=' "gid":"'+gid+'"}\n'
  http.url ='invoice.wsgi'
  http.req ='POST'
  http.send()
 },

 'comments':function()
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]}catch(e){}
  var oid=0; try{oid=document.URL.match(/\?(.*?)(-|$)/)[1]}catch(e){}
  var txt=document.getElementById('com').value
  if(txt){txt=escape(txt)+'%0A'}
  var h=new Http()
  h.fml =function(v){try{document.getElementById('d-com').innerHTML=unescape(v.rec[0][0])}catch(e){}document.getElementById('com').value=''}
  h.xml ='{"cmd":"comments",\n'
  h.xml+=' "gid":"'+gid+'",\n'
  h.xml+=' "com":"'+txt+'",\n'
  h.xml+=' "oid":"'+oid+'"}'
  h.url ='invoice.wsgi'
  h.req ='POST'
  h.send()
 },

 'total':function(gid)
 {
  var r,s,t=0
  for(r in products.rec){t+=(products.rec[r][2]*products.rec[r][3])}
  s ='total = '+t
  s =document.createTextNode(s)
  document.getElementById('products-dg').appendChild(s)
 },

 'update':function()
 {
  var gid='guest'; try{gid=document.URL.match(/-(.*)/)[1]} catch(e){}
  var oid=0; try{oid=document.URL.match(/\?(.*?)(-|$)/)[1]} catch(e){}
  http.xml ='{"cmd":"update",\n'
  http.xml+=' "gid":"'+gid+'",\n'
  http.xml+=' "rec":'+JSON.stringify(products.rec)+',\n'
  http.xml+=' "oid":"'+oid+'"}'
  http.url ='invoice.wsgi'
  http.req ='POST'
  http.send()
 }
}
