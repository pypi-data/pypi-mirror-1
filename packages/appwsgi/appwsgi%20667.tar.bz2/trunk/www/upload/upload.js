// Copyright(c) gert.cuykens@gmail.com
upload=
{
 'open':function()
 {
  document.body.innerHTML='<a href="upload.htm">cancel</a> <a id="submit"></a>'+
                          '<form enctype="multipart/form-data" action="servlet" method="post">'+
                          ' <ul id="files">'+
                          '  <li>'+
                          '   <input type="file"   id="file0" name="file0" maxlength="0"/>'+
                          '   <input type="button" id="add" onclick="upload.add()" value="add"/>'+
                          '  </li>'+
                          ' </ul>'+
                          '</form>'
 },
 
 'add':function()
 {
  if(!document.getElementsByTagName('input')[0].value) return 0
  document.getElementsByTagName('input')[0].style.visibility='hidden'

  var li=document.createElement('li')
  li.onclick=function()
  {
   this.parentNode.removeChild(this)
   if(!document.getElementsByTagName('li')[1])
   {
    document.getElementById('submit').onclick=function(){}
    document.getElementById('submit').innerHTML=''
   }
  }
  li.appendChild(document.createTextNode('-> '+document.getElementsByTagName('input')[0].value))
  li.appendChild(document.getElementsByTagName('input')[0]);
  
  var submit=document.getElementById('submit')
  submit.innerHTML='submit'
  submit.name='submit'
  submit.type='submit'
  submit.value='submit'
  submit.onclick=function()
  {
   document.getElementsByTagName('li')[0].innerHTML=''
   document.getElementsByTagName('li')[0].appendChild(document.createTextNode('Uploading...'))
   document.getElementsByTagName('form')[0].submit()
   this.style.visibility='hidden'
  }
  
  var e
  if(e=document.getElementsByTagName('li')[1]) {document.getElementById('files').insertBefore(li,e)}
  else {document.getElementById('files').appendChild(li)}
  
  var input=document.createElement('input')
  input.id='file'+(document.getElementsByTagName('input').length-1)
  input.name='file'+(document.getElementsByTagName('input').length-1)
  input.type='file'
  input.setAttribute('maxlength',0)
  
  document.getElementsByTagName('li')[0].insertBefore(input,document.getElementById('add'))
  document.getElementsByTagName('li')[0].insertBefore(document.createTextNode(' '),document.getElementById('add'))
 }
 
}
