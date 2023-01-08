# import the necessary packages
import uuid
import os
import datetime

class TempImage:
	def __init__(self, basePath="./ImageFiles", ext=".jpg"):
		# construct the file path
		filenameDateFormatString="%Y_%m_%d_%H_%M_%S"
		timeStr=datetime.datetime.now().strftime(filenameDateFormatString)
		#self.path = "{base_path}/{rand}{ext}".format(base_path=basePath,
		#	rand=str(uuid.uuid4()), ext=ext)
		self.path = "{base_path}/{rand}{ext}".format(base_path=basePath,
			rand=timeStr, ext=ext)
            
	def cleanup(self):
		# remove the file
		os.remove(self.path)