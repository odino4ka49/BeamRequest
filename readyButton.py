__author__ = 'oidin'

import cothread.catools as catools
import cothread
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from cothread.catools import *


class MonitoringThread(QThread):

    def __init__(self,pvname):
        QThread.__init__(self)
        self.pvname=pvname

    def __del__(self):
        self.wait()

    def printpv(self,pv_val):
        print pv_val

    def run(self):
        camonitor(self.pvname,self.printpv)


class ConfigInfo(QDialog):
    def __init__(self, parent=None):
        super(ConfigInfo, self).__init__(parent)
        self.setWindowTitle("Config info")

        label = QLabel()
        label.setText('Config file: "/home/vepp4/beamrequest/ReadyButton/config"')
        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addStretch()
        self.setLayout(vbox)


class MainWin(QMainWindow):

    def __init__(self):
        super(MainWin, self).__init__()
        self.form = Form(self)
        self.setCentralWidget(self.form)
        self.setWindowTitle("Request")
        self.configinfo = ConfigInfo()
        self.resize(100,200)

        helpaction = QAction("&config file",self)
        helpaction.triggered.connect(self.showconfig)
        mainmenu = self.menuBar()
        helpmenu = mainmenu.addMenu('&Help')
        helpmenu.addAction(helpaction)

    def showconfig(self):
        self.configinfo.show()


class RequestButton(QPushButton):
    def __init__(self, Text, parent=None):
        super(RequestButton, self).__init__()
        self.setupbt(Text)

    def setupbt(self, Text):
        self.setText(Text)
        self.setCheckable(True)
        self.setStyleSheet('QPushButton { border-image: url(images/gray-rectangle-button.png)}'
                           'QPushButton:checked { border-image: url(images/yellow-rectangle-button.svg)}')
        self.setFixedSize(80,80)

    def setbtnzero(self):
        if self.isChecked():
            self.toggle()

    def setbtnuno(self):
        if not self.isChecked():
            self.toggle()

class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        self.b1 = RequestButton("e-")
        self.b1.clicked.connect(lambda:self.whichbtn(self.b1))
        layout.addWidget(self.b1)

        self.b2 = RequestButton("e+")
        self.b2.clicked.connect(lambda:self.whichbtn(self.b2))
        layout.addWidget(self.b2)

        self.pvname = "VEPP3:InjRequest-SP"

        self.polarity = 0
        self.setbtns(caget(self.pvname))

        camonitor(self.pvname,self.setbtns)
        self.check_coef = 0.9
        self.readConfig()
        self.subscribeToCheck()


    def subscribeToCheck(self):
        camonitor("VEPP3:Status-RB",self.checkCurrent)
        camonitor("VEPP3:InjRequest-SP",self.checkCurrent)
        camonitor("VEPP3:Polarity-RB",self.checkCurrent)
        camonitor("VEPP3:CurrentRequest-RB",self.checkCurrent)
        camonitor("VEPP3:CurrentTotal-RB",self.checkCurrent)

    def whichbtn(self,b):
        if b.isChecked():
            if b.text()=="e+":
                self.setPv(2)
                self.b1.setbtnzero()
            elif b.text()=="e-":
                self.setPv(1)
                self.b2.setbtnzero()

        else:
            self.setPv(0)

    def setbtns(self,pv_val):
        print "camonitor",pv_val
        self.polarity = pv_val
        if pv_val==0:
            self.b1.setbtnzero()
            self.b2.setbtnzero()
        elif pv_val==1:
            self.b1.setbtnuno()
            self.b2.setbtnzero()
        elif pv_val==2:
            self.b1.setbtnzero()
            self.b2.setbtnuno()

    def setPv(self,value):
        while True:
            try:
                caput(self.pvname,float(value),wait=True)
            except:
                caput(self.pvname,float(value),wait=True)
            else:
                break

    def checkCurrent(self,value):
        status = caget("VEPP3:Status-RB")
        print status
        if status == 2:
            polarity = caget("VEPP3:Polarity-RB")
            print polarity,self.polarity
            if polarity == self.polarity:
                currentreq = caget("VEPP3:CurrentRequest-RB")
                currenttotal = caget("VEPP3:CurrentTotal-RB")
                print currenttotal,currentreq
                if currenttotal > currentreq*self.check_coef:
                    self.setPv(0)

    def readConfig(self):
        with open("config") as config:
            self.check_coef = config.readline()


def main():
    app = cothread.iqt()
    ex = MainWin()
    ex.show()
    cothread.WaitForQuit()

if __name__ == '__main__':
    main()