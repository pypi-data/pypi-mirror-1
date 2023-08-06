// Copyright(c) gert.cuykens@gmail.com
package
{
 import flash.display.Sprite;
 import flash.display.LoaderInfo;
 import flash.external.ExternalInterface;
 import flash.net.FileReference;
 import flash.net.FileReferenceList;
 import flash.net.URLRequest;
 import flash.net.URLRequestMethod;
 import flash.net.URLRequestHeader;
 import flash.events.*;

 public class upload extends Sprite
 {
  private var fileList:FileReferenceList = new FileReferenceList();

  public function upload():void
  {
   fileList.addEventListener(Event.SELECT,onSelect);
   ExternalInterface.addCallback("cancel", onCancel);
   //ExternalInterface.addCallback("browse", onBrowse); *** and then there was flash 10 MFU ***
   stage.addEventListener(MouseEvent.MOUSE_DOWN, onBrowse);
   stage.scaleMode = "noScale";
   stage.align = "TL";
   stage.quality = "best";
  }

  private function onBrowse(e:Event):void
  {
   fileList.browse();
  }

  private function onCancel():void
  {
   var file:FileReference = new FileReference();
   for (var i:uint = 0; i < fileList.fileList.length; i++)
   {
    file = FileReference(fileList.fileList[i]);
    file.cancel();
   }
   var rt:Object = ExternalInterface.call("upload.cancel");
  }

  private function onSelect(e:Event):void
  {
   var url:String = LoaderInfo(root.loaderInfo).parameters.url;
   var sid:Object = ExternalInterface.call("upload.select");
   var header:URLRequestHeader = new URLRequestHeader("Content-type", "text/plain");
   var http:URLRequest = new URLRequest();
   http.url = url+"?"+sid;
   http.method = URLRequestMethod.POST;
   http.requestHeaders.push(header);
   trace("FileUpload: "+http.url);
   var file:FileReference = new FileReference();
   for (var i:uint = 0; i < fileList.fileList.length; i++)
   {
    file = FileReference(fileList.fileList[i]);
    file.addEventListener(ProgressEvent.PROGRESS,onProgress);
    file.addEventListener(Event.COMPLETE, onComplete);
    file.addEventListener(IOErrorEvent.IO_ERROR, onError);
    file.addEventListener(DataEvent.UPLOAD_COMPLETE_DATA,onCompleteData);
    file.upload(http)
    trace("FileName: "+file.name);
   }
  }

  private function onProgress(e:ProgressEvent):void
  {
   var file:FileReference = FileReference(e.target);
   var rt:Object = ExternalInterface.call("upload.progress", file.name, e.bytesLoaded, e.bytesTotal);
   trace("File: "+file.name+" Bytes: "+e.bytesLoaded+" Total: "+e.bytesTotal);
  }

  private function onError(e:IOErrorEvent):void 
  {
   var file:FileReference = FileReference(e.target);
   var rt:Object = ExternalInterface.call("upload.error", file.name+" "+e.text);
   trace(file.name+" "+e.text);
  }

  private function onComplete(e:Event):void
  {
   var file:FileReference = FileReference(e.target);
   var rt:Object = ExternalInterface.call("upload.complete", file.name);
   trace("Upload: "+file.name+" complete");
  }

  private function onCompleteData(e:DataEvent):void 
  {
   var rt:Object = ExternalInterface.call("upload.server", e.text);
   trace("Server: "+e.text);
  }
 }
}

