// Copyright(c) gert.cuykens@gmail.com
// http://livedocs.adobe.com/flex/3/langref/flash/media/Sound.html

package  
{
    import flash.display.Sprite;
	import flash.events.*;
	import flash.media.Sound;
    import flash.media.SoundChannel;
	import flash.net.URLRequest;
    import flash.external.ExternalInterface;
    import flash.display.LoaderInfo;

	public class SoundTest extends Sprite
	{
		private var soundFactory:Sound;
        private var song:SoundChannel;

		public function SoundTest():void
		{
         ExternalInterface.addCallback("play", play);
         ExternalInterface.addCallback("loop", loop);
         ExternalInterface.addCallback("stop", stop);
         var l:String = LoaderInfo(this.root.loaderInfo).parameters.loop;
         if (l) loop(l);
		}

        private function loading(request:URLRequest):void
        {
	     soundFactory = new Sound();
		 soundFactory.addEventListener(IOErrorEvent.IO_ERROR, ioErrorHandler);
		 soundFactory.addEventListener(ProgressEvent.PROGRESS, progressHandler);
         soundFactory.load(request);
        }

        private function play(mp3:String):void
        {
         if (song != null) return;
         var request:URLRequest = new URLRequest(mp3);
         loading(request);
         song = soundFactory.play(0,0);
         song.addEventListener(Event.SOUND_COMPLETE, soundCompleteHandler);
        }

        private function loop(mp3:String):void
        {
         if (song != null) return;
         var request:URLRequest = new URLRequest(mp3);
         loading(request);
         song = soundFactory.play(0,99999999);
        }

        private function stop():void
        {
         song.stop();
         song=null;
        }

        private function ioErrorHandler(event:Event):void 
	    {
		 trace("ioErrorHandler: " + event);
	    }
		
	    private function progressHandler(event:ProgressEvent):void 
	    {
		 trace("progressHandler: " + event);
	    }

        private function soundCompleteHandler(event:Event):void 
        {
         song=null;
        }
	
    }
}

