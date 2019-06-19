#!/usr/bin/python3

#import Libraries
import RPi.GPIO as GPIO
import time
import pyrebase
import datetime
from os import path
from qhue import Bridge
from qhue import create_new_username


BRIDGE_IP = "10.220.45.137"
#USERNAME = "001788fffe74dfc3"      #This is not the username.  See documentation under "Creating a user"

atHome = False


#Firebase Configuration
config = {
  #"apiKey": "apiKey",
  "apiKey": "AlzaSyBTsS_7A0ozpYbKhUCKAF_f8_1Jjai2Hsl",
  "authDomain": "door-lock-2e39e.firebaseapp.com",
  "databaseURL": "https://door-lock-2e39e.firebaseio.com",
  "storageBucket": "door-lock-2e39e.appspot.com"
}

firebase = pyrebase.initialize_app(config)

#username = create_new_username(BRIDGE_IP)
username = "V10aaqpebzbjw2l9RsWxfIg6qWBO6pIznm5cTvtJ"

b = Bridge(BRIDGE_IP, username)


#GPIO Setup
GPIO.setmode(GPIO.BCM)
#GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(27, GPIO.OUT)                                    # Door Strike
GPIO.setup(23, GPIO.OUT)                                    # Status Door Strike
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)           # Reed Switch


reedState = "Init"

def reed_callback(channel):
    print("Door %s at " )
    toggleLightState()


    
def reed_checkCurrentState():
    if GPIO.input(17):
        return "OPENED"
    else:
        return "Closed"   

#Firebase Database Intialization
db = firebase.database()

#.output(17, False)
print(GPIO.VERSION)

print("username ")
print(username)

print(b.url)
groups = b.groups
#print(groups.url)
#print(groups())
#print(groups[1].action(on=True))


# Invert group lights state
def toggleLightState():
    '''
    if(((groups[1]()['action']['on']) == True) and (atHome == False)):
        groups[1].action(on=False)
    elif ((groups[1]()['action']['on']) == False):
        groups[1].action(on=True)
    '''
    if GPIO.input(17):
        groups[1].action(on=False)
        timeClosed = datetime.datetime.now().strftime("%A %B %m %I %M %S %p")
        db.child("Reed").child("Time").update({"Last Closed": timeClosed})
    else:
        groups[1].action(on=True)
        timeOpened = datetime.datetime.now().strftime("%A %B %m %I %M %S %p")
        db.child("Reed").child("Time").update({"Last Opened": timeOpened})

#b.lights[1].state(bri=128, hue=900)

scenes = b.scenes
#print(scenes.url)
#print(scenes())


#GPIO.add_event_detect(17, GPIO.FALLING)

    
#GPIO.add_event_detect(17, GPIO.FALLING, callback=reedclose_callback)
GPIO.add_event_detect(17, GPIO.BOTH, callback=reed_callback, bouncetime=1000)



#While loop to run until user kills program
while(True):
    
    #Get value of LED 
    led = db.child("led").get()

    #Sort through children of LED(we only have one)
    for user in led.each():
        #Check value of child(which is 'state')
        if(user.val() == "ON"):
            #If value is on, turn dont apply power to door strike (locked)
            GPIO.output(27, False)
            GPIO.output(23, True)
            #print("Door is Locked")
 
        else:
            #If value is off, apply current to door strike (unlocked)
            GPIO.output(27, True)
            GPIO.output(23, False)
            #print("Door is unlocked")

        #0.1 Second Delay
        time.sleep(0.1)   