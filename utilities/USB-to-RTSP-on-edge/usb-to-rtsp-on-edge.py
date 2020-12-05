import sys
import time
import gi
import os
import logging
import asyncio
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient
from azure.iot.device import MethodResponse
import subprocess
from subprocess import PIPE

logging.basicConfig(level=logging.DEBUG)

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject, GLib

import asyncio_glib
asyncio.set_event_loop_policy(asyncio_glib.GLibEventLoopPolicy())

loop = asyncio.get_event_loop()

module_status = {
    "status":"ready",
    "videoPipeline" : "v4l2src device=/dev/video0 ! videoconvert ! videoscale! video/x-raw ! x264enc tune=zerolatency ! rtph264pay name=pay0"
    }

Gst.init(None)

class USBtoRtspMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self):
#        self.videoPipeline = os.getenv('VIDEO_PIPELINE')
        self.videoPipeline = module_status["videoPipeline"]
        if self.videoPipeline is None:
            self.videoPipeline = "v4l2src device=/dev/video0 ! videoconvert ! videoscale! video/x-raw ! x264enc tune=zerolatency ! rtph264pay name=pay0"

        GstRtspServer.RTSPMediaFactory.__init__(self)

    def do_create_element(self, url):
        logging.info("Video pipeline to be used: {0}".format(self.videoPipeline)) 
        return Gst.parse_launch(self.videoPipeline)

class GstreamerRtspServer():
    def __init__(self):
        self.rtspServer = GstRtspServer.RTSPServer()
        factory = USBtoRtspMediaFactory()
        factory.set_shared(True)
        mountPoints = self.rtspServer.get_mount_points()
        mountPoints.add_factory("/stream1", factory)
        self.rtspServer.attach(None)

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        async def method_request_handler(method_request):
            payload = {"result": True, "data": "There is no direct method current."}  # set response payload
            status = 200  # set return status code
            print("invoked method: " + method_request.name)
            if method_request.name == "ShellCommandExecute":
                if "command" in method_request.payload and "args" in method_request.payload:
                    commandStr = method_request.payload["command"]
                    argsStr = method_request.payload["args"]
                    proc = subprocess.run("{} {}".format(commandStr, argsStr), shell=True, stdout=PIPE)
                    payload = {"result":  str(proc.stdout)}
                else:
                    payload = {"request":"bad payload. command and args are necessary!"}
                    status = 400

            print("invoked method: " + method_request.name)
            # Send the response
            method_response = MethodResponse.create_from_method_request(method_request, status, payload)
            await module_client.send_method_response(method_response)

        module_client.on_method_request_received = method_request_handler

        # connect the client.
        await module_client.connect()

        print('Get current desired properties...')
        currentTwin = await module_client.get_twin()
        if 'videoPipeline' in currentTwin['desired'] :
            module_status['videoPipeline'] = currentTwin['desired']['videoPipeline']
            print("Indicated new video pipeline - %s" % module_status['videoPipeline'])

        print("module_status={}".format(module_status))

        print("Starting RTSP Stream...")
        s = GstreamerRtspServer()
        print("Started RTSP Stream...")

        module_client.patch_twin_reported_properties(module_status)

        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)

        user_finished = loop.run_in_executor(None, stdin_listener)
        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Finally, disconnect
        await module_client.disconnect()


    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == '__main__':
    loop.run_until_complete(main())
