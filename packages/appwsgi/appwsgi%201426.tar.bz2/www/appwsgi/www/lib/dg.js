// Copyright(c) gert.cuykens@gmail.com
dg=
{

 'remove':function(self,r)
 {
  var c,td,tb
  if(r<self.rec.length-1){self.rec[r]=self.rec.pop()}else{self.rec.pop()}
  dg.init(self)
 },

 'update':function(self,r,v)
 {
  var c,td
  for(c=0;c<v.length;c++)
  {
   td=document.getElementById(self.id+'-row-'+r+'-col-'+c)
   td.innerHTML=v[c]
  }
  self.rec[r]=v
 },

 'insert':function(self,r)
 {
  var tb,tr,td,c,r

  var ontd=function()
  {
   var tr,td,r,c,s
   s=this.id.split('-row-')[1].split('-col-')[0]
   self.selection=self.rec[s]
   for(r=0;r<self.rec.length;r++)
   {
    for(c=0;c<self.des.length;c++)
    {
     td=document.getElementById(self.id+'-row-'+r+'-col-'+c)
     td.style.backgroundColor=""
     if(r==s){td.style.backgroundColor="#FFCC80"}
    }
   }
   self.onselect()
  }

  for(c=0; c<self.des.length; c++){document.getElementById(self.id+'-des-'+c).style.backgroundImage='url()'}
  tb=document.getElementById(self.id)
  tr=tb.insertRow(-1)
  tr.id=self.id+'-row-'+r
  for (c=0; c<self.des.length; c++)
  {
   td=tr.insertCell(-1)
   td.id=self.id+'-row-'+r+'-col-'+c
   td.onclick=ontd
   td.innerHTML=self.rec[r][c]
  }
 },

'select':function(self,r)
{
 var tb=document.getElementById(self.id).childNodes[0],i=0
 for(i=1;i<tb.childNodes.length;i++)
 {
  var tr=tb.childNodes[i],j=0
  for(j=0;j<tr.childNodes.length;j++)
  {
   var td=tr.childNodes[j]
   if(td.style){td.style.backgroundColor='#ffffff';if(r==i-1)td.style.backgroundColor='#FFCC80';}
  }
 }
 if(r>-1){self.selection=rec[r]}else{self.selection=[]}
},

 'init':function(self)
 {
  if(!self.des)return 0;
  var r,c,tb,th,td
  var onhd=function()
  {
   var c,r,a,b,n,td
   n=this.id.split('-des-')[0]
   for (c=0; c<self.des.length; c++){document.getElementById(n+'-des-'+c).style.backgroundImage='url()'}
   if(self.so==this.id)
   {
    self.so=''
    c=this.id.split('-des-')[1]
    self.rec.sort(function(a,b){if (a[c] > b[c]) return -1;if (a[c] < b[c]) return 1;return 0})
    document.getElementById(n+'-des-'+c).style.backgroundImage="url('../bin/up.png')"
   }
   else
   {
    self.so=this.id
    c=this.id.split('-des-')[1]
    self.rec.sort(function(a,b){if (a[c] < b[c]) return -1;if (a[c] > b[c]) return 1;return 0})
    document.getElementById(n+'-des-'+c).style.backgroundImage="url('../bin/down.png')"
   }
   for (r=0; r<self.rec.length; r++) 
   {
    for (c=0; c<self.des.length; c++)
    {
     td=document.getElementById(n+'-row-'+r+'-col-'+c)
     td.innerHTML=self.rec[r][c]
     td.style.backgroundColor=''
    }
   }
  }

  self.so='-1'
  self.selection=[]
 
  tb=document.createElement('table')
  tb.id=self.id
  th=tb.insertRow(-1)
  th.id=self.id+'-des'
  for(c=0;c<self.des.length;c++)
  {
   td=th.insertCell(-1)
   td.id=self.id+'-des-'+c
   td.className='des'
   td.onclick=onhd
   td.appendChild(document.createTextNode(self.des[c]))
  }
  document.getElementById(self.id+'-dg').innerHTML=''
  document.getElementById(self.id+'-dg').appendChild(tb)
  for(r=0;r<self.rec.length;r++){dg.insert(self,r)}
 }

}
