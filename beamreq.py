__author__ = 'oidin'

import cothread.catools as catools
import cothread
import sys
import psycopg2
from datetime import date, datetime
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from cothread.catools import *


class LoggingThread(QThread):
    def __init__(self, filename):
        QThread.__init__(self)
        self.filename = filename

    def __del__(self):
        self.wait()

    def getTime(self):    
	timenow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	return timenow

    def getPersonSurname(self):
	surname = "Anderson"
	try:
	    conn = psycopg2.connect("dbname=v4parameters user=vepp4 host=vepp4-pg port=5432")
	    cur = conn.cursor()
	    duty = 1 if (datetime.now().hour < 21) else 2
	    cur.execute("""SELECT ddate, dname, nduty FROM ttvduty WHERE ddate = %s AND nduty = %s;""",
		    (date.today().isoformat(), duty,))
	    rows = cur.fetchall()
	    row = rows[0]
	    if isinstance(row, list):
	        surname = row[1].decode('koi8-r').encode('utf-8')
	    cur.close()
	    conn.close()
	except Exception as e:
	    surname = format(e)
	return surname

    def logPressEvent(self,time,value,person):
	print "logme",time,value,person
	file = open(self.filename,'a+')
	text = time + " " + str(value) + " " + person + "\n"
	file.write(text)
	file.close()

    def savePressEvent(self, value):
	time = self.getTime()
	person = self.getPersonSurname()
	self.logPressEvent(time,value,person)


class ConfigInfo(QDialog):
    def __init__(self, parent=None):
        super(ConfigInfo, self).__init__(parent)
        self.setWindowTitle("Config info")

        label = QLabel()
        label.setText('Config file: "/home/oidin/projects/readybutton/ReadyButton/config"')
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
        self.resize(50, 50)

        helpaction = QAction("&config file", self)
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
        self.setStyleSheet(
            'QPushButton { border-image: url(/home/oidin/projects/readybutton/ReadyButton/images/gray-rectangle-button.png);font-size:30px;}'
            'QPushButton:checked { border-image: url(/home/oidin/projects/readybutton/ReadyButton/images/yellow-rectangle-button.svg)}')
        self.setFixedSize(80, 80)

    def setbtnzero(self):
        if self.isChecked():
            self.toggle()

    def setbtnuno(self):
        if not self.isChecked():
            self.toggle()


class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

	self.log = LoggingThread("/home/oidin/projects/readybutton/ReadyButton/log")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.b1 = RequestButton("e-")
        self.b1.clicked.connect(lambda: self.whichbtn(self.b1))
        layout.addWidget(self.b1)

        self.b2 = RequestButton("e+")
        self.b2.clicked.connect(lambda: self.whichbtn(self.b2))
        layout.addWidget(self.b2)

        self.pvname = "VEPP3:InjRequest-SP"

        self.polarity = 0
        self.syncronize(self.pvname)

        camonitor(self.pvname, self.setbtns)
        self.check_coef = 0.9
        self.readConfig()
        self.subscribeToCheck()

    def subscribeToCheck(self):
        camonitor("VEPP3:Status-RB", self.checkCurrent)
        camonitor("VEPP3:InjRequest-SP", self.checkCurrent)
        camonitor("VEPP3:Polarity-RB", self.checkCurrent)
        camonitor("VEPP3:CurrentRequest-RB", self.checkCurrent)
        camonitor("VEPP3:CurrentTotal-RB", self.checkCurrent)

    def whichbtn(self, b):
	try:
            if b.isChecked():
                if b.text() == "e+":
                    self.setPv(2)
                    self.b1.setbtnzero()
		    self.log.savePressEvent(2)
                elif b.text() == "e-":
                    self.setPv(1)
                    self.b2.setbtnzero()
		    self.log.savePressEvent(1)
            else:
                self.setPv(0)
		self.log.savePressEvent(0)
        except Exception as e:
            self.displayError(format(e))
	    self.syncronize(self.pvname)

    def syncronize(self, pvname):
	try:
	    self.setbtns(caget(pvname))
	except Exception as e:
	    self.displayError(format(e))

    def setbtns(self, pv_val):
        print "camonitor", pv_val
        self.polarity = pv_val
        if pv_val == 0:
            self.b1.setbtnzero()
            self.b2.setbtnzero()
        elif pv_val == 1:
            self.b1.setbtnuno()
            self.b2.setbtnzero()
        elif pv_val == 2:
            self.b1.setbtnzero()
            self.b2.setbtnuno()

    def setPv(self, value):
        while True:
            try:
                caput(self.pvname, float(value), wait=True)
            except:
                caput(self.pvname, float(value), wait=True)
            else:
                break

    def checkCurrent(self, value):
	try:
	    status = caget("VEPP3:Status-RB")
	    if status == 2:
	        polarity = caget("VEPP3:Polarity-RB")
	        if polarity == self.polarity:
		    currentreq = caget("VEPP3:CurrentRequest-RB")
		    currenttotal = caget("VEPP3:CurrentTotal-RB")
		    if currenttotal > currentreq * self.check_coef:
		        self.setPv(0)
	except Exception as e:
	    self.displayError(format(e))

    def readConfig(self):
        with open("/home/oidin/projects/readybutton/ReadyButton/config") as config:
            self.check_coef = config.readline()

    def displayError(self,message):
	print "heeeeeey"
        self.err = QMessageBox.critical(self,"Error",message)


def main():
    app = cothread.iqt()
    ex = MainWin()
    ex.show()
    cothread.WaitForQuit()

if __name__ == '__main__':
    main()
