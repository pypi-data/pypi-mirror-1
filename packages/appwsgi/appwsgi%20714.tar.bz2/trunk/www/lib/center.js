// Copyright(c) gert.cuykens@gmail.com
center=
{
 'obj':function(obj)
 {
  var ww=obj.parentNode.offsetWidth
  var hh=obj.parentNode.offsetHeight
  var w= obj.offsetWidth
  var h= obj.offsetHeight
  obj.style.top = (hh/2) - (h/2) + 'px'
  obj.style.left = (ww/2) - (w/2) + 'px'
  //document.getElementById('window').style.left=window.pageXOffset+'px';
 }
}

//  <div id="window">
//   <div id="shadow"></div>
//   <div id="center" onclick="document.getElementById('window').style.display='none';document['myMovie'].stop()"></div>
//  </div>

