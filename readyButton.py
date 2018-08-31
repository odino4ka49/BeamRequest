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


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.b1 = QPushButton("e-")
        self.b1.setCheckable(True)
        self.b1.clicked.connect(lambda:self.whichbtn(self.b1))
        self.b1.setStyleSheet('QPushButton:checked { border-image: url(images/squareprev.png)}')
        self.b1.setFixedSize(100,100)
        layout.addWidget(self.b1)

        self.b2 = QPushButton("e+")
        self.b2.setCheckable(True)
        self.b2.clicked.connect(lambda:self.whichbtn(self.b2))
        self.b2.setFixedSize(100,100)
        self.b2.setStyleSheet('QPushButton:checked { border-image: url(images/squareprev.png)}')
        layout.addWidget(self.b2)

        self.pvname = "VEPP3:InjRequest-SP"

        self.polarity = 0
        self.setWindowTitle("Request")
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

    def setbtnzero(self,b):
        if b.isChecked():
            b.toggle()

    def setbtnuno(self,b):
        if not b.isChecked():
            b.toggle()

    def whichbtn(self,b):
        if b.isChecked():
            if b.text()=="e+":
                self.setPv(2)
                self.setbtnzero(self.b1)
            elif b.text()=="e-":
                self.setPv(1)
                self.setbtnzero(self.b2)

        else:
            self.setPv(0)

    def setbtns(self,pv_val):
        print "camonitor",pv_val
        self.polarity = pv_val
        if pv_val==0:
            self.setbtnzero(self.b1)
            self.setbtnzero(self.b2)
        elif pv_val==1:
            self.setbtnuno(self.b1)
            self.setbtnzero(self.b2)
        elif pv_val==2:
            self.setbtnzero(self.b1)
            self.setbtnuno(self.b2)

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
    ex = Form()
    ex.show()
    cothread.WaitForQuit()

if __name__ == '__main__':
    main()