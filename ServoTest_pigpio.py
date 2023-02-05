# info from: https://www.section.io/engineering-education/how-to-control-a-servo-motor-using-a-raspberry-pi-3
#import RPi.GPIO as GPIO
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo
import time
from time import sleep
#pigpio : http://abyz.me.uk/rpi/pigpio/download.html
#start at boot: https://www.instructables.com/Raspberry-Pi-Remote-GPIO/
# enable start at boot: sudo systemctl enable pigpiod
# start immediately:    sudo systemctl start pigpiod 
#disable start at boot: sudo systemctl disable pigpiod
# stop immediately:     sudo systemctl stop pigpiod
#Run it manually from terminal:
#    sudo pigpiod # start pigpio daemon
#
#    pigs s 18 1000 # counterclockwise
#    pigs s 18 1500 # centre
#    pigs s 18 2000 # clockwise#
#
#    pigs s 18 0 # switch servo pulses off

#kill: sudo killall pigpiod
#see if running: ps aux | grep pigpiod
#

factory=PiGPIOFactory(host='raspberrypi.local')

#servo = Servo(17,min_pulse_width=0.8/1000, max_pulse_width=2.2/1000,pin_factory=factory)
servo=Servo(17,pin_factory=factory)

servo.min()
sleep(2)
servo.max()
sleep(2)
servo.min()

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
    # 12 is vertical for the cat sprayer
    # 2 is fully extended


    print ("Rotating")
    duty = 2
    while duty <= 12:
        print("  ",duty)
        servo.ChangeDutyCycle(duty)
        time.sleep(1)
##        #servo.ChangeDutyCycle(0)
        time.sleep(.5)
        duty = duty + 1
        
    print("set to 8")
    servo.ChangeDutyCycle(12)
    time.sleep(2)
    print("set to 2")
    servo.ChangeDutyCycle(2)
    time.sleep(2)
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

#print ("started")
#GPIOTest()
#servoTest()
print("done")