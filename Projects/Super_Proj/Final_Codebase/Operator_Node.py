# AWS Includes
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json

from mfrc522 import SimpleMFRC522

from datetime import datetime

import RPi.GPIO as GPIO

# AWS Variables
host = "a2p5kv6o0amgdr-ats.iot.us-east-2.amazonaws.com"
rootCAPath = "/home/pi/Downloads/AmazonRootCA1.pem"
certificatePath = "/home/pi/Downloads/14aced04de-certificate.pem.crt"
privateKeyPath = "/home/pi/Downloads/14aced04de-private.pem.key"
port = 8883
clientId = "EID_Proj_3"
topic = "EID/Project_3"
topic2 = "EID/Auth"

Poorn_Tag = "308375609162"
Poorn_ID = 1
Rushi_Tag = "1064179238322"
Rushi_ID = 2

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

buzzer=7

GPIO.setup(buzzer,GPIO.OUT)

# Configure AWS logging
#logger = logging.getLogger("AWSIoTPythonSDK.core")
#streamHandler = logging.StreamHandler()
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None

# AWSIoTMQTTClient connection configuration
AWS_Base_Quiet_Time = 1
AWS_Max_Quiet_Time = 32
AWS_Stable_Conn_Time = 20

# AWS MQTT QoS
AWS_QoS = 1

# AWS Message Types
AWS_CLR_Type_Str = "CLR"
AWS_ALT_Type_Str = "ALT"
AWS_LOW_Type_Str = "LOW"
AWS_WEB_Type_Str = "AWS"

# AWS Message ID/Seq No
AWS_Msg_ID = 1

# To Indicate if tehre is a new message available
AWS_New_Msg = 0

# Shared string for AWS IoT Publishing
AWS_AWS_Incoming_Str = ""

RFID_Scanner_Polling_Timeout = 2

def AWS_Sub_Callback(client, userdata, message):
    print("AWS Received")
    print(message.payload)
    Rx = json.loads(message.payload)
    Rx_Str = Rx['Type']
    if(Rx_Str == "ALT"):
        print(">>>>>>>>>>>HIGH ALERT DETECTED<<<<<<<<<<<<<")
        GPIO.output(buzzer,GPIO.HIGH)
        time.sleep(10)
        print("ALERT CLEARED")
        GPIO.output(buzzer,GPIO.LOW)
    else:
        print("Got %s"%Rx_Str)

def RFID_Func():
    
    global Poorn_Tag, Poorn_ID, Rushi_Tag, Rushi_ID
    
    # Setup RFID Reader
    RFID_Reader = SimpleMFRC522()
    
    print("RFID Setup Done")
    
    while 1:
    
        print("RFID Block")
        # Blocking read function - wait for any tag to be present at the RFID reader
        RFID_tag, RFID_text = RFID_Reader.read()
        print("RFID out of Block")
        
        # Check if the RFID Tag number and text matches that of hardcoded values
        if(str(RFID_tag) == Poorn_Tag):
            
            RFID_User_Present = 1
            RFID_User_ID = Poorn_ID
            print("Poorn's Tag Identified")
        
        elif(str(RFID_tag) == Rushi_Tag):
            
            RFID_User_Present = 1
            RFID_User_ID = Rushi_ID
            print("Rushi's Tag Identified")
            
        else:
            RFID_User_Present = 0
            print("Tag: %s"%RFID_tag)
        
        if(RFID_User_Present == 1):
            
            AWS_Msg = {}
            
            AWS_Msg['Auth'] = 1
            
            AWS_Msg['Timestamp'] = str(datetime.now().time())
                
            AWS_Msg['Msg_ID'] = AWS_Msg_ID
            AWS_Msg_ID += 1
                
            # Convert to JSON
            AWS_JSON_Obj = json.dumps(AWS_Msg)
            
            # Publish to MQTT Topic
            myAWSIoTMQTTClient.publish(topic2, AWS_JSON_Obj, AWS_QoS)
            
            #time.sleep(Waiting_Time)
            
            # For debugging
            print("AWS Sent: %s" % AWS_JSON_Obj)
        
        time.sleep(RFID_Scanner_Polling_Timeout)

# TODO - Add Comments
def AWS_Func():
    
    global host, rootCAPath, certificatePath, privateKeyPath, port, clientId, topic
    global logger, streamHandler, formatter, myAWSIoTMQTTClient, AWS_QoS
    global AWS_Base_Quiet_Time, AWS_Max_Quiet_Time, AWS_Stable_Conn_Time
    global AWS_New_Msg, Waiting_Time
    global AWS_QoS, AWS_Msg_ID
    
#    logger.setLevel(logging.DEBUG)
#    streamHandler.setFormatter(formatter)
#    logger.addHandler(streamHandler)
    
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
    
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(AWS_Base_Quiet_Time, AWS_Max_Quiet_Time, AWS_Stable_Conn_Time)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect to AWS IoT
    myAWSIoTMQTTClient.connect()
    
#    myAWSIoTMQTTClient.subscribe(topic, 1, AWS_Sub_Callback)


if __name__ == '__main__':
    
    AWS_Func()
    
    RFID_Func()
    
    
