// Copyright(c) gert.cuykens@gmail.com
package 
{
 import flash.display.Sprite;
 import flash.external.ExternalInterface;
 public class JsTest extends Sprite
 {	
  public function JsTest():void 
  {
   ExternalInterface.addCallback("test", callTest);
  }
  public function callTest():void
  {
   var result:Object = ExternalInterface.call("test");
  }
 }
}

/* 
package com.Test
{
 import flash.display.MovieClip;
 import flash.events.*;
 import com.io.Upload;
 import com.animation.Play;

 public class Test extends MovieClip
 {

  public function Test()
  {
   _root.watch("jsCall", jsEvent);
   upload()
   animation()
  }

  jsEvent = function(id, oldValue, newValue):String {}

  private function upload()
  { 
   f = new Upload();
   this.addEventListener(...,f.onUpload);
   f.addEventListener(f...,onUpload);
   e = new Event(...);
   dispatchEvent(e);
  }

  private function onUpload(e:Event):void
  {
   var f:FileUpload=Upload.file(e.target);
   trace("image uploaded");
  }

}

package com.animation
{

 public class Play
 {

  function Play()
  {
   var xmlString:URLRequest = new URLRequest("animation.xml");
   var xmlLoader:URLLoader = new URLLoader(xmlString);
   xmlLoader.addEventListener("complete", init);
  }

  function init(e:Event):void
  {
   var document:XMLDocument = new XMLDocument();
   document.ignoreWhite = true;
   var animationXML:XML = XML(xmlLoader.data);
   document.parseXML(animationXML.toXMLString());
   trace(document.firstChild.childNodes[0]);
  }

 }
}


package com.io
{
 import flash.events.*;
 import flash.net.*;
 import flash.events.*;

 public class Upload
 {
  private var http:URLRequest;

  public function Upload()
  {
   super();
   http         = new URLRequest();
   http.url     = "../upload/servlet";
  }

  public function file(e:Event)
  {
   ff=new FileFilter("Images", "*.jpg;*.gif;*.png")
   f=new FileReference();
   f.addEventListener(Event.SELECT,onSelect);
   f.addEventListener(IOErrorEvent.IO_ERROR,onError);
   f.addEventListener(Event.COMPLETE, onComplete);
   f.browse([ff]);
  }

  private function onSelect(e:Event):void
  {
   var file:FileReference = FileReference(e.target);
   trace("selectHandler: " + file.name);
   file.upload(http)
  }

  private function onError(e:IOErrorEvent) 
  {
   trace("error "+e.toString())
  }

  private function onComplete(e:Event)
  {
   var ee:Event=new Event("onUpload");
   dispatchEvent(ee);
  }

 }
}
*/
