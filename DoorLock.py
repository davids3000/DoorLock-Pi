#!/usr/bin/python3

#import Libraries
import RPi.GPIO as GPIO
import time
import pyrebase
import datetime
from os import path
from qhue import Bridge
from qhue import create_new_username

bridge = None

def main():
    
    BRIDGE_IP = "10.220.45.137"
    #USERNAME = "001788fffe74dfc3"      #This is not the username.  See documentation under "Creating a user"

    atHome = False
    
    #GPIO Setup
    GPIO.setmode(GPIO.BCM)
    #GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(27, GPIO.OUT)                                    # Door Strike
    GPIO.setup(23, GPIO.OUT)                                    # Status Door Strike
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)         # Reed Switch

    #Firebase Configuration
    config = {
      #"apiKey": "apiKey",
      "apiKey": "AlzaSyBTsS_7A0ozpYbKhUCKAF_f8_1Jjai2Hsl",
      "authDomain": "door-lock-2e39e.firebaseapp.com",
      "databaseURL": "https://door-lock-2e39e.firebaseio.com",
      "storageBucket": "door-lock-2e39e.appspot.com"
    }

    # Initialize pyrebase
    firebase = pyrebase.initialize_app(config)
    
    #Firebase Database Intialization
    global database
    database = firebase.database()

    #username = create_new_username(BRIDGE_IP)
    username = "V10aaqpebzbjw2l9RsWxfIg6qWBO6pIznm5cTvtJ"

    # Bridge instance
    global hueBridge
    hueBridge = Bridge(BRIDGE_IP, username)

    #output(17, False)
    print(GPIO.VERSION)

    print("username ")
    print(username)

    print(hueBridge.url)
    groups = hueBridge.groups
    
    roomGroup = hueBridge.groups[1]

    print("Lights are : ")
    print(lights_checkCurrentState(roomGroup))
    print("Reed switch is : ")
    print(reed_checkCurrentState())
    #print(groups.url)
    #print(groups())
    #print(groups[1].action(on=True))


    #b.lights[1].state(bri=128, hue=900)

    scenes = hueBridge.scenes
    #print(scenes.url)
    #print(scenes())

    #GPIO.add_event_detect(17, GPIO.FALLING)

    #GPIO.add_event_detect(17, GPIO.FALLING, callback=reedclose_callback)
    GPIO.add_event_detect(17, GPIO.BOTH, callback=reed_callback, bouncetime=1000)

    #While loop to run until user kills program
    while(True):
        
        #Get value of LED 
        led = database.child("led").get()

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


# Reed switch interrupt routine
def reed_callback(channel):
    reed_toggleLights(lights_getCurrentGroup(), getCurrentDatabase())
    
def getCurrentDatabase():
    return database
    
# Check if lights are on/off
def lights_checkCurrentState(group):
    if((group()['action']['on']) == True):
        return True
    elif ((group()['action']['on']) == False):
        return False

def lights_getCurrentGroup():
    return hueBridge.groups[1]

# Check current state of reed switch
def reed_checkCurrentState():
    if GPIO.input(17):
        return True
    else:
        return False
    
# Toggle light state with respect to reed state
def reed_toggleLights(lightGroup, fireDatabase):
    
    # Reed switch closed
    if GPIO.input(17):
        
        # Turn off lights
        lightGroup.action(on=False)
        
        # Timestamp
        timeClosed = datetime.datetime.now().strftime("%A %B %m %I %M %S %p")
        fireDatabase.child("Reed").child("Time").update({"Last Closed": timeClosed})
    # Reed switch opened
    else:
        
        # Turn on lights
        lightGroup.action(on=True)
        
        # Timestamp
        timeOpened = datetime.datetime.now().strftime("%A %B %m %I %M %S %p")
        fireDatabase.child("Reed").child("Time").update({"Last Opened": timeOpened})


if __name__== "__main__":
    main()