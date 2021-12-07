#! /usr/bin/python3
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, messaging
import boto3
import requests
import threading
import RPi.GPIO as GPIO

RECEIVE_PIN = 17
# Use RTL SDR and rtl_433 tool to capture the code (rtl_433 -A)
doorbellCode = "changeme"

# Function to setup GPIO
def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RECEIVE_PIN, GPIO.IN)

# Function to authenticate to firebase
def firebaseAuthenticate():
    # Authenticate
    cred = credentials.Certificate("google-credentials.json")

    # Initialize the app with a service account, granting admin privileges
    firebase_admin.initialize_app(cred)

# Send FCM nofitication
def sendFCMNotification(message):
    title = "Doorbell"
    message = messaging.Message(
        notification=messaging.Notification(title,message),
        topic="alerts",
    )
    
    response = messaging.send(message)

# Function for SMS alert
def sendSNSNotification(message):
    #sns = boto3.client('sns',
    #    aws_access_key_id='<AWS KEY ID>',
    #    aws_secret_access_key='<AWS SECRET KEY>',
    #    region_name="<AWS REGION>"
    #)

    # Make sure you have the profile in ~/.aws/credentials or use the above
    session = boto3.Session(profile_name='notifications')
    sns = session.client('sns')

    response = sns.publish(TopicArn='<ARN>',
        Message=message
    )


# Function to show message on SPHD
def sendSPHDNotification(message):
    headers = {"x-scrollbot-auth":"changeme"}
    URL = f"http://<scrollbotIP>:8080/scrollbot?message={message}"
    res = requests.get(URL,headers=headers)
    if res.text != "Success!":
        print("Error occured when calling scrollbot")


# Function to listen for RF signals and parse the timings
def listenRF():
    result = []
    parseTime = datetime.now()
    previous = 0
    print('*Started capturing RF signals*')
    # Basically this is a while loop which will note the time of how long a high signal is detected
    # Once it detects a low signal after the high signal it will calculate how long the high signal was and store that value
    # The timings are send to the parseData function (runs in different thread)
    while True:
        data = GPIO.input(RECEIVE_PIN)
        if data == 1 and previous == 0:
            previous = datetime.now()

        if data == 0 and previous != 0:
            result.append((datetime.now() - previous).microseconds)
            previous = 0

        # If 2 seconds of capturing are passed, then process the data
        #if (datetime.now() - parseTime).seconds >= 2:
        if len(result) >= 200:
            parseThread = threading.Thread(target=parseData,args=(result,))
            parseThread.start()
            parseTime = datetime.now()
            result = []

# Function which will convert data
def parseData(data):
    # Convert data timings 
    # Long 1 signal is 0 binary
    # Short 1 signal is 1 binary
    short_pulse = 328
    long_pulse = 636
    margin = 150
    binary = []
    for element in data:
        if element > (short_pulse - margin) and element < (short_pulse + margin):
            binary.append(1)
        elif element > (long_pulse - margin) and element < (long_pulse + margin):
            binary.append(0)
        else:
            binary.append("(" + str(element) + ")")

    binary = ''.join(str(element) for element in binary)

    # Check if doorbell data is present
    checkDoorbell(binary)

# Function which will check if doorbell data is found
def checkDoorbell(data):
    # Check if doorbell code was found:
    if doorbellCode in data:

        print("Ding dong @ " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(data)
        if datetime.now() > notificationTimeout:
            sendFCMNotification("Ding dong!")
            sendSNSNotification("DING DONG")
            sendSPHDNotification("BEL")
            notificationTimeout = datetime.now() + datetime.timedelta(seconds=30)



if __name__ == '__main__':

    # Firebase Authentication
    firebaseAuthenticate()

    # Setup devices
    setupGPIO()

    # Thread to start listening for RF signals
    print("Starting thread to listen for RF signals")    
    rfThread = threading.Thread(target=listenRF)
    rfThread.start()

    #print("Performing cleanup")    
    #GPIO.cleanup()
