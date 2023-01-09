# info from: https://www.section.io/engineering-education/how-to-control-a-servo-motor-using-a-raspberry-pi-3
import RPi.GPIO as GPIO
import time
from time import sleep


def servoTest():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11,GPIO.OUT)
    servo = GPIO.PWM(11,50)
    servo.start(0)
    print ("Waiting for 1 second")
    time.sleep(1)


    print ("Rotating at intervals of 12 degrees")
    duty = 2
    while duty <= 17:
        print("  ",duty)
        servo.ChangeDutyCycle(duty)
        time.sleep(1)
        duty = duty + 1

    print ("Turning back to 0 degrees")
    servo.ChangeDutyCycle(2)
    time.sleep(1)
    servo.ChangeDutyCycle(0)


    servo.stop()
    GPIO.cleanup()
    print ("Everything's cleaned up")

def GPIOTest():
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
GPIOTest()
print("done")