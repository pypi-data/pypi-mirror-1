//Copyright(c) gert.cuykens@gmail.com 
//Patent IE7 work around, yes its realy realy sad 

player=
{

 'obj':function() 
 {
  var isIE = navigator.appName.indexOf("Microsoft") != -1;
  return (isIE) ? window['flowplayer'] : document['flowplayer'];
 },

 'write':function()
 {
  document.write('   <object id="flv"                                        ')
  document.write('           type="application/x-shockwave-flash"            ')
  document.write('           data="../bin/flowplayer.swf">                   ')
  document.write('    <param name="movie" value="../bin/flowplayer.swf"/>    ')
  document.write('    <param name="allowScriptAccess" value="sameDomain"/>   ') 
  document.write('    <param name="quality" value="high"/>                   ')
  document.write('    <param name="scale" value="noScale"/>                  ')
  document.write('    <param name="wmode" value="transparent"/>              ')
  document.write('    <param name="allowFullScreen" value="true"/>           ')
  document.write('    <param name="bgcolor" value="transparent"/>            ')
  document.write('    <param name="flashvars" value="config=                 ')
  document.write('    {                                                      ')
  document.write('     initialScale: \'orig\',                               ')
  document.write('     showMenu: false,                                      ')
  document.write('     showFullScreenButton: false,                          ')
  document.write('     autoPlay: true,                                       ')
  document.write('     autoRewind: false,                                    ')
  document.write('     autoBuffering: true,                                  ')
  document.write('     loop: false,                                          ')
  document.write('     showPlayListButtons: false,                           ')
  //document.write('     hideControls: true,                                 ')
  document.write('     playList: [{url:\'../bin/roel.flv\'},                 ')
  document.write('                {url:\'../bin/continue.png\'}]             ')
  document.write('    }"/>                                                   ')
  document.write('   </object>                                               ')  
 }

}

