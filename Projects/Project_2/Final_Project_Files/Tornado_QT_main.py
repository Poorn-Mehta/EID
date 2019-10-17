

# Importing Multiprocessing Library #
import multiprocessing

# Importing Libraries for Tornado #
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket

# Imported json to try and send JSON objects #
import json

# General Includes #
import array as arr
import sys, os, signal, time
import  numpy  as  np 
import  random
from datetime import datetime

# Include files for PyQT5 #
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication
from PyQt5.uic import loadUi

# Include for MySQL #
import MySQLdb

# Include for Matplotlib #
from  matplotlib.backends.backend_qt5agg  import(NavigationToolbar2QT  as  NavigationToolbar)

# Include for DHT22 #
import Adafruit_DHT as dht

# Threshold Globals (Temperature & Humidity)#
TH = 35
TL = 15
HH = 50
HL = 10

# Humidity and Temperature Variables #
Humidity_Data = 0.0
Temperature_Data = 0.0

# Configuration Variables #
Max_No_of_Readings = 50
Current_Reading = 1
Update_Period_sec = 5

# Timer #
Periodic_Timer = 0
sec_to_msec = 1000

# Constant Source Identifier Variable #
Periodic_Update_source = 0
Update_Button_source = 1

# Constant Alert Status Identifier Variable #
Alert_Asserted = 1
Alert_Cleared = 0

# Celsius/Fahrenheit Config #
Set_to_Celsius = 0
Set_to_Fahrenheit = 1
C_to_F = Set_to_Celsius

# Exit variable settings #
Exit_Set = 1
Exit_Clear = 0
Exit_Flag = Exit_Clear

# Arrays required for Graphs #
Temp_Arr = arr.array('f', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
Humi_Arr = arr.array('f', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

# Sensor Lock #
Sensor_Lock = multiprocessing.Lock()

# Tornado Variables required for Server Application #
Tornado_Data_Req_String = "DHT22_DATA_TSTAMP"
Tornado_Unit_Change_String = "FLIP_UNIT"
Tornado_Network_Test_String = "NET_TEST"
Tornado_First_Line = "<br/><b>Immediate Update via Tornado & Python</b>"
Tornado_Remote_Unit = Set_to_Celsius
Prev_Temperature = 0.0
Prev_Message = ""
Update_Failure = False
Tornado_PID = 0

# Class for Matplotlib Widget in pyqt #
class MatplotlibWidget(QMainWindow):
    
    def __init__(self):
        
        QMainWindow.__init__(self)
        
        global Periodic_Timer, Update_Period_sec, sec_to_msec

        # Load UI directly (pyqt) #
        loadUi("qt_designer.ui" , self)

        # Set the title of window #
        self.setWindowTitle("EID Project 1")
        
        # Disable text editing #
        self.Text_Main.setReadOnly(True)
        self.Text_C_F.setReadOnly(True)
        self.Text_DB.setReadOnly(True)
        
        # Write initial/default values #
        self.Text_C_F.textCursor().insertHtml('<font size="4"><b>C</b></font>')
        self.Text_DB.textCursor().insertHtml('<font size="3"><b>Database Information</b></font>')
        self.Temp_High.setPlainText(str(TH))
        self.Temp_Low.setPlainText(str(TL))
        self.Humi_High.setPlainText(str(HH))
        self.Humi_Low.setPlainText(str(HL))
        self.Config_Text.setPlainText("Update Period(s): %d \nMax Readings: %d" \
                                      %(Update_Period_sec, Max_No_of_Readings))
        
        # Setup timer #
        Periodic_Timer = QtCore.QTimer(self)
        Periodic_Timer.timeout.connect(Update_DB)
        Periodic_Timer.start(Update_Period_sec * sec_to_msec)

        # Setup button press actions #
        self.Updt_Reading.clicked.connect(Instant_Update) 
        self.Temp_Graph.clicked.connect(Temperature_Graph)
        self.Humi_Graph.clicked.connect(Humidity_Graph)
        self.Updt_Thr.clicked.connect(Update_Thresholds)
        self.C_F.clicked.connect(Change_Unit)
        self.Updt_Cfg.clicked.connect(Update_Config)

        # Add toolbar for graphs #
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas ,  self))   


# Class to return multiple values from a function #
class Thr_Return_Val:
    
  def __init__(self, TH_Flag, TL_Flag, HH_Flag, HL_Flag):
     self.TH_Flag = TH_Flag
     self.TL_Flag = TL_Flag
     self.HH_Flag = HH_Flag
     self.HL_Flag = HL_Flag

# Check if the latest readings are within user defined range or not #
def Check_Thresholds():
    
    global Humidity_Data, Temperature_Data, TH, TL, HH, HL
    
    # Reset all flags #
    TH_Flag = Alert_Cleared
    TL_Flag = Alert_Cleared
    HH_Flag = Alert_Cleared
    HL_Flag = Alert_Cleared
     
    # Test for each alert #
    if(Temperature_Data > float(TH)):
        TH_Flag = Alert_Asserted
        
    if(Temperature_Data < float(TL)):
        TL_Flag = Alert_Asserted
        
    if(Humidity_Data > float(HH)):
        HH_Flag = Alert_Asserted
        
    if(Humidity_Data < float(HL)):
        HL_Flag = Alert_Asserted   

    # Return required flags #
    return Thr_Return_Val(TH_Flag, TL_Flag, HH_Flag, HL_Flag)
    
# Function to update main text display widget #
def Update_Main_Display(source):
    
    global Humidity_Data, Temperature_Data, Periodic_Update_source, Update_Button_source
    global C_to_F, Set_to_Celsius, Set_to_Fahrenheit
    
#    Clear the display first 
    PyQtInterface.Text_Main.clear()
    
#    Look at the source (passed as function argument), and print text message accordingly 
    if(source == Periodic_Update_source):
        PyQtInterface.Text_Main.textCursor().insertHtml('Periodic Update')
        
    elif(source == Update_Button_source):
        PyQtInterface.Text_Main.textCursor().insertHtml('Immediate Update')
        
    else:
        PyQtInterface.Text_Main.textCursor().insertHtml('Unknown Update(???)')
    
#    Check whether the latest sensor read succeeded or not
    if((Humidity_Data != None) and (Temperature_Data != None)):
        
#        Check whether the required unit is Celsius or Fahrenheit, and print temperature accordingly
        if(C_to_F == Set_to_Celsius):
            PyQtInterface.Text_Main.textCursor().insertHtml('<br/>Temperature: <b>%.1f*C</b>'%Temperature_Data)
            
        elif(C_to_F == Set_to_Fahrenheit):
            Temperature_Data = (Temperature_Data * 1.8) + 32
            PyQtInterface.Text_Main.textCursor().insertHtml('<br/>Temperature: <b>%.1f*F</b>'%Temperature_Data)
            
        else:
            PyQtInterface.Text_Main.textCursor().insertHtml('<br/><b>INVALID C_to_F Passed</b>')
            
#        Print humidity and timestamp
        PyQtInterface.Text_Main.textCursor().insertHtml('<br/>Humidity: <b>%.1f%%</b>'%Humidity_Data)
        PyQtInterface.Text_Main.textCursor().insertHtml('<br/>Updated On: <b>%s</b>'%datetime.now().time())
        
#       Call threshold checking function
        Thr_Res = Check_Thresholds()
        
#        Use data from threshold tester and print messages if necessary
        if((Thr_Res.TH_Flag == Alert_Asserted) or \
           (Thr_Res.TL_Flag == Alert_Asserted) or \
           (Thr_Res.HH_Flag == Alert_Asserted) or \
           (Thr_Res.HL_Flag == Alert_Asserted)):
            
            PyQtInterface.Text_Main.textCursor().insertHtml('<br/><b>!!!***ALERT***!!!</b>')
            
            if(Thr_Res.TH_Flag == Alert_Asserted):
                PyQtInterface.Text_Main.textCursor().insertHtml('<br/><b>Temperature Too High</b>')
                
            if(Thr_Res.TL_Flag == Alert_Asserted):
                PyQtInterface.Text_Main.textCursor().insertHtml('<br/><b>Temperature Too Low</b>')
                
            if(Thr_Res.HH_Flag == Alert_Asserted):
                PyQtInterface.Text_Main.textCursor().insertHtml('<br/><b>Humidity Too High</b>')
                
            if(Thr_Res.HL_Flag == Alert_Asserted):
                PyQtInterface.Text_Main.textCursor().insertHtml('<br/><b>Humidity Too Low</b>') 

#    Print error message if sensor reading failed
    else:
        PyQtInterface.Text_Main.textCursor().insertHtml('<br/><b>ERROR with SENSOR</b>')
        PyQtInterface.Text_Main.textCursor().insertHtml('<br/><b>GOT BAD RESPONSE</b>')           
        
# Function to poll the sensor and update data #
def Poll_Sensor():
    
    global Humidity_Data, Temperature_Data
    Sensor_Lock.acquire()
    Humidity_Data, Temperature_Data = dht.read(dht.DHT22, 23)
    Sensor_Lock.release()

# Callback function for instantaneous data update #
def Instant_Update():
    
    global Update_Button_source
    
    # Query the sensor and then update display #
    Poll_Sensor()
    Update_Main_Display(Update_Button_source)

# Callback function for periodic data update and storage #
def Update_DB():
    
    global Periodic_Update_source, Humidity_Data, Temperature_Data, Current_Reading
    global Max_No_of_Readings, Exit_Flag, Update_Period_sec

    if(Exit_Flag == Exit_Clear):

        # Poll the sensor first #
        Poll_Sensor()
        
        # Update the MySQL database only if reading hasn't failed, otherwise print the error message #
        if((Humidity_Data == None) or (Temperature_Data == None)):
            PyQtInterface.Text_DB.clear()
            PyQtInterface.Text_DB.textCursor().insertHtml('<font size="4"><b>Error While Reading Sensor</b></font>')
            
        else:
            PyQtInterface.Text_DB.clear()
            PyQtInterface.Text_DB.textCursor().insertHtml('<font size="3"><b>Reading %d Added to Database</b></font>'%Current_Reading)
            Current_Reading += 1
            cursor.execute("""INSERT INTO DHT22_Table (Temperature, Humidity) VALUES (%s,%s)""",(Temperature_Data,Humidity_Data))

        Update_Main_Display(Periodic_Update_source)

        # If all of the readings are stored - then stop the timer, and exit the event loop of PyQt #
        if(Current_Reading > Max_No_of_Readings):
            Exit_Flag = Exit_Set
            print("Program will Close in %d Seconds" % Update_Period_sec)
            PyQtInterface.Text_Main.textCursor().insertHtml('<br/><b>Program will Close in %d Seconds</b>'%Update_Period_sec) 
            
    else:
            
            Periodic_Timer.stop()
            QCoreApplication.quit()

# Function to update thresholds (temperature and humidity) #
def Update_Thresholds():
    
    global TH, TL, HH, HL

    # Read thresholds from editable textboxes, and update the global variables accordingly #
    TH = int(PyQtInterface.Temp_High.toPlainText())
    TL = int(PyQtInterface.Temp_Low.toPlainText())
    HH = int(PyQtInterface.Humi_High.toPlainText())
    HL = int(PyQtInterface.Humi_Low.toPlainText())
    
    # Update the textboxes as well #
    PyQtInterface.Temp_High.setPlainText(str(TH))
    PyQtInterface.Temp_Low.setPlainText(str(TL))
    PyQtInterface.Humi_High.setPlainText(str(HH))
    PyQtInterface.Humi_Low.setPlainText(str(HL))

# Function to change unit of temperature (between Celsius and Fahrenheit) #
def Change_Unit():
    
    global C_to_F, Set_to_Celsius, TH, TL
    
    # Check the previous setting, and choose the other one. Update global variables #
    if(C_to_F == Set_to_Celsius):
        PyQtInterface.Text_C_F.clear()
        PyQtInterface.Text_C_F.textCursor().insertHtml('<font size="4"><b>F</b></font>')
        C_to_F = 1
        TH = int((TH * 1.8) + 32)
        TL = int((TL * 1.8) + 32)
        
    else:
        PyQtInterface.Text_C_F.clear()
        PyQtInterface.Text_C_F.textCursor().insertHtml('<font size="4"><b>C</b></font>')
        C_to_F = 0
        TH = int(((TH - 32) * 5) / 9)
        TL = int(((TL - 32) * 5) / 9)
        
    # Print the new values #
    PyQtInterface.Temp_High.setPlainText(str(TH))
    PyQtInterface.Temp_Low.setPlainText(str(TL)) 

# Function to draw temperature graph #
def Temperature_Graph():
    
    global Temp_Arr, C_to_F, Set_to_Fahrenheit
    
    # Select most recent 10 Entries #
    cursor.execute("""SELECT * FROM (SELECT * FROM DHT22_Table ORDER BY Readings DESC LIMIT 10) sub ORDER BY Readings ASC""")
    
    # Move through those rows, and pick out the temperature #
    y = 0
    for x in cursor.fetchall():
        Temp_Arr[y] = float(x[1])
        if(C_to_F == Set_to_Fahrenheit):
            Temp_Arr[y] = (Temp_Arr[y] * 1.8) + 32
        y += 1
    
    # Print the data for easy debugging #
    print("Plotting Following Temperature Data")
    
    for x in range(0, 10):
        print("Temp Arr: %f" % Temp_Arr[x])

    # Plot using Matplotlib Widget #
    PyQtInterface.MplWidget.canvas.axes.clear() 
    PyQtInterface.MplWidget.canvas.axes.plot(Temp_Arr)
    PyQtInterface.MplWidget.canvas.axes.legend('Temp in C',loc = 'upper right')
    if(C_to_F == Set_to_Fahrenheit):
        PyQtInterface.MplWidget.canvas.axes.set_title('Temperature Graph (*F)')
    else:
        PyQtInterface.MplWidget.canvas.axes.set_title('Temperature Graph (*C)')
    PyQtInterface.MplWidget.canvas.draw()

# Function to draw humidity graph #
def Humidity_Graph():
    
    global Humi_Arr

    # Select most recent 10 Entries #
    cursor.execute("""SELECT * FROM (SELECT * FROM DHT22_Table ORDER BY Readings DESC LIMIT 10) sub ORDER BY Readings ASC""")
    
    # Move through those rows, and pick out the humidity #
    y = 0
    for x in cursor.fetchall():
        Humi_Arr[y] = float(x[2])
        y += 1
    
    # Print the data for easy debugging #
    print("Plotting Following Humidity Data")
    
    for x in range(0, 10):
        print("Humi Arr: %f" % Humi_Arr[x])

    # Plot using Matplotlib Widget #
    PyQtInterface.MplWidget.canvas.axes.clear() 
    PyQtInterface.MplWidget.canvas.axes.plot(Humi_Arr)
    PyQtInterface.MplWidget.canvas.axes.legend('Relative Humidity',loc = 'upper right')
    PyQtInterface.MplWidget.canvas.axes.set_title('Humidity Graph')
    PyQtInterface.MplWidget.canvas.draw()

# Function to update basic configuration settings #
def Update_Config():
    
    global Update_Period_sec, Max_No_of_Readings

    # Setup local variables and get the whole string from the editable textbox #
    local_s = 0
    local_count = 0
    local_str = PyQtInterface.Config_Text.toPlainText()
    
    # Pick out integers from the string and apply to appropriate global variables #
    for local_s in local_str.split():
        
        if local_s.isdigit():
            
            if(local_count == 0):
                Update_Period_sec = int(local_s)
                Periodic_Timer.stop()
                Periodic_Timer.start(Update_Period_sec * sec_to_msec)
                
            else:
                Max_No_of_Readings = int(local_s)
                
            local_count += 1

    # Update the display as well #
    PyQtInterface.Config_Text.setPlainText("Update Period(s): %d \nMax Readings: %d" \
                          %(Update_Period_sec, Max_No_of_Readings))

# Function to truncate floating point numbers - returns a string #
def truncate(f, n):
    #Truncates/pads a float f to n decimal places without rounding#
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

# Function to provide instant sensor reading functionality on the client #
def Tornado_Data_Server():

    global Humidity_Data, Temperature_Data, Tornado_First_Line, Prev_Temperature, Tornado_Remote_Unit, Set_to_Fahrenheit, Prev_Message, Update_Failure

    # Poll the sensor first #
    Poll_Sensor()

    if((Humidity_Data == None) or (Temperature_Data == None)):
        message = Tornado_First_Line + "<br/><b>Error while Polling Sensor</b><br/>Please try again"
        Update_Failure = True
        
    # If the data is valid, then prepare HTML formatted string and return it #
    else:
        
        Update_Failure = False
        
        # Storing temperature for conversion purposes #
        Prev_Temperature = Temperature_Data
        
        # Unit conversion logic #
        if(Tornado_Remote_Unit == Set_to_Fahrenheit):
            local_temperature =  (Temperature_Data * 1.8) + 32
            message_1 = "<br/>Temperature: <b>%.1f*F</b>"%local_temperature
        else:
            local_temperature =  Temperature_Data
            message_1 = "<br/>Temperature: <b>%.1f*C</b>"%local_temperature
        
        # Rest of the messages including HTML formatting information #
        message_0 = "<br/><b>Sensor Reading Successful</b>"
        message_2 = "<br/>Humidity: <b>%.1f%%</b>"%Humidity_Data
        message_3 = "<br/>Updated On: <b>%s</b>"%datetime.now().time()
        Prev_Message = message_2 + message_3
        
        # Final message #
        message = Tornado_First_Line + message_0 + message_1 + message_2 + message_3
        
    return message

# This function enables the client with the ability to change the unit of temperature on the webpage #
def Tornado_Unit_Change():
    
    global Prev_Message, Tornado_Remote_Unit, Set_to_Celsius, Set_to_Fahrenheit, Prev_Temperature, Tornado_First_Line, Update_Failure
    
    # Filtering known bad conditions #
    if((Prev_Message == "") and (Update_Failure == False)):
        message = ""

    elif(Update_Failure == True):
        message = Tornado_First_Line + "<br/><b>Error while Polling Sensor</b><br/>Please try again"

    # Performing conversion #
    else:
        message_0 = "<br/><b>Sensor Reading Successful</b>"
        
        if(Tornado_Remote_Unit == Set_to_Celsius):
            Tornado_Remote_Unit = Set_to_Fahrenheit
            local_temperature =  (Prev_Temperature * 1.8) + 32
            message_1 = "<br/>Temperature: <b>%.1f*F</b>"%local_temperature
            
        else:
            Tornado_Remote_Unit = Set_to_Celsius
            local_temperature =  Prev_Temperature
            message_1 = "<br/>Temperature: <b>%.1f*C</b>"%local_temperature
        
        # Perparing final string to return #
        message = Tornado_First_Line + message_0 + message_1 + Prev_Message
        
    return message

# Function to test the speed of this route (Client - Tornado - Python - MySQL, and back) #
def Tornado_Network_Test():

    # Time stamping #
    start_time = str(datetime.now().time())
    start_time_flt = time.time()

    # Array to store data #
    Local_Humi_Arr = arr.array('f', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    # Getting last 10 entries #
    cursor.execute("""SELECT * FROM (SELECT * FROM DHT22_Table ORDER BY Readings DESC LIMIT 10) sub ORDER BY Readings ASC""")

    # Storing data to local array #
    y = 0
    for x in cursor.fetchall():
        Local_Humi_Arr[y] = float(x[2])
        y += 1

    # Table is required so formatting the same here #
    table_format_1 = "<style>table {font-family: arial,sans-serif; order-collapse: collapse; width: 50%;} "
    table_format_2 = "td, th { border: 1px solid #dddddd; text-align: center; padding: 1px;} </style>"

    # Other required strings #
    message_0 = "<br/><b>Database Readings in a Table Below</b>"
    message_1 = "<table><tr><th><b>Index</b></th><th><b>Humidity</b></th></tr>"
    message_2 = ""

    # Making one long string by looping 10 times to fill table cells #
    for x in range(0, 10):
        tmp_msg1 = "<tr><td>%d</td>"%(x+1)
        tmp_msg2 = "<td>%.1f%%</td></tr>"%Local_Humi_Arr[x]
        message_2 += tmp_msg1 + tmp_msg2
        
    # End time stamps #
    end_time = str(datetime.now().time())
    end_time_flt = time.time()

    # Elapsed time calculations #
    elapsed_time_flt = (end_time_flt - start_time_flt) * 1000000
    elapsed_time = truncate(elapsed_time_flt, 3) + "us"

    # String for timing displays in HTML #
    timings_message = "<br/>Start Time: <b>" + start_time + "</b><br/>End Time: <b>" + end_time + "</b><br/>Elapsed Time(in microseconds): <b>" + elapsed_time + "</b>"

    # Final message to be returned #
    message = "<br/><b>Network Test: Tornado & Python Route</b>" + timings_message + table_format_1 + table_format_2 + message_0 + message_1 + message_2 + "</table>"
    
    return message

# For Tornado WebSockets and Server #
class WSHandler(tornado.websocket.WebSocketHandler):
    
    # Defines the steps to be taken when a connection opens #
    def open(self):
        global Tornado_Remote_Unit, Set_to_Celsius
        
        print("New Connection")
        
        Tornado_Remote_Unit = Set_to_Celsius
    
    # Callback function when any message is received #
    def on_message(self, message):
        
        global Tornado_Data_Req_String, Tornado_Unit_Change_String, Tornado_Network_Test_String
        
        local_temperature = 0.0
        
        # Print out the message that was received #
        print("message received:  %s" % message)
        
        # Appropriate function to call based on the client request #
        if(message == Tornado_Data_Req_String):
            message = Tornado_Data_Server()
            
        elif(message == Tornado_Unit_Change_String):
            message = Tornado_Unit_Change()
                
        elif(message == Tornado_Network_Test_String):
            message = Tornado_Network_Test()
            
        # Error condition #
        else:
            print("Unknown Request: Strings Didn't Match")
            
            message = Tornado_First_Line + "<br/><b>Unknown Request</b>"
        
        # Sending back appropriate response #
        self.write_message(message)
 
     # Callback for connection closed event #
    def on_close(self):
        print ('connection closed')
 
     # Useful for some reason #
    def check_origin(self, origin):
        return True

# Starting Tornado application #
application = tornado.web.Application([(r'/ws', WSHandler),])

# Function callback used by multiprocessing module - for Tornado related tasks #
def tornado_func():
    
    global Tornado_PID
    
    # Forcing Tornado process to run on CPU Core 1 #
    Tornado_PID = os.getpid()
    os.system("taskset -p 0x22 %d" % os.getpid())
    
    print("Tornado Process bound to CPU Core #1")
    print("Tornado's pid is: {}".format(os.getpid()))
    
    # Starting Tornado Server and ioloop #
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    print("Tornado Server has been Started")
    tornado.ioloop.IOLoop.instance().start()

# Function callback used by multiprocessing module - for PyQT and all other Project 1 functionalities #
def QT_func():
    
    global PyQtInterface, cursor, db, Periodic_Timer
    
    # Forcing PyQT process to run on CPU Core 2 #
    os.system("taskset -p 0x44 %d" % os.getpid())
    
    print("IQT Process bound to CPU Core #2")
    print("QT's pid is: {}".format(os.getpid()))
    
    # Neccessary MySQL database functions #
    cursor.execute("DROP TABLE IF EXISTS DHT22_Table")
    cursor.execute("CREATE TABLE DHT22_Table (Readings INT UNSIGNED NOT NULL AUTO_INCREMENT, Temperature FLOAT, Humidity FLOAT, PRIMARY KEY (Readings))")
    cursor.execute("ALTER TABLE `DHT22_Table` ADD `Time_Stamp` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP")
    
    # Start PyQT and its own event loop #
    app  =  QApplication([])
    PyQtInterface = MatplotlibWidget()
    PyQtInterface.show()
    app.exec_()
    
    # Stop the timer when PyQT's event loop is terminated #
    Periodic_Timer.stop()
    
    # Print out all stored data in the Database #
    cursor.execute("""SELECT * FROM DHT22_Table;""")
    for x in cursor.fetchall():
        print ("Readings: ", x[0], "Temperature: ", x[1], "C", "Humidity: ", x[2], "%", "Time_Stamp: ", x[3])
 
# Not using these right now #
#    cursor.execute("TRUNCATE TABLE DHT22_Table")
#    cursor.execute("DROP TABLE DHT22_Table")
    
    db.close()
  
if __name__ == "__main__": 
    
    # Creating 2 different processes #
    
    # Connecting to MySQL database #
    db = MySQLdb.connect("localhost","poorn","root","EID_Project1_DB")
    db.autocommit(True)
    cursor = db.cursor()
    
    p1 = multiprocessing.Process(target=tornado_func, ) 
    p2 = multiprocessing.Process(target=QT_func, ) 
  
    # Starting Tornado Process #
    p1.start()
    
    # Starting PyQT Process #
    p2.start() 
  
    # Wait for PyQT Process to be done #
    p2.join()
    
    print("PyQT Done")
#    time.sleep(10)
#    ioloop = tornado.ioloop.IOLoop.instance()
#    ioloop.add_callback(ioloop.stop)
#    tornado.ioloop.IOLoop.instance().stop()
#    wait until process 1 is finished 
    p1.join()
    
    quit()