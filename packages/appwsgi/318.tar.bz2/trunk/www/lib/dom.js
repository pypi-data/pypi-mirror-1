dom=
{
 'parser':function(v)
 {
  if (window.ActiveXObject) // I HATE USING ActiveX !!!
  {
   var d=new ActiveXObject("Microsoft.XMLDOM")
   d.async="false"
   d.loadXML(v)
  }
  else
  {
   var d=new DOMParser()
   d=d.parseFromString(v,"text/xml")
  }
  return d
 }
}
