import flash.display.LoaderInfo;
var flv:String = LoaderInfo(this.root.loaderInfo).parameters.flv;

import flash.net.URLLoader;
var loader:URLLoader = new URLLoader();
loader.addEventListener(ProgressEvent.PROGRESS,progressHandler);
loader.load(request);

public function progressHandler(e:ProgressEvent):void
{
 var l:Number = Math.round(e.bytesLoaded/e.bytesTotal * 100);
}
