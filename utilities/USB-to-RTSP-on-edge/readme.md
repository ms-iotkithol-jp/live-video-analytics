# Live Video from USB Camera to RTSP on IoT Edge
This module is developed from [USB-to-RTSP sample](../USB-to-RTSP) to be able to run on IoT Edge.
This document shows how to build on your IoT Edge device platform and deploy this module. 

## Building the IoT Edge Module
Run the following command in the solution folder, **... live-video-analytics/utilities/usb-to-rtsp-on-edge**.

```bash
sudo docker build -t rtspwebcam -f Dockerfile .
sudo docker tag rtspwebcam <your-repository>/rtspwebcam:<version>-<edge-platform>
sudo docker push <your-repository>/rtspwebcam:<version>-<edge platform>
```

## Deploy the <b>rtspwebcam</b> on IoT Edge device.
By Azure Portal add new Azure IoT Edge Module as follows.

### Name  
<b>rtspwebcam</b>

### Image URI  
\<your-repository\>/rtspwebcam:\<version\>-\<edge-platform\>

### Create Option  
```json
{
  "HostConfig": {
    "PortBindings": {
      "8554/tcp": [
        {
          "HostPort": "554"
        }
      ]
    },
    "Privileged": true,
    "Devices": [
      {
        "PathOnHost": "/dev/video0",
        "PathInContainer": "/dev/video0",
        "CgroupPermissions": "mrw"
      }
    ]
  }
}
```

From other modules, the RTSP stream of this module can be connected by 
- <b>rtsp://rtspwebcam:8554/stream1</b>


You can see the RTSP stream on your PC connected to same local network by  
- <b>rtsp://iot-edge-device-ip-address:8554/stream1</b>  

## Graph Instance Example  
On the LVA on Edge module side, video stream from this module can be refered as follow.  
Invoke GraphInstanceSet with following payload.  
```json
{
    "@apiVersion" : "1.0",
    "name" : "Sample-Graph-Webcam",
    "properties" : {
        "topologyName" : "MotionDetection",
        "description" : "Sample graph description",
        "parameters" : [
            { "name" : "rtspUrl", "value" : "rtsp://device-ip-address/stream1" }
        ]
    }
}
```


## Other Features  
Default VIDEO_PIPELINE is 
```
v4l2src device=/dev/video0 ! videoconvert ! videoscale! video/x-raw ! x264enc tune=zerolatency ! rtph264pay name=pay0
```
and this module write status and the video pipeline to reporeted properties.
```json
"reported": {
  "status": "ready",
  "videoPipeline": "current video pipeline statement",
```

You can change this video pipeline via deresied properties.
```json
"desired": {
  "videoPipeline": "current video pipeline statement",
```
This module doesn't have stop capability of RTSP stream. The desired properties update will be applyed at next restart.  

