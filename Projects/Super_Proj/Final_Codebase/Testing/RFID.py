import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
from datetime import datetime

import numpy

reader = SimpleMFRC522()

Incoming_Str = "AWSMON09:3017:30TUE10:1518:15WED08:4516:45THU11:3019:30FRI07:1515:15SAT12:0012:00SUN12:0012:00"

#Shared_Arr = arr.array('d', 100)
Shared_Arr = numpy.zeros(100) 

try:
    val = 5
    lalala = "F" + f'{val:04}'
    print(datetime.now())
    print(lalala)
    
    if((Incoming_Str[3:6] != "MON") or (Incoming_Str[16:19] != "TUE") or (Incoming_Str[29:32] != "WED") or (Incoming_Str[42:45] != "THU")
       or (Incoming_Str[55:58] != "FRI") or (Incoming_Str[68:71] != "SAT") or (Incoming_Str[81:84] != "SUN")):
        print("Error in AWS Rx String")
        
#    if((Incoming_Str[3:6] != "MON") or (Incoming_Str[16:19] != "TUE") or (Incoming_Str[26:29] != "WED")):
#        print("Error in AWS Rx String")
        
    else:
        print("Valid AWS Rx String")
        
        Shared_Arr[0] = 4
        # Mon
        Shared_Arr[1] = int(Incoming_Str[6:8])
        Shared_Arr[2] = int(Incoming_Str[9:11])
        Shared_Arr[3] = int(Incoming_Str[11:13])
        Shared_Arr[4] = int(Incoming_Str[14:16])
        # Tue
        Shared_Arr[5] = int(Incoming_Str[19:21])
        Shared_Arr[6] = int(Incoming_Str[22:24])
        Shared_Arr[7] = int(Incoming_Str[24:26])
        Shared_Arr[8] = int(Incoming_Str[27:29])
        # Wed
        Shared_Arr[9] = int(Incoming_Str[32:34])
        Shared_Arr[10] = int(Incoming_Str[35:37])
        Shared_Arr[11] = int(Incoming_Str[37:39])
        Shared_Arr[12] = int(Incoming_Str[40:42])
        # Thu
        Shared_Arr[13] = int(Incoming_Str[45:47])
        Shared_Arr[14] = int(Incoming_Str[48:50])
        Shared_Arr[15] = int(Incoming_Str[50:52])
        Shared_Arr[16] = int(Incoming_Str[53:55])
        # Fri
        Shared_Arr[17] = int(Incoming_Str[58:60])
        Shared_Arr[18] = int(Incoming_Str[61:63])
        Shared_Arr[19] = int(Incoming_Str[63:65])
        Shared_Arr[20] = int(Incoming_Str[66:68])
        # Sat
        Shared_Arr[21] = int(Incoming_Str[71:73])
        Shared_Arr[22] = int(Incoming_Str[74:76])
        Shared_Arr[23] = int(Incoming_Str[76:78])
        Shared_Arr[24] = int(Incoming_Str[79:81])
        # Sun
        Shared_Arr[25] = int(Incoming_Str[84:86])
        Shared_Arr[26] = int(Incoming_Str[87:89])
        Shared_Arr[27] = int(Incoming_Str[89:91])
        Shared_Arr[28] = int(Incoming_Str[92:94])
        
        for i in range(len(Shared_Arr)):
            print(Shared_Arr[i])
    
    id, text = reader.read()
    print(id)
    print(text)
    time.sleep(2)
        
finally:
    GPIO.cleanup()