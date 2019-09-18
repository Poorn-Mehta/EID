import sys
import Adafruit_DHT as dht    # Importing Adafruit library for DHT22
from time import sleep           # Impoting sleep from time library to add delay
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import random

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(599, 349)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(70, 120, 161, 61))
        self.pushButton.setObjectName("pushButton")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(310, 60, 256, 192))
        self.graphicsView.setObjectName("graphicsView")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(50, 50, 201, 61))
        self.textEdit.setObjectName("textEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        #added lines start
        self.textEdit.setReadOnly(True)
        self.textEdit.clear()
        self.textEdit.textCursor().insertHtml('Temperature:')
        self.textEdit.textCursor().insertHtml('<br/>Humidity:')
        #added lines complete
        
        
    def button_click(self, MainWindow):
        humi, temp = dht.read_retry(dht.DHT22, 23)  # Reading humidity and temperature
#        print ("Temp: {0:0.1f}*C  Humidity: {1:0.1f}%".format(temp, humi))
        self.textEdit.clear()
        self.textEdit.textCursor().insertHtml('Temperature: <b>%.1f*C</b>'%temp)
        self.textEdit.textCursor().insertHtml('<br/>Humidity: <b>%.1f%%</b>'%humi)
#    QMessageBox.information(MainWindow, 'Example', 'Welcome')

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DHT22 Controller"))
        self.pushButton.setText(_translate("MainWindow", "Update Readings"))
        #user code
        self.pushButton.clicked.connect(self.button_click)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
