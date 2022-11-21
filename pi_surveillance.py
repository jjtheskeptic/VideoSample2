# import the necessary packages
from pyimagesearch.tempimage import TempImage
#from picamera.array import PiRGBArray
#from picamera import PiCamera.
from imutils.video import VideoStream #JJ
import argparse
import warnings
import datetime
import dropbox
import imutils
import json
import time
import cv2
# https://learn.microsoft.com/en-us/python/api/overview/azure/cognitiveservices-vision-computervision-readme?view=azure-python
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import http.client, urllib.request, urllib.parse, urllib.error, base64


# construct the argument parser and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-c", "--conf", required=True, help="path to the JSON configuration file")

#args = vars(ap.parse_args())

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


	
# ===============initialize the camera and grab a reference to the raw camera capture
#camera = PiCamera()
#camera.resolution = tuple(conf["resolution"])
#camera.framerate = conf["fps"]
#rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))
vs=VideoStream(src=1).start() 
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
	frame=vs.read() #frame = f.array
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
	print("[INFO] waiting for scene changes...")
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

			# check to see if the number of frames with consistent motion is
			# high enough
			if motionCounter >= conf["min_motion_frames"]:
				print("[INFO] - MOTION FOUND") # DO SOMETHING
                # write the image to temporary file
				t = TempImage()
				cv2.imwrite(t.path, frame)
#### AZURE ###
				# Read file
				with open(t.path, 'rb') as f:
					data = f.read()
				try:
					conn = http.client.HTTPSConnection('cattraps.cognitiveservices.azure.com')
					#conn.request("POST", "/computervision/imageanalysis:analyze?api-version=2022-10-12-preview&%s" % params, "{body}", headers)
					conn.request("POST", "/computervision/imageanalysis:analyze?api-version=2022-10-12-preview&%s" % params, data, headers)
					response = conn.getresponse()
					responseData = response.read()
					print(responseData)
					pythonObj=json.loads(responseData)
					print(pythonObj["tagsResult"])
					tags=pythonObj["tagsResult"]
					for object in tags["values"]:
						print(object["name"], object["confidence"])
					print("[INFO]:sleeping 5 seconds...")
					time.sleep(5)
					conn.close()
#### END AZURE
				except Exception as e:
					print("[Errno {0}] {1}".format(e.errno, e.strerror))



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
		cv2.imshow("Security Feed", frame)
		key = cv2.waitKey(1) & 0xFF

		# if the `q` key is pressed, break from the lop
		if key == ord("q"):
			break

	# clear the stream in preparation for the next frame
	#rawCapture.truncate(0)