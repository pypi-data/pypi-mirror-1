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

  public function sound():void
  {
   ExternalInterface.addCallback("play", play);
   ExternalInterface.addCallback("stop", stop);
   stage.quality = "best";
  }

  public function play(v:String):void
  {
   var url:URLRequest = new URLRequest(v);

   var snd:Sound = new Sound();
   snd.load(url);
   snd.addEventListener(Event.ID3, id3Handler);
   snd.addEventListener(IOErrorEvent.IO_ERROR, ioErrorHandler);
   snd.addEventListener(ProgressEvent.PROGRESS, progressHandler);
   //snd.addEventListener(Event.SOUND_COMPLETE, loadCompleteHandler);
   //snd.close()
 
   var transform:SoundTransform = new SoundTransform();
   transform.volume = 1;

   channel.stop();
   channel = snd.play();
   channel.addEventListener (Event.SOUND_COMPLETE, soundCompleteHandler);
   channel.soundTransform = transform;
  }

  public function stop():void
  {
   channel.stop();
  }

  private function id3Handler(e:Event):void 
  {
   trace("id3Handler: "+e);
  }

  private function ioErrorHandler(e:Event):void 
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

