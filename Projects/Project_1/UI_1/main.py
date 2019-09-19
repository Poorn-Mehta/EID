from  PyQt5.QtWidgets  import *
from PyQt5.uic import loadUi
from datetime import datetime
   

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

# 0 is C 1 if F
C_to_F = 0
     
class  MatplotlibWidget(QMainWindow):
    
    def  __init__(self):
        
        QMainWindow.__init__(self)

        loadUi("qt_designer.ui" , self)

        self.setWindowTitle("PyQt5 & Matplotlib Example GUI")
        
        #added lines start
        self.textEdit.setReadOnly(True)
        self.textEdit.clear()
        self.textEdit.textCursor().insertHtml('Temperature:')
        self.textEdit.textCursor().insertHtml('<br/>Humidity:')
        
        self.Temp_High.setPlainText(str(TH))
        self.Temp_Low.setPlainText(str(TL))
        self.Humi_High.setPlainText(str(HH))
        self.Humi_Low.setPlainText(str(HL))
        #added lines complete

        self.pushButton.clicked.connect(self.button_click)

        self.pushButton_2.clicked.connect(self.update_graph)
        
        self.Updt_Thr.clicked.connect(self.update_thresholds)
        
        self.C_F.clicked.connect(self.change_unit)

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas ,  self))
 
    def button_click(self, MainWindow):
        global TH, TL, HH, HL, C_to_F, humi, temp
        humi, temp = dht.read(dht.DHT22, 23)  # Reading humidity and temperature
        
        self.textEdit.clear()
        
        if ((humi != None) and (temp != None)):
            if(C_to_F == 0):
                self.textEdit.textCursor().insertHtml('Temperature: <b>%.1f*C</b>'%temp)
            else:
                temp = (temp * 1.8) + 32
                self.textEdit.textCursor().insertHtml('Temperature: <b>%.1f*F</b>'%temp)
                
            self.textEdit.textCursor().insertHtml('<br/>Humidity: <b>%.1f%%</b>'%humi)
            self.textEdit.textCursor().insertHtml('<br/>Updated On: <b>%s</b>'%datetime.now().time())
            
            if((humi > float(HH)) or (humi < float(HL)) or (temp > float(TH)) or (temp < float(TL))):
                self.textEdit.textCursor().insertHtml('<br/><b>!!!***ALERT***!!!</b>')
                if(humi > float(HH)):
                    self.textEdit.textCursor().insertHtml('<br/><b>Humidity Too High</b>')
                if(humi < float(HL)):
                    self.textEdit.textCursor().insertHtml('<br/><b>Humidity Too Low</b>')            
                if(temp > float(TH)):
                    self.textEdit.textCursor().insertHtml('<br/><b>Temperature Too High</b>')
                if(temp < float(TL)):
                    self.textEdit.textCursor().insertHtml('<br/><b>Temperature Too Low</b>')

        else:
            self.textEdit.textCursor().insertHtml('<b>ERROR with SENSOR</b>')
            self.textEdit.textCursor().insertHtml('<br/><b>NO RESPONSE</b>')

    def update_thresholds(self):
        global TH, TL, HH, HL
        TH = int(self.Temp_High.toPlainText())
        TL = int(self.Temp_Low.toPlainText())
        HH = int(self.Humi_High.toPlainText())
        HL = int(self.Humi_Low.toPlainText())
        
        self.Temp_High.setPlainText(str(TH))
        self.Temp_Low.setPlainText(str(TL))
        self.Humi_High.setPlainText(str(HH))
        self.Humi_Low.setPlainText(str(HL))
        
    def change_unit(self):
        global C_to_F, TH, TL
        if(C_to_F == 0):
            C_to_F = 1
            TH = int((TH * 1.8) + 32)
            TL = int((TL * 1.8) + 32)
            
        else:
            C_to_F = 0
            TH = int(((TH - 32) * 5) / 9)
            TL = int(((TL - 32) * 5) / 9)
            
        self.Temp_High.setPlainText(str(TH))
        self.Temp_Low.setPlainText(str(TL))        
        

    def update_graph(self):

        fs  =  500 
        f  =  random.randint(1 ,  100)
        ts  =  1 / fs 
        length_of_signal  =  100 
        t  =  np.linspace(0 , 1 , length_of_signal)
        
        cosinus_signal  =  np.cos(2 * np.pi * f * t)
        sinus_signal  =  np.sin(2 * np.pi * f * t)

        self.MplWidget.canvas.axes.clear() 
        self.MplWidget.canvas.axes.plot(t ,  cosinus_signal)
        self.MplWidget.canvas.axes.plot(t ,  sinus_signal)
        self.MplWidget.canvas.axes.legend(( 'cosinus' ,  'sinus'),loc = 'upper right')
        self.MplWidget.canvas.axes.set_title(' Cosinus - Sinus Signal')
        self.MplWidget.canvas.draw()
        

app  =  QApplication([]) 
window  =  MatplotlibWidget() 
window.show() 
app.exec_()