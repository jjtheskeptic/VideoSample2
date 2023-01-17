# info from: https://www.section.io/engineering-education/how-to-control-a-servo-motor-using-a-raspberry-pi-3
import RPI.GPIO as GPIO
import time
from time import sleep
#DutyCycle values:     
#  0 is no instruction   
#  2 is 0 degrees
#  7 is 90 degrees
# 11.5 is 180 degrees
#  1.5  = MIN - slightly less than 0
# 12.3 = MAX (slightly more than 180 degrees)

class Servox:
    def __init__(self,servoPin):
        #servoPin=11
        positionStart=11.5
        positionEnd=2
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(servoPin,GPIO.OUT)
        thisServo = GPIO.PWM(self.servoPin,50)
        thisServo.start(0)
        thisServo.changeDutyCycle(positionStart)
        time.sleep(0.5)
        thisServo.changeDutyCycle(0)

            
    def cleanup(self):
        # remove the file
        self.thisServo.stop()
        GPIO.cleanup()

    def trigger(self):
        self.thisServo.changeDutyCycle(self.positionEnd)
        time.sleep(0.5)
        self.thisServo.changeDutyCycle(self.positionStart)
        time.sleep(0.5)
        self.thisServo.changeDutyCycle(0)
