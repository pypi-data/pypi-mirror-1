// Copyright(c) gert.cuykens@gmail.com

package 
{
 import flash.display.Sprite;
 import flash.media.Video;
 import flash.media.SoundTransform;
 import flash.net.NetConnection;
 import flash.net.NetStream;
 import flash.net.URLRequest;
 import flash.ui.ContextMenu;
 import flash.ui.ContextMenuItem;
 import flash.external.ExternalInterface;
 import flash.events.*;

 public class video extends Sprite 
 {
  public var stream:NetStream;
      
  public function video() 
  {
   var seek:ContextMenuItem = new ContextMenuItem("seek");
   seek.addEventListener(ContextMenuEvent.MENU_ITEM_SELECT,seekHandler);

   var fullscreen:ContextMenuItem = new ContextMenuItem("fullscreen");
   fullscreen.addEventListener(ContextMenuEvent.MENU_ITEM_SELECT,fullscreenHandler);
 
   var menu:ContextMenu = new ContextMenu();
   menu.hideBuiltInItems();
   menu.customItems.push(seek);  
   menu.customItems.push(fullscreen);
 
   contextMenu = menu;
   stage.scaleMode = "noScale";
   stage.align = "TL";
   stage.quality = "best";
 
   ExternalInterface.addCallback("play",play);
   ExternalInterface.addCallback("stop",stop);

   var connection:NetConnection = new NetConnection();
   connection.addEventListener(NetStatusEvent.NET_STATUS, netStatusHandler);
   connection.addEventListener(SecurityErrorEvent.SECURITY_ERROR, securityErrorHandler);
   connection.connect(null);

   var transform:SoundTransform = new SoundTransform();
   transform.volume = 1;

   stream = new NetStream(connection);
   stream.addEventListener(AsyncErrorEvent.ASYNC_ERROR, asyncErrorHandler);
   stream.addEventListener(NetStatusEvent.NET_STATUS, netStatusHandler);
   stream.addEventListener("cuePoint", cuePointHandler);
   stream.addEventListener("metaData", metaDataHandler);
   stream.soundTransform=transform;

   var screen:Video = new Video();
   screen.attachNetStream(stream);
   addChild(screen);
  }

  public function play(url:String):void
  {
   stream.play(url);
  }

  public function stop():void 
  {
   stream.togglePause();
  }

  public function asyncErrorHandler(e:AsyncErrorEvent):void 
  {
   trace(e.text);
  }
  
  private function securityErrorHandler(e:SecurityErrorEvent):void 
  {
   trace("securityErrorHandler:"+e);
  }

  public function netStatusHandler(e:NetStatusEvent):void 
  {
   switch (e.info.code) 
   {
    case "NetConnection.Connect.Success":
     trace("Connection ok");
    break;
    case "NetStream.Play.StreamNotFound":
     trace("Video not found");
    break;
    case "NetStream.Buffer.Full":
    break;
    case "NetStream.Buffer.Empty": 
    break;
    case "NetStream.Play.Stop":
     var result:Object = ExternalInterface.call("video.complete");
    break; 
   }
  }

  public function cuePointHandler(o:Object):void 
  {
   trace("time: " + o.cuePointTime);
   trace("name: " + o.cuePointName);
   trace("type: " + o.cuePointType);
  }

  public function metaDataHandler(o:Object):void 
  {
   //screen.width = o.width;
   //screen.height = o.height;
   var s:String;
   for (s in o) { trace(s + ": " + o[s]); }
  }

  public function fullscreenHandler(e:ContextMenuEvent):void
  {
   stage.displayState = "fullScreen";
  }
        
  public function seekHandler(e:Event):void
  {
   //if(this.bufferbar._visible==false){this.bufferbar._visible=true;}
   //else{this.bufferbar._visible=false;}
  }

 }
}
