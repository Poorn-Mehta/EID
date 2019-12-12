
def sendToArduino(td):
    numLoops = len(td)
    
    n = 0
    while n < numLoops:
        teststr = ord(td[n])
    
    ser.write(teststr) # change for Python3


#======================================

def recvFromArduino():
    global startMarker, endMarker
    
    ck = ""
    x = "z" # any value that is not an end- or startMarker
    byteCount = -1 # to allow for the fact that the last increment will be one too many
    
    # wait for the start character
    while  ord(x) != startMarker: 
        x = ser.read()
        time.sleep(1)
    
    # save data until the end marker is found
    while ord(x) != endMarker:
        if ord(x) != startMarker and ord(x) != 255:
            ck = ck + x.decode("utf-8") # change for Python3
            #ck = ck + chr(ord(x))
            byteCount += 1
        x = ser.read()
    
    return(ck)


#============================

def waitForArduino():

    # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded
    
    global startMarker, endMarker
    
    msg = ""
    while msg.find("Arduino is ready") == -1:

        while ser.inWaiting() == 0:
            pass
        
        msg = recvFromArduino()

        print (msg) # python3 requires parenthesis
        print ()
        
#======================================

def runTest(td):
    numLoops = len(td)
    waitingForReply = False

    n = 0
    while n < numLoops:
        teststr = td[n]

        if waitingForReply == False:
            sendToArduino(teststr)
            print ("Sent from PC -- LOOP NUM " + str(n) + " TEST STR " + teststr)
            waitingForReply = True

        if waitingForReply == True:

            while ser.inWaiting() == 0:
                pass
            
            dataRecvd = recvFromArduino()
            print ("Reply Received  " + dataRecvd)
            n += 1
            waitingForReply = False

            print ("===========")

        time.sleep(5)


#======================================

# THE DEMO PROGRAM STARTS HERE

#======================================

import serial
import time

print ()
print ()

# NOTE the user must ensure that the serial port and baudrate are correct
# serPort = "/dev/ttyS80"
serPort = "/dev/ttyS0"
baudRate = 9600
ser = serial.Serial(serPort, baudRate)
print ("Serial port " + serPort + " opened  Baudrate " + str(baudRate))


startMarker = 60
endMarker = 62

i = 0
temp_str = ""

while 1:
     #   global startMarker, endMarker, large_arr, byteCount
#    trystr = "<CLR00>"
#    for i in range (0, 5):
#        simple = trystr[i]
#        ser.write(simple.encode('utf-8'))
    gotthis = recvFromArduino()
    print ("Reply Received  " + gotthis)
    trystr = "NOUPD"
    for i in range (0, 5):
        simple = trystr[i]
        ser.write(simple.encode('utf-8'))
#    simple = '<'
#    ser.write(simple.encode('utf-8'))
#    simple = 2
#    ser.write(simple)
#    simple = 3
#    ser.write(simple)
        
    #temp_str = "<From RPi: " + str(i) + "\n>"
    #testData.append(temp_str)
    #testData = "<A>"
    #sendToArduino(testData)
    #while 1:
        #ser.write(simple)
        #time.sleep(1)
    i += 1
    if(i >= 10):
        i = 0

"""
waitForArduino()


testData = []
testData.append("<LED1,200,0.2>")
testData.append("<LED1,800,0.7>")
testData.append("<LED2,800,0.5>")
testData.append("<LED2,200,0.2>")
testData.append("<LED1,200,0.7>")

runTest(testData)


ser.close

"""