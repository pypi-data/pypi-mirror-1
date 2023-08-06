// Copyright(c) gert.cuykens@gmail.com

package
{
 import flash.display.Sprite;
 import flash.external.ExternalInterface;
 public class json extends Sprite
 {
  public function json():void
  {
   ExternalInterface.addCallback("test", callTest);
  }
  public function callTest():Object
  {
   var r:Object = ExternalInterface.call("test");
   var t:Object = {"t":"not ok"};
   if (r.t=="ok") t = {"t":"ok"};
   return t;
  }
 }
}

