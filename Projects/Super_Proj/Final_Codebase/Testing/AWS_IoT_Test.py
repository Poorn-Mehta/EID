# AWS Includes
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json

import threading

from datetime import datetime

from multiprocessing import Process, Value, Array

# AWS Variables
host = "a2p5kv6o0amgdr-ats.iot.us-east-2.amazonaws.com"
rootCAPath = "/home/pi/Downloads/AmazonRootCA1.pem"
certificatePath = "/home/pi/Downloads/14aced04de-certificate.pem.crt"
privateKeyPath = "/home/pi/Downloads/14aced04de-private.pem.key"
port = 8883
clientId = "EID_Proj_3"
topic = "EID/Project_3"
topic2 = "EID/Auth"

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

def AWS_Sub_Callback(client, userdata, message):
    print("AWS Received")
    print(message.payload)
    Rx = json.loads(message.payload)
    RID = int(Rx['Auth'])
    if(RID != 0):
        print("!!!AUTH!!!")
    else:
        print("!!!NO AUTH!!!")

# TODO - Add Comments
def AWS_Func(Shared_Flag, Shared_Arr):
    
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
    
    myAWSIoTMQTTClient.subscribe(topic2, 1, AWS_Sub_Callback)
    
    while 1:
        
        if(Shared_Flag.value == 1):
            
            print("Shared Flag is 1 - read by AWS")

            Shared_Flag.value = 0

            AWS_Msg = {}
    
            if(Shared_Arr[0] == 1):
                AWS_Msg['Type'] = AWS_CLR_Type_Str
                AWS_Msg['Node'] = Shared_Arr[1]
    
            elif(Shared_Arr[0] == 1):
                AWS_Msg['Type'] = AWS_ALT_Type_Str
                AWS_Msg['Node'] = Shared_Arr[1]
    
            elif(Shared_Arr[0] == 2):
                AWS_Msg['Type'] = AWS_LOW_Type_Str
                AWS_Msg['Node'] = Shared_Arr[1]
    
            elif(Shared_Arr[0] == 3):
                AWS_Msg['Type'] = AWS_WEB_Type_Str
                # Mon
                AWS_Msg['MONST'] =  f'{Shared_Arr[1]:02}' + ":" + f'{Shared_Arr[2]:02}'
                AWS_Msg['MONET'] =  f'{Shared_Arr[3]:02}' + ":" + f'{Shared_Arr[4]:02}'
                # Tue
                AWS_Msg['TUEST'] =  f'{Shared_Arr[5]:02}' + ":" + f'{Shared_Arr[6]:02}'
                AWS_Msg['TUEET'] =  f'{Shared_Arr[7]:02}' + ":" + f'{Shared_Arr[8]:02}'
                # Wed
                AWS_Msg['WEDST'] =  f'{Shared_Arr[9]:02}' + ":" + f'{Shared_Arr[10]:02}'
                AWS_Msg['WEDET'] =  f'{Shared_Arr[11]:02}' + ":" + f'{Shared_Arr[12]:02}'
                # Thu
                AWS_Msg['THUST'] =  f'{Shared_Arr[13]:02}' + ":" + f'{Shared_Arr[14]:02}'
                AWS_Msg['THUET'] =  f'{Shared_Arr[15]:02}' + ":" + f'{Shared_Arr[16]:02}'
                # Fri
                AWS_Msg['FRIST'] =  f'{Shared_Arr[17]:02}' + ":" + f'{Shared_Arr[18]:02}'
                AWS_Msg['FRIET'] =  f'{Shared_Arr[19]:02}' + ":" + f'{Shared_Arr[20]:02}'
                # Sat
                AWS_Msg['SATST'] =  f'{Shared_Arr[21]:02}' + ":" + f'{Shared_Arr[22]:02}'
                AWS_Msg['SATET'] =  f'{Shared_Arr[23]:02}' + ":" + f'{Shared_Arr[24]:02}'
                # Sun
                AWS_Msg['SUNST'] =  f'{Shared_Arr[25]:02}' + ":" + f'{Shared_Arr[26]:02}'
                AWS_Msg['SUNET'] =  f'{Shared_Arr[27]:02}' + ":" + f'{Shared_Arr[28]:02}'
            else:
                AWS_Msg['Type'] = "ERR"
            
            AWS_Msg['Timestamp'] = str(datetime.now().time())
                
            AWS_Msg['Msg_ID'] = AWS_Msg_ID
            AWS_Msg_ID += 1
                
            # Convert to JSON
            AWS_JSON_Obj = json.dumps(AWS_Msg)
            
            # Publish to MQTT Topic
            myAWSIoTMQTTClient.publish(topic, AWS_JSON_Obj, AWS_QoS)
            
            #time.sleep(Waiting_Time)
            
            # For debugging
            print("AWS Sent: %s" % AWS_JSON_Obj)

def Test_Func(Shared_Flag, Shared_Arr):
    
    while 1:
        
        if(Shared_Flag.value == 0):
            
            print("Shared Flag is 0 - read by Test")
            
            # Type
            Shared_Arr[0] = 3
            # Mon
            Shared_Arr[1] = 9
            Shared_Arr[2] = 0
            Shared_Arr[3] = 17
            Shared_Arr[4] = 0
            # Tue
            Shared_Arr[5] = 10
            Shared_Arr[6] = 0
            Shared_Arr[7] = 18
            Shared_Arr[8] = 0
            # Wed
            Shared_Arr[9] = 8
            Shared_Arr[10] = 0
            Shared_Arr[11] = 16
            Shared_Arr[12] = 0
            # Thu
            Shared_Arr[13] = 11
            Shared_Arr[14] = 0
            Shared_Arr[15] = 19
            Shared_Arr[16] = 0
            # Fri
            Shared_Arr[17] = 7
            Shared_Arr[18] = 0
            Shared_Arr[19] = 15
            Shared_Arr[20] = 0
            # Sat
            Shared_Arr[21] = 12
            Shared_Arr[22] = 0
            Shared_Arr[23] = 12
            Shared_Arr[24] = 0
            # Sun
            Shared_Arr[25] = 12
            Shared_Arr[26] = 0
            Shared_Arr[27] = 12
            Shared_Arr[28] = 0
            
            Shared_Flag.value = 1
        
        time.sleep(12)

def f(n, a):
    n.value = 3.1415927
    for i in range(len(a)):
        a[i] = -a[i]

if __name__ == '__main__':
    
    num = Value('d', 0)
    arr = Array('i', 30)

    p1 = Process(target=AWS_Func, args=(num, arr))
    p2 = Process(target=Test_Func, args=(num, arr))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()