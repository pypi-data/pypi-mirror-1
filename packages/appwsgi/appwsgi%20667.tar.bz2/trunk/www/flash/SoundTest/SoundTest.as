// Copyright(c) gert.cuykens@gmail.com
// http://scriptplayground.com/tutorials/as/Play-Sound-Samples-From-One-File-Using-ActionScript-3/

package  
{
    import flash.display.Sprite;
	import flash.events.*;
	import flash.media.Sound;
	import flash.media.SoundChannel;
	import flash.net.URLRequest;
	import flash.utils.Timer;
    import flash.external.ExternalInterface;

	public class SoundTest extends Sprite
	{
		private var song:SoundChannel;
		private var timer:Timer;
		private var soundFactory:Sound;
		private var endPoint:uint;
		
		public function SoundTest():void
		{
			soundFactory = new Sound();
			soundFactory.addEventListener(IOErrorEvent.IO_ERROR, ioErrorHandler);
			soundFactory.addEventListener(ProgressEvent.PROGRESS, progressHandler);	
			var request:URLRequest = new URLRequest("SoundTest.mp3");
			soundFactory.load(request);
            ExternalInterface.addCallback("playSound", playSound);
		}

		public function playSound():void
		{
            var start:uint=0;
            var end:uint=0;
			song = soundFactory.play(start);		
			if(end == 0)
			{
				endPoint = soundFactory.length;
			}
			else
			{
				endPoint = end;
			}
			enableTimer();
		}

		private function enableTimer():void
		{
			timer = new Timer(20);
			timer.addEventListener(TimerEvent.TIMER, timerHandler);
			timer.start();
		}

		private function timerHandler(event:TimerEvent):void 
		{
			if(uint(song.position.toFixed(2)) >= endPoint)
			{
				timer.stop();
				song.stop();
				soundComplete();
				return;
			}
		}
		
		private function soundComplete():void 
		{
			trace("Snippet finished playing");
		}
		
		private function ioErrorHandler(event:Event):void 
		{
			trace("ioErrorHandler: " + event);
		}
		
		private function progressHandler(event:ProgressEvent):void 
		{
			trace("progressHandler: " + event);
		}
		
	}
}

