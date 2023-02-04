# info from: https://www.section.io/engineering-education/how-to-control-a-servo-motor-using-a-raspberry-pi-3
import RPi.GPIO as GPIO
import time
from time import sleep


def servoTest():    
    servoPin=11
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servoPin,GPIO.OUT)
    servo = GPIO.PWM(servoPin,50)
    servo.start(0)
    time.sleep(0.5)
    #DutyCycle of 7 is 90 degrees
    #  2 is 0 degrees
    # 11.5 is 180 degrees
    #  1.5  = MIN - slightly less than 0
    # 12.3 = MAX (slightly more than 180 degrees)

  
    print ("Rotating")
    duty = 2
    while duty <= 12:
        print("  ",duty)
        servo.ChangeDutyCycle(duty)
        time.sleep(0.5)
        #servo.ChangeDutyCycle(0)
        #time.sleep(.5)
        duty = duty + 1
        

    print ("Turning back to 0 degrees")
    servo.ChangeDutyCycle(2)
    time.sleep(0.5)
    

    servo.stop()
    GPIO.cleanup()
    print ("Everything's cleaned up")

def GPIOTest():
    #This blinks LEDs when attached to these ports - just to verify the ports are working
    #Both these GPIO ports (9 & 11)are able to drive an LED on 1/8 7:20pm - so tested OK
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(11,GPIO.OUT,initial=0)
    GPIO.setup(9,GPIO.OUT,initial=0)
    sleep(0.5)
    blinks=0
    onTime=.01
    offTime=.05
    while (blinks<50):
        print("blinks")
        GPIO.output(11,1)
        GPIO.output(9,1)
        sleep(onTime)
        GPIO.output(11,0)
        GPIO.output(9,0)
        sleep(offTime) 
        blinks+=1

print ("started")
#GPIOTest()
servoTest()
print("done")