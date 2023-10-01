#How to record video: https://www.etutorialspoint.com/index.php/320-how-to-capture-a-video-in-python-opencv-and-save
# import the necessary packages
#current execute command: python3 /home/pi/Documents/Python/GitHub/VideoSample2/pi_surveillance.py

from pyimagesearch.tempimage import TempImage
from Servo import Servox
import imutils 
from imutils.video import VideoStream # must install: https://pypi.org/project/imutils/
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2
import os
#import threading
#from multiprocessing import Process #https://blog.devgenius.io/why-is-multi-threaded-python-so-slow-f032757f72dc

# https://learn.microsoft.com/en-us/python/api/overview/azure/cognitiveservices-vision-computervision-readme?view=azure-python
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import http.client, urllib.request, urllib.parse, urllib.error, base64
#Python 3.11.1

theServo=Servox(17)



# filter warnings, load the configuration
warnings.filterwarnings("ignore")
dir_path=os.path.dirname(os.path.realpath(__file__))
conf_path=os.path.join(dir_path,'conf.json')
conf=json.load(open(conf_path))  #conf = json.load(open(args["conf"]))
client = None
# https://westus.dev.cognitive.microsoft.com/docs/services//unified-vision-apis-public-preview-2022-10-12-preview/operations/61d65934cd35050c20f73ab6
headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': conf["azure_api_key"],
}
params = urllib.parse.urlencode({
    # Request parameters
    'features': 'tags',
    'model-version': 'latest',
    'language': 'en',
   # 'smartcrops-aspect-ratios': '{string}',
})


videoDeviceNumber=conf["videoDeviceNumber"]
filenameDateFormatString="%Y_%m_%d_%H_%M_%S"

vs=VideoStream(src=videoDeviceNumber).start()   # this works for external USB camera on new laptop: 0:internal; 2:external USB
#on the pi, deviceNumber0 works for the external USB camera
# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0
# capture frames from the camera
while True: #for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image and initialize
	# the timestamp and occupied/unoccupied text
	frame_raw=vs.read() #frame = f.array
	frame=frame_raw
	timestamp = datetime.datetime.now()
	text = "Unoccupied"
		

	# resize the frame, convert it to grayscale, and blur it
	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
	# if the average frame is None, initialize it
	if avg is None:
		print("[INFO] starting background model...")
		avg = gray.copy().astype("float")
		#rawCapture.truncate(0)
		continue
	#qprint("[INFO] waiting for scene changes...")
	# accumulate the weighted average between the current frame and
	# previous frames, then compute the difference between the current
	# frame and running average
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    	# threshold the delta image, dilate the thresholded image to fill
	# in holes, then find contours on thresholded image
	thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,
		cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < conf["min_area"]:
			continue

		contourArea=cv2.contourArea(c)
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Motion Detected"

	# draw the text and timestamp on the frame
	ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35, (0, 0, 255), 1)
        # check to see if the room is occupied
	if text == "Motion Detected":
		# check to see if enough time has passed between uploads
		if (timestamp - lastUploaded).seconds >= conf["wait_between_detections_seconds"]:
			# increment the motion counter
			motionCounter += 1
			hasCat=False
			detectionTags=conf["trigger_objects"]

			# check to see if the number of frames with consistent motion is high enough
			if motionCounter >= conf["min_motion_frames"]:
				motionCount=0 #reset
				print("[INFO] - MOTION DETECTED-"+datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p")) 
                # write the image to temporary file
				t = TempImage()
				cv2.imwrite(t.path, frame)
#### AZURE ###
				azureStartTime = datetime.datetime.now()
				lastUploaded=azureStartTime
				with open(t.path, 'rb') as f:
					data = f.read()
				try:
					hasCat=False
					print("[INFO] making AZURE request-",datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))
					conn = http.client.HTTPSConnection('cattraps.cognitiveservices.azure.com')
					conn.request("POST", "/computervision/imageanalysis:analyze?api-version=2022-10-12-preview&%s" % params, data, headers)
					response = conn.getresponse()
					responseData = response.read()
					azureEndTime = datetime.datetime.now()
					azureSeconds=(azureEndTime-azureStartTime).seconds
					print("[INFO]:upload time in seconds",azureSeconds,datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))
					conn.close()		
					print("after conn.close")
					pythonObj=json.loads(responseData)
					# print (responseData)
					# print("pythonObj: ", pythonObj["tagsResult"])
					tags=pythonObj["tagsResult"]
					detectionText=""
					for object in tags["values"]:		
						print(object["name"], object["confidence"])						
						if ((object["name"] in detectionTags) and (object["confidence"] > conf["confidence_threshold"])):								
							print(object["name"], object["confidence"])									
							hasCat=True
							detectionText+=object["name"]+":"+str(round(object["confidence"],2))+"; "

					if hasCat == False:  #Delete the temp image if desired object not detected
						t.cleanup()
					else:
						print("[INFO] Start Video Capture: ",datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))
						captureStartTime = datetime.datetime.now()		
						startTimeString = captureStartTime.strftime("%A %d %B %Y %I_%M_%S%p")
						servoTriggerTimeString=""
						
						videoFileName="/ImageFiles/"+datetime.datetime.now().strftime(filenameDateFormatString)+".avi"	
						videoFilePath="{0}{1}".format(dir_path,videoFileName)		
						# #try this: https://www.etutorialspoint.com/index.php/320-how-to-capture-a-video-in-python-opencv-and-save
						#The codec's seem to be here - not sure if needed or not: https://github.com/cisco/openh264/releases
						
						video_output=cv2.VideoWriter(videoFilePath,cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),50, tuple(conf["resolution"]))
						servoTriggered=False
						startTimeCaptured=False
						while  ((datetime.datetime.now()-captureStartTime).seconds < conf["video_recording_seconds"]) :
							textOutputPixelY=10
							frame_raw=vs.read() 
							cv2.putText(frame_raw, "{}".format(startTimeString+" ContourArea: "+"{:.0f}".format(contourArea)), (10,textOutputPixelY),
									cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
							textOutputPixelY+=10
							if (startTimeCaptured == False):
								startTimeCaptured=True
								servoTriggerStartTime = datetime.datetime.now()		
								servoTriggerTimeString = servoTriggerStartTime.strftime("%A %d %B %Y %I_%M_%S%p")
							cv2.putText(frame_raw, "{}".format(servoTriggerTimeString), (10,textOutputPixelY),
									cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
							textOutputPixelY+=10
							
							for object in tags["values"]:	#print the objects detected to the frame											
								detectionText=object["name"]+":"+str(round(object["confidence"],2))+"; "
								cv2.putText(frame_raw, "{}".format(detectionText), (10,textOutputPixelY),
									cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
								textOutputPixelY+=15
							video_output.write(frame_raw)
							if (servoTriggered==False) and ((datetime.datetime.now()-captureStartTime).seconds) > .5:
								servoTriggered=True
								theServo.trigger()
							if (servoTriggered==True) and ((datetime.datetime.now()-captureStartTime).seconds) > 1.5:								
								theServo.stopMotion()
								servoTriggered=False

						print("[INFO] Video capture stopped: ",datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))
						video_output.release()
						theServo.resetPosition()
#### END AZURE					
				except Exception as e:
					print("[ErrNo {0}] {1}".format("error", e))

	else:
		motionCounter = 0
####################################################################
	# check to see if the frames should be displayed to screen
	if conf["show_video"]:
		# display the security feed
		cv2.imshow("Cat-Cam", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key is pressed, break from the loop
		if key == ord("q"):
			theServo.cleanup()
			break
