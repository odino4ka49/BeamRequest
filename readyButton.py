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
        layout.addWidget(self.b1)

        self.b2 = QPushButton("e+")
        self.b2.setCheckable(True)
        self.b2.clicked.connect(lambda:self.whichbtn(self.b2))
        layout.addWidget(self.b2)

        self.pvname = "VEPP3:InjRequest-SP"

        self.setWindowTitle("Ready")
        self.setbtns(caget(self.pvname))
        camonitor(self.pvname,self.setbtns)


    def setbtnzero(self,b):
        if b.isChecked():
            b.toggle()

    def setbtnuno(self,b):
        if not b.isChecked():
            b.toggle()

    def whichbtn(self,b):
        if b.isChecked():
            if b.text()=="e+":
                setPv(2)
                self.setbtnzero(self.b1)
            elif b.text()=="e-":
                setPv(1)
                self.setbtnzero(self.b2)

        else:
            setPv(0.0)

    def setbtns(self,pv_val):
        print "camonitor",pv_val
        pv_val = caget(self.pvname)
        if pv_val==0:
            self.setbtnzero(self.b1)
            self.setbtnzero(self.b2)
        elif pv_val==1:
            self.setbtnuno(self.b1)
            self.setbtnzero(self.b2)
        elif pv_val==2:
            self.setbtnzero(self.b1)
            self.setbtnuno(self.b2)


def setPv(value):
    pv = "VEPP3:InjRequest-SP"
    while True:
        try:
            caput(pv,float(value),wait=True)
        except:
            caput(pv,float(value),wait=True)
        else:
            break
            #print "caget",caget(pv)


def main():
    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()