# info from: https://www.section.io/engineering-education/how-to-control-a-servo-motor-using-a-raspberry-pi-3
import RPi.GPIO as GPIO
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
        self.positionStart=11.5
        self.positionEnd=2
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(servoPin,GPIO.OUT)
        #thisServo = GPIO.PWM(self.servoPin,50)
        self.thisServo = GPIO.PWM(servoPin,50)
        self.thisServo.start(0)
        self.thisServo.ChangeDutyCycle(self.positionStart)
        time.sleep(0.5)
        self.thisServo.ChangeDutyCycle(0)

            
    def cleanup(self):
        # remove the file
        self.thisServo.stop()
        GPIO.cleanup()

    def trigger(self):
        print("[INFO] Servo Triggered")
        self.thisServo.ChangeDutyCycle(self.positionEnd)
        time.sleep(0.5)
        self.thisServo.ChangeDutyCycle(self.positionStart)
        time.sleep(0.5)
        self.thisServo.ChangeDutyCycle(0)
