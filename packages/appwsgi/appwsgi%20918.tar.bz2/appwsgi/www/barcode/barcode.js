// Copyright(c) gert.cuykens@gmail.com
barcode=
{
 'image':function()
 {
  var img
  if(img=document.getElementById('png'))img.parentNode.removeChild(img)
  img=document.createElement('img')
  img.src='barcode.py?'+document.getElementById('bnr').value
  img.id='png'
  document.body.appendChild(img)
 }
}

