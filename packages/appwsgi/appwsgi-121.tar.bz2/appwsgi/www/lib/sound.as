// Copyright(c) gert.cuykens@gmail.com

package  
{
 import flash.display.Sprite;
 import flash.media.Sound;
 import flash.media.SoundChannel;
 import flash.media.SoundTransform;
 import flash.net.URLRequest;
 import flash.external.ExternalInterface;
 import flash.events.*;

 public class sound extends Sprite
 {
  private var channel:SoundChannel = new SoundChannel();
  private var snd:Sound;
  private var pause:int = 0;

  public function sound():void
  {
   ExternalInterface.addCallback("load", load);
   ExternalInterface.addCallback("play", play);
   ExternalInterface.addCallback("stop", stop);
   stage.quality = "best";
  }

  public function load(v:String):void
  {
   var url:URLRequest = new URLRequest(v);
   snd = new Sound();
   snd.load(url);
   snd.addEventListener(Event.ID3, id3Handler);
   snd.addEventListener(IOErrorEvent.IO_ERROR, ioErrorHandler);
  }

  public function play():void
  {
   channel.stop();
   channel = snd.play();
   channel.soundTransform = new SoundTransform();; 
   channel.addEventListener(Event.SOUND_COMPLETE, soundCompleteHandler);
  }

  public function stop():void
  {
   if(pause==0)
   {
    pause=channel.position;
    channel.stop();
   }
   else
   {
    channel.stop();
    channel = snd.play(pause);
    channel.soundTransform = new SoundTransform();; 
    channel.addEventListener(Event.SOUND_COMPLETE, soundCompleteHandler);
    pause=0;
   }
  }

  private function id3Handler(e:Event):void 
  {
   trace("id3Handler: "+e);
  }

  private function ioErrorHandler(e:IOErrorEvent):void 
  {
   trace("ioErrorHandler: "+e);
  }
	
  private function progressHandler(e:ProgressEvent):void 
  {
   var result:Object = ExternalInterface.call("sound.progress",e.bytesLoaded,e.bytesTotal);
  }

  private function soundCompleteHandler(e:Event):void 
  {
   var result:Object = ExternalInterface.call("sound.complete");
  }
	
 }
}

