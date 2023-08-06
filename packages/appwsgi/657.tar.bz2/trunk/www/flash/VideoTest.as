// Copyright(c) gert.cuykens@gmail.com
// source: http://livedocs.adobe.com/flex/2/docs/wwhelp/wwhimpl/common/html/wwhelp.htm?context=LiveDocs_Parts&file=00001861.html#139750

package 
{

    import flash.display.Sprite;
    import flash.net.*;
    import flash.media.Video;

    public class VideoTest extends Sprite 
    {
        private var videoUrl:String = "test.flv";

        public function VideoTest() 
        {

            var connection:NetConnection = new NetConnection();
            connection.connect(null);

            var stream:NetStream = new NetStream(connection);

            var myVideo:Video = new Video(360, 240);
            myVideo.attachNetStream(stream);
            stream.play(videoUrl);

            addChild(myVideo);
        }
    }

}

