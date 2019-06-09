#import Libraries
import RPi.GPIO as GPIO
import time
import pyrebase

#Firebase Configuration
config = {
  "apiKey": "apiKey",
  "authDomain": "door-lock-2e39e.firebaseapp.com",
  "databaseURL": "https://door-lock-2e39e.firebaseio.com",
  "storageBucket": "door-lock-2e39e.appspot.com"
}

firebase = pyrebase.initialize_app(config)

#GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18, GPIO.OUT)

#Firebase Database Intialization
db = firebase.database()

#While loop to run until user kills program
while(True):
    #Get value of LED 
    led = db.child("led").get()

    #Sort through children of LED(we only have one)
    for user in led.each():
        #Check value of child(which is 'state')
        if(user.val() == "ON"):
            #If value is on, turn dont apply power to door strike (locked)
            GPIO.output(18, False)
        else:
            #If value is off, apply current to door strike (unlocked)
            GPIO.output(18, True)

        #0.1 Second Delay
        time.sleep(0.1)   

