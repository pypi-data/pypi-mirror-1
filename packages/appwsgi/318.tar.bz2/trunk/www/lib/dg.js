// Copyright(c) gert.cuykens@gmail.com
dg={

 'xml':function(self)
 {
  var c,r,i,j
  i=0
  xml=''
  while(r=self.table[i])
  {
   j=1
   xml+=' <record index="'+i+'">\n'
   while(c=r[j])
   {
    c=c+''
    c=c.replace(/&/g,'&amp;')
    c=c.replace(/</g,'&lt;')
    c=c.replace(/>/g,'&gt;')  
    xml+='  <'+self.header[j]+'>'+c+'</'+self.header[j]+'>\n'
    j++
   }
   i++
   xml+=' </record>\n'
  }
  return xml
 },
 
 'remove':function(self,v)
 {
  var c,r,p,tr,td,tb
  tb=document.getElementById(self.id)
  c=0;r=0;p=0
  for (c=1; c<self.header.length; c++){document.getElementById(self.id+'_hd_c'+c).style.backgroundImage='url()'}
  tr=document.getElementById(self.id+'_hd')
  tb=document.getElementById(self.id)
  tb.deleteRow(tb.rows.length-1)
  for (r=0; r<self.table.length-1; r++) 
  {
   if(self.table[r][0]==v){p=1}
   for (c=1; c<self.header.length; c++)
   {
    self.table[r][c]=self.table[r+p][c]
    td=document.getElementById(self.id+'_r'+r+'_c'+c)
    td.firstChild.nodeValue=self.table[r][c]
    td.style.background=''
   }
  }
  self.selection=new Array()
  self.selection[0]=-1
  self.table.pop()
 },

 'insert':function(self,v)
 {
  var tb,tr,td,v,c,r

  var update=function()
  {
   var r,c,td
   for (r=0; r<self.table.length; r++) 
   {
    if(self.table[r][0]==v[0])
    { 
     self.table[r]=v
     for(c=1;c<v.length;c++)
     {
      td=document.getElementById(self.id+'_r'+r+'_c'+c)
      td.innerHTML=v[c]
     }
     return 0
    }
   }
  }

  var ontd=function()
  {
   var tr,td,r,c
   tr=document.getElementById(self.id+'_hd')
   r=this.id.split('_')[1].substring(1,this.id.split('_')[1].length)
   self.selection=self.table[r]
   for(r=0;r<self.table.length;r++)
   {
    for(c=1;c<self.header.length;c++)
    {
     td=document.getElementById(self.id+'_r'+r+'_c'+c)
     td.style.backgroundColor=""
     if(self.table[r][0]==self.selection[0]){td.style.backgroundColor="#FFCC80"}
    }
   }
   self.onselect()
  }


  if(!self.table){self.table=new Array()}
  else if(self.table.length>v[0]){update();return 0;}

  self.table[self.table.length]=new Array()
  self.table[self.table.length-1][0]=v[0]
  for(c=1; c<self.header.length; c++){document.getElementById(self.id+'_hd_c'+c).style.backgroundImage='url()'}
  tb=document.getElementById(self.id)
  tr=tb.insertRow([-1])
  tr.id=self.id+'_r'+v[0]
  for (c=1; c<self.header.length; c++)
  {
   td=tr.insertCell([-1])
   td.id=self.id+'_r'+v[0]+'_c'+c
   td.className=self.id+'_'+self.header[c]
   td.onclick=ontd
   td.innerHTML=v[c]
   self.table[self.table.length-1][c]=v[c]
  }

 },
   
 'select':function(self,v)
 {
  var r,c,td
  if(!self.table) return 0
  if(v=='-1')self.selection=new Array()
  for(r=0;r<self.table.length;r++)
  {
   for(c=0;c<self.header.length;c++)
   {
    if(self.table[r][0]==v)
    {
     self.selection[c]=self.table[r][c]
     if(c>0)
     {
      td=document.getElementById(self.id+'_r'+r+'_c'+c)
      td.style.backgroundColor='#FFCC80'
     }
    }
    else if(c>0)
    {
     td=document.getElementById(self.id+'_r'+r+'_c'+c)
     td.style.backgroundColor=''
    }
   }
  }
  if(v!='-1')self.onselect()
 },

 'init':function(self,xml)
 {
  var n,h,c,v,i,tb,th,tr,td,record,x,y
  var d=new Array()
  var r=0
  var onhd=function()
  {
   var c,r,a,b,n,td
   n=this.id.split('_hd_c')[0]
   for (c=1; c<self.header.length; c++){document.getElementById(n+'_hd_c'+c).style.backgroundImage='url()'}
   if(!self.table)return 0
   if(self.so==this.id)
   {
    self.so=''
    c=this.id.split('_hd_c')[1]
    self.table.sort
    (
     function(a,b) 
     { 
      if (a[c] > b[c]) return -1
      if (a[c] < b[c]) return 1
      return 0
     }
    )
    document.getElementById(n+'_hd_c'+c).style.backgroundImage="url('../bin/up.png')"
   }
   else
   {
    self.so=this.id
    c=this.id.split('_hd_c')[1]
    self.table.sort
    (
     function(a,b)
     {
      if (a[c] < b[c]) return -1
      if (a[c] > b[c]) return 1
      return 0
     }
    )
    document.getElementById(n+'_hd_c'+c).style.backgroundImage="url('../bin/down.png')"
   }
   for (r=0; r<self.table.length; r++) 
   {
    for (c=1; c<self.header.length; c++)
    {
     td=document.getElementById(n+'_r'+r+'_c'+c)
     td.innerHTML=self.table[r][c]
     td.style.backgroundColor=''
     if(self.table[r][0]==self.selection[0])td.style.backgroundColor='#FFCC80'
    }
   }
  }

  self.so='-1',
  self.header=['index']
  self.table=[]
  self.selection=[]

  while(x=xml.getElementsByTagName('record')[r])
  {
   record=new Array()
   record[0]=x.getAttribute('index')
   h=1;c=0;
   while(y=x.childNodes[c])
   {
    if(y.nodeType==1)
    {
     self.header[h]=y.nodeName
     v='';i=0;
     while(n=y.childNodes[i])
     {
      n=n.nodeValue
      n=n+''
      n=n.replace(/&lt;/g,'<')
      n=n.replace(/&gt;/g,'>')
      n=n.replace(/&amp;/g,'&')
      v+=n
      i++
     }
     record[h]=v
     h++
    }
    c++
   }
   d[r]=record
   r++
  }
 
  tb=document.createElement('table')
  tb.id=self.id
  th=tb.insertRow(-1)
  th.id=self.id+'_hd'
  for(c=1;c<self.header.length;c++)
  {
   td=th.insertCell(-1)
   td.id=self.id+'_hd_c'+c
   td.className='hd'
   td.onclick=onhd
   td.appendChild(document.createTextNode(self.header[c]))
  } 
  document.getElementById('c'+self.id).appendChild(tb) 
  for(r=0;r<d.length;r++){dg.insert(self,d[r])}
 }

}
