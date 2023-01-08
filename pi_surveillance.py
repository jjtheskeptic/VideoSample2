#How to record video: https://www.etutorialspoint.com/index.php/320-how-to-capture-a-video-in-python-opencv-and-save
#comment
# import the necessary packages
from pyimagesearch.tempimage import TempImage
#from picamera.array import PiRGBArray
#from picamera import PiCamera.
import imutils 
from imutils.video import VideoStream # must install: https://pypi.org/project/imutils/
import argparse
import warnings
import datetime
#import dropbox
import imutils
import json
import time
import cv2

import os
# https://learn.microsoft.com/en-us/python/api/overview/azure/cognitiveservices-vision-computervision-readme?view=azure-python
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import http.client, urllib.request, urllib.parse, urllib.error, base64
#
#Python 3.11.1


# filter warnings, load the configuration and initialize the Dropbox
# client
warnings.filterwarnings("ignore")
conf=json.load(open("conf.json"))#conf = json.load(open(args["conf"]))
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

# check to see if the Dropbox should be used
if conf["use_dropbox"]:
    # connect to dropbox and start the session authorization process
    client = dropbox.Dropbox(conf["dropbox_access_token"])
    print("[SUCCESS] dropbox account linked")
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
apiCallCounter=0
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

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		text = "Occupied"

	# draw the text and timestamp on the frame
	ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35, (0, 0, 255), 1)
##### UPLOAD TO DROPBOX #######
        # check to see if the room is occupied
	if text == "Occupied":
#		# check to see if enough time has passed between uploads
		if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
#			# increment the motion counter
			motionCounter += 1
			hasCat=False
			catTags=["cat","kitty","kitten","felidae","dog","hand"]

			# check to see if the number of frames with consistent motion is
			# high enough
			if motionCounter >= conf["min_motion_frames"]:
				print("[INFO] - MOTION DETECTED-"+datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p")) 
                # write the image to temporary file
				t = TempImage()
				cv2.imwrite(t.path, frame)
				#cv2.imwrite("./ImageFiles/",frame) ## JJ testing
#### AZURE ###
				# Read file
				if 1==1:  #testing to exclude azure
					azureStartTime = datetime.datetime.now()
					lastUploaded=azureStartTime
					with open(t.path, 'rb') as f:
						data = f.read()
					try:
						hasCat=False
						print("[INFO] making POST request-",datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))
						conn = http.client.HTTPSConnection('cattraps.cognitiveservices.azure.com')
						apiCallCounter+=1
						conn.request("POST", "/computervision/imageanalysis:analyze?api-version=2022-10-12-preview&%s" % params, data, headers)
						print("[INFO] POST complete-",datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))
						response = conn.getresponse()
						responseData = response.read()
						azureEndTime = datetime.datetime.now()
						azureSeconds=(azureEndTime-azureStartTime).seconds
						print("[INFO]:upload time in seconds",azureSeconds,datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))
						conn.close()		
						pythonObj=json.loads(responseData)
						#print(pythonObj["tagsResult"])
						tags=pythonObj["tagsResult"]
						for object in tags["values"]:
							if hasCat==True:
								break
							if object["name"] in catTags:
								if object["confidence"] > .6:
									print(object["name"], object["confidence"])
									hasCat=True
									
										
						
						print ("numCalls:",apiCallCounter)
						#t.cleanup() #delete the temp image
						if hasCat == False:  #Delete the temp image if no cat detected
							#if 1==2:
							t.cleanup()
						else:
							print("capture video here",datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))
							captureStartTime = datetime.datetime.now()		
							startTimeString = captureStartTime.strftime("%A %d %B %Y %I_%M_%S%p")	
							videoFileName="./ImageFiles/Capture_"+datetime.datetime.now().strftime(filenameDateFormatString)+".avi"			
							# #### Here is where I need to record a few seconds of video
							# #try this: https://www.etutorialspoint.com/index.php/320-how-to-capture-a-video-in-python-opencv-and-save
							#The codec's seem to be here - not sure if needed or not: https://github.com/cisco/openh264/releases
							#cap=cv2.VideoCapture(videoDeviceNumber)
							#if (cap.isOpened() == False): 
  							# 	print("Camera is unable to open.")
							#print("75")
							#frame_width = int(frame_raw.get(3))
							#print("80")
							#frame_height = int(frame_raw.get(4))
							
							# frame_width = int(cap.get(3))
							# frame_height = int(cap.get(4))
							
							print("100",datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))
							#video_output=cv2.VideoWriter('captured_video.avi',cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),20, (frame_width,frame_height))
							#video_output=cv2.VideoWriter('./ImageFiles/captured_video.avi',cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),20, tuple(conf["resolution"]))
							video_output=cv2.VideoWriter(videoFileName,cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),20, tuple(conf["resolution"]))
							print ("200"+datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))
							while ((1==1) and ((datetime.datetime.now()-captureStartTime).seconds < 3) ):
								frame_raw=vs.read() 
								video_output.write(frame_raw)
								#cv2.imshow('frame',frame_raw)  # this is too slow to come up on the RasberryPi/VNC								
								#else:
								#	break
								#cap.release()
							# video_output.release()
							print("Video capture stopped",datetime.datetime.now().strftime("%A %d %B %Y %I_%M_%S%p"))

							

	#### END AZURE
						
					except Exception as e:
						#print("[Errno {0}] {1}".format("e.errno", e.strerror))
						print("[Errno {0}] {1}".format("error", e))



				# update the last uploaded timestamp and reset the motion
				# counter
				#lastUploaded = timestamp
				#motionCounter = 0
#				t.cleanup()
				# check to see if dropbox sohuld be used
#				if conf["use_dropbox"]:
					# write the image to temporary file
#					t = TempImage()
#					cv2.imwrite(t.path, frame)

					# upload the image to Dropbox and cleanup the tempory image
#					print("[UPLOAD] {}".format(ts))
#					path = "/{base_path}/{timestamp}.jpg".format(
#					    base_path=conf["dropbox_base_path"], timestamp=ts)
#					client.files_upload(open(t.path, "rb").read(), path)
#					t.cleanup()

				# update the last uploaded timestamp and reset the motion
				# counter
#				lastUploaded = timestamp
#				motionCounter = 0

	# otherwise, the room is not occupied
	else:
		motionCounter = 0
####################################################################
	# check to see if the frames should be displayed to screen
	if conf["show_video"]:
		# display the security feed
		cv2.imshow("Cat-Cam", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key is pressed, break from the lop
		if key == ord("q"):
			break

	# clear the stream in preparation for the next frame
	#rawCapture.truncate(0)