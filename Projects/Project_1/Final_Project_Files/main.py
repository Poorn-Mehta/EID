# https://www.geeksforgeeks.org/global-local-variables-python/
# https://stackoverflow.com/questions/24035660/how-to-read-from-qText_Main-in-python
# https://matplotlib.org/examples/user_interfaces/embedding_in_qt5.html
# https://yapayzekalabs.blogspot.com/2018/11/pyqt5-gui-qt-designer-matplotlib.html
# https://stackoverflow.com/questions/415511/how-to-get-the-current-time-in-python
# https://stackoverflow.com/questions/25148854/how-to-display-some-non-editable-text-in-rich-format-in-gui-created-by-pyqt4
# https://stackoverflow.com/questions/44718779/embeding-plot-into-graphicsview-in-pyqt5
# https://stackoverflow.com/questions/12459811/how-to-embed-matplotlib-in-pyqt-for-dummies
# https://doc.qt.io/qt-5/qgraphicsscene.html#addPixmap
# https://doc.qt.io/qt-5/qgraphicsscene.html
# https://stackoverflow.com/questions/44193227/pyqt5-how-can-i-draw-inside-existing-qgraphicsview
# https://pythonspot.com/pyqt5-matplotlib/
# https://stackoverflow.com/questions/43947318/plotting-matplotlib-figure-inside-qwidget-using-qt-designer-form-and-pyqt5

# https://stackoverflow.com/questions/36555153/pyqt5-closing-terminating-application
# https://stackoverflow.com/questions/38283705/proper-way-to-quit-exit-a-pyqt-program
# http://www.learningaboutelectronics.com/Articles/How-to-delete-all-rows-of-a-MySQL-table-in-Python.php

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication
from PyQt5.uic import loadUi
from datetime import datetime

import array as arr

import sys, os

import MySQLdb

from  matplotlib.backends.backend_qt5agg  import(NavigationToolbar2QT  as  NavigationToolbar)

import  numpy  as  np 
import  random

import Adafruit_DHT as dht

TH = 35
TL = 15
HH = 50
HL = 10
humi = 0.0
temp = 0.0
cnt = 1

# 0 is C 1 if F
C_to_F = 0

timer = 0

temp_arr = arr.array('f', [0, 0, 0, 0, 0])
humi_arr = arr.array('f', [0, 0, 0, 0, 0])

db = MySQLdb.connect("localhost","poorn","root","EID_Project1_DB")

db.autocommit(True)

cursor = db.cursor()

cursor.execute("DROP TABLE IF EXISTS Test")

cursor.execute("CREATE TABLE Test (Readings INT UNSIGNED NOT NULL AUTO_INCREMENT, Temperature FLOAT, Humidity FLOAT, PRIMARY KEY (Readings))")

cursor.execute("ALTER TABLE `Test` ADD `Time_Stamp` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP")
     
class  MatplotlibWidget(QMainWindow):
    
    def  __init__(self):
        
        QMainWindow.__init__(self)
        
        global timer

        loadUi("qt_designer.ui" , self)

        self.setWindowTitle("PyQt5 & Matplotlib Example GUI")
        
        #added lines start
        self.Text_Main.setReadOnly(True) 
        self.Text_Main.clear()
        self.Text_Main.textCursor().insertHtml('Temperature:')
        self.Text_Main.textCursor().insertHtml('<br/>Humidity:')
        
        self.Text_C_F.setReadOnly(True)
        self.Text_C_F.clear()
        self.Text_C_F.textCursor().insertHtml('<font size="4"><b>C</b></font>')
        
        self.Text_DB.setReadOnly(True)
        self.Text_DB.clear()
        self.Text_DB.textCursor().insertHtml('<font size="3"><b>Database Information</b></font>')
        
        self.Temp_High.setPlainText(str(TH))
        self.Temp_Low.setPlainText(str(TL))
        self.Humi_High.setPlainText(str(HH))
        self.Humi_Low.setPlainText(str(HL))
        
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.Update_DB)
        timer.start(5000)
        #added lines complete

        self.Updt_Reading.clicked.connect(self.Poll_Sensor)

        self.Temp_Graph.clicked.connect(self.Draw_Temp_Graph)
        
        self.Humi_Graph.clicked.connect(self.Draw_Humi_Graph)
        
        self.Updt_Thr.clicked.connect(self.Update_Thresholds)
        
        self.C_F.clicked.connect(self.Change_Unit)

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas ,  self))
        
    def Update_DB(self):
        global humi, temp, cnt, timer
        humi, temp = dht.read(dht.DHT22, 23)
        if ((humi == None) or (temp == None)):
            self.Text_DB.clear()
            self.Text_DB.textCursor().insertHtml('<font size="4"><b>Error While Reading Sensor</b></font>')
        else:
            self.Text_DB.clear()
            self.Text_DB.textCursor().insertHtml('<font size="3"><b>Reading %d Added to Database</b></font>'%cnt)
            cnt += 1
            cursor.execute("""INSERT INTO Test (Temperature, Humidity) VALUES (%s,%s)""",(temp,humi))
        if(cnt >= 15):
            timer.stop()
#            QCoreApplication.quit()
            
 
    def Poll_Sensor(self, MainWindow):
        global TH, TL, HH, HL, C_to_F, humi, temp
        humi, temp = dht.read(dht.DHT22, 23)  # Reading humidity and temperature
        
        self.Text_Main.clear()
        
        if ((humi != None) and (temp != None)):
            if(C_to_F == 0):
                self.Text_Main.textCursor().insertHtml('Temperature: <b>%.1f*C</b>'%temp)
            else:
                temp = (temp * 1.8) + 32
                self.Text_Main.textCursor().insertHtml('Temperature: <b>%.1f*F</b>'%temp)
                
            self.Text_Main.textCursor().insertHtml('<br/>Humidity: <b>%.1f%%</b>'%humi)
            self.Text_Main.textCursor().insertHtml('<br/>Updated On: <b>%s</b>'%datetime.now().time())
            
            if((humi > float(HH)) or (humi < float(HL)) or (temp > float(TH)) or (temp < float(TL))):
                self.Text_Main.textCursor().insertHtml('<br/><b>!!!***ALERT***!!!</b>')
                if(humi > float(HH)):
                    self.Text_Main.textCursor().insertHtml('<br/><b>Humidity Too High</b>')
                if(humi < float(HL)):
                    self.Text_Main.textCursor().insertHtml('<br/><b>Humidity Too Low</b>')            
                if(temp > float(TH)):
                    self.Text_Main.textCursor().insertHtml('<br/><b>Temperature Too High</b>')
                if(temp < float(TL)):
                    self.Text_Main.textCursor().insertHtml('<br/><b>Temperature Too Low</b>')

        else:
            self.Text_Main.textCursor().insertHtml('<b>ERROR with SENSOR</b>')
            self.Text_Main.textCursor().insertHtml('<br/><b>NO RESPONSE</b>')

    def Update_Thresholds(self):
        global TH, TL, HH, HL, cnt
        TH = int(self.Temp_High.toPlainText())
        TL = int(self.Temp_Low.toPlainText())
        HH = int(self.Humi_High.toPlainText())
        HL = int(self.Humi_Low.toPlainText())
        
        self.Temp_High.setPlainText(str(TH))
        self.Temp_Low.setPlainText(str(TL))
        self.Humi_High.setPlainText(str(HH))
        self.Humi_Low.setPlainText(str(HL))
        
    def Change_Unit(self):
        global C_to_F, TH, TL
        if(C_to_F == 0):
            self.Text_C_F.clear()
            self.Text_C_F.textCursor().insertHtml('<font size="4"><b>F</b></font>')
            C_to_F = 1
            TH = int((TH * 1.8) + 32)
            TL = int((TL * 1.8) + 32)
            
        else:
            self.Text_C_F.clear()
            self.Text_C_F.textCursor().insertHtml('<font size="4"><b>C</b></font>')
            C_to_F = 0
            TH = int(((TH - 32) * 5) / 9)
            TL = int(((TL - 32) * 5) / 9)
            
        self.Temp_High.setPlainText(str(TH))
        self.Temp_Low.setPlainText(str(TL))        
        

    def Draw_Temp_Graph(self):
        global temp_arr, C_to_F
        y = 0
        cursor.execute("""SELECT * FROM (SELECT * FROM Test ORDER BY Readings DESC LIMIT 5) sub ORDER BY Readings ASC""")
        
        for x in cursor.fetchall():
            temp_arr[y] = float(x[1])
            if(C_to_F == 1):
                temp_arr[y] = (temp_arr[y] * 1.8) + 32
            y += 1
        
        print("Plotting Following Temperature Data")
        
        for x in range(0, 5):
            print("Temp Arr: %f" % temp_arr[x])


#        length_of_signal  =  10 
#        ay  =  np.linspace(-5 , 45 , length_of_signal)

        self.MplWidget.canvas.axes.clear() 
        self.MplWidget.canvas.axes.plot(temp_arr)
#        self.MplWidget.canvas.axes.plot(t ,  sinus_signal)
        self.MplWidget.canvas.axes.legend('Temp in C',loc = 'upper right')
        self.MplWidget.canvas.axes.set_title('Temperature Graph')
        self.MplWidget.canvas.draw()
        
        

    def Draw_Humi_Graph(self):
        global humi_arr
        y = 0
        cursor.execute("""SELECT * FROM (SELECT * FROM Test ORDER BY Readings DESC LIMIT 5) sub ORDER BY Readings ASC""")
        
        for x in cursor.fetchall():
            humi_arr[y] = float(x[2])
            y += 1
        
        print("Plotting Following Humidity Data")
        
        for x in range(0, 5):
            print("Humi Arr: %f" % humi_arr[x])

        self.MplWidget.canvas.axes.clear() 
        self.MplWidget.canvas.axes.plot(humi_arr)
        self.MplWidget.canvas.axes.legend('Relative Humidity',loc = 'upper right')
        self.MplWidget.canvas.axes.set_title('Humidity Graph')
        self.MplWidget.canvas.draw()
        

app  =  QApplication([]) 
window  =  MatplotlibWidget() 
window.show()

app.exec_()

timer.stop()

cursor.execute("""SELECT * FROM Test;""")
for x in cursor.fetchall():
    print ("Readings: ", x[0], "Temperature: ", x[1], "C", "Humidity: ", x[2], "%", "Time_Stamp: ", x[3])

cursor.execute("TRUNCATE TABLE Test")

cursor.execute("DROP TABLE Test")

db.close()

quit()
    