// Copyright(c) gert.cuykens@gmail.com
// http://livedocs.adobe.com/flex/3/html/help.html?content=Working_with_Video_10.html
// http://livedocs.adobe.com/flash/9.0/main/wwhelp/wwhimpl/common/html/wwhelp.htm?context=LiveDocs_Parts&file=00000282.html

package {

    import flash.display.Sprite;
    import flash.events.*;
    import flash.net.*;
    import flash.media.Video;

    public class VideoTest extends Sprite {

        public var myVideo:Video = new Video();

        public function VideoTest() {
            var client:Object = new Object();
            client.onMetaData = metaDataHandler;
            
            var connection:NetConnection = new NetConnection();
            connection.connect(null);

            var stream:NetStream = new NetStream(connection); 
            stream.addEventListener(AsyncErrorEvent.ASYNC_ERROR, asyncErrorHandler); 
            stream.addEventListener("cuePoint", cuePoint);
            stream.play("VideoTest.flv");
            stream.client = client;

            myVideo.attachNetStream(stream);
            myVideo.x=-50
            myVideo.y=-12
            addChild(myVideo);
        }

        public function asyncErrorHandler(event:AsyncErrorEvent):void {
            trace(event.text);
        }
        
        public function metaDataHandler(metaObject:Object):void {
            myVideo.width = metaObject.width;
            myVideo.height = metaObject.height;
            //var k:String;
            //for (k in metaObject) {
            // trace(k + ": " + metaObject[k]);
            //}
        }

        public function cuePoint (event:Object):void {
          //trace("Elapsed time in seconds: " + stream.playheadTime);
          trace("Cue point name is: " + event.info.name);
          trace("Cue point type is: " + event.info.type);
        }
 
    }
}

