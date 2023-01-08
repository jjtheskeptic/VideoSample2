# info from: https://www.section.io/engineering-education/how-to-control-a-servo-motor-using-a-raspberry-pi-3
import RPi.GPIO as GPIO
import time


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