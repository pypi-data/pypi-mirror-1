# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/fccoelho/Documents/Projects_software/epigrass/Epigrass-devel/cpanel.ui'
#
# Created: Seg Out 23 11:03:40 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.15.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x20\x00\x00\x00\x20" \
    "\x08\x06\x00\x00\x00\x73\x7a\x7a\xf4\x00\x00\x00" \
    "\xdc\x49\x44\x41\x54\x58\x85\xed\x96\x59\x0e\xc3" \
    "\x20\x0c\x44\x1f\x55\xef\x55\x1f\x9d\x9b\x39\x1f" \
    "\x55\x22\x67\x81\x62\x16\xd1\x56\x19\x29\x5f\x04" \
    "\x66\x0c\xc3\x98\x00\x40\x44\x59\x21\x04\x3c\x68" \
    "\x99\x0b\x3c\xcf\xeb\x45\xbd\xfa\x31\x05\x41\xbc" \
    "\x9c\x79\x01\x82\x78\xab\x70\x09\x4e\xc2\x5b\x79" \
    "\x2f\x3c\x66\x90\xde\x02\x6e\x01\x5f\x25\xe0\x7d" \
    "\xe7\x4b\xd2\xac\x31\xf1\x52\x28\x4e\xc2\xd6\xc4" \
    "\x2b\x16\x90\x49\xc2\xb1\x41\x35\x2b\x09\x4f\x3b" \
    "\x60\x91\x39\x8e\x71\x1e\x38\x92\x5f\x91\xd9\x31" \
    "\x35\x47\x13\x68\x30\xa7\xad\xb6\xf4\x38\x22\x51" \
    "\x15\xb6\xaf\x9a\xdc\x92\x7a\xbd\xd0\x55\xc0\x0c" \
    "\x23\xfe\x46\x12\x66\x8d\xd6\xeb\x4d\xa8\x02\x21" \
    "\xa6\x3c\x20\x86\x6f\x3f\x2e\xc8\x36\xb7\x06\xd3" \
    "\x77\xc0\xac\x53\x6f\xc0\x96\xb9\xd3\x4d\xb8\x43" \
    "\x6d\x25\xff\xb3\x03\xe0\xaf\x66\x48\x78\x79\x7a" \
    "\x41\x2b\x57\xf2\xda\xac\x8b\xbf\x4c\x06\xac\x57" \
    "\x30\xd7\x29\xbb\xe2\xd8\xed\x46\xf4\x8b\x8f\x15" \
    "\x74\xeb\xf7\x09\x2c\x49\xf5\x7d\xcb\x80\x93\xf4" \
    "\xd9\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60" \
    "\x82"

class MainPanel(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("MainPanel")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setMinimumSize(QSize(560,480))
        self.setMaximumSize(QSize(560,480))
        self.setIcon(self.image0)


        LayoutWidget = QWidget(self,"Layout1")
        LayoutWidget.setGeometry(QRect(10,420,520,38))
        Layout1 = QHBoxLayout(LayoutWidget,0,6,"Layout1")

        self.buttonHelp = QPushButton(LayoutWidget,"buttonHelp")
        self.buttonHelp.setAutoDefault(1)
        Layout1.addWidget(self.buttonHelp)
        Horizontal_Spacing2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        Layout1.addItem(Horizontal_Spacing2)

        self.buttonRun = QPushButton(LayoutWidget,"buttonRun")
        self.buttonRun.setAutoDefault(1)
        self.buttonRun.setDefault(1)
        Layout1.addWidget(self.buttonRun)

        self.buttonExit = QPushButton(LayoutWidget,"buttonExit")
        self.buttonExit.setAutoDefault(1)
        Layout1.addWidget(self.buttonExit)

        self.textLabel1_6 = QLabel(self,"textLabel1_6")
        self.textLabel1_6.setGeometry(QRect(330,380,110,23))

        self.stepLCD = QLCDNumber(self,"stepLCD")
        self.stepLCD.setGeometry(QRect(450,380,64,23))

        self.tabWidget = QTabWidget(self,"tabWidget")
        self.tabWidget.setEnabled(1)
        self.tabWidget.setGeometry(QRect(10,0,520,370))

        self.Widget8 = QWidget(self.tabWidget,"Widget8")

        self.dbType = QComboBox(0,self.Widget8,"dbType")
        self.dbType.setGeometry(QRect(6,176,220,25))

        self.dbSpecGroupBox = QGroupBox(self.Widget8,"dbSpecGroupBox")
        self.dbSpecGroupBox.setEnabled(0)
        self.dbSpecGroupBox.setGeometry(QRect(236,160,268,150))
        self.dbSpecGroupBox.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred,0,0,self.dbSpecGroupBox.sizePolicy().hasHeightForWidth()))

        LayoutWidget_2 = QWidget(self.dbSpecGroupBox,"layout7")
        LayoutWidget_2.setGeometry(QRect(6,24,254,106))
        layout7 = QGridLayout(LayoutWidget_2,1,1,6,6,"layout7")

        self.textLabel2 = QLabel(LayoutWidget_2,"textLabel2")

        layout7.addWidget(self.textLabel2,0,0)

        self.portEdit = QLineEdit(LayoutWidget_2,"portEdit")

        layout7.addWidget(self.portEdit,1,1)

        self.textLabel3 = QLabel(LayoutWidget_2,"textLabel3")

        layout7.addWidget(self.textLabel3,0,1)

        self.pwEdit = QLineEdit(LayoutWidget_2,"pwEdit")
        self.pwEdit.setEchoMode(QLineEdit.Password)

        layout7.addWidget(self.pwEdit,3,1)

        self.textLabel1_2 = QLabel(LayoutWidget_2,"textLabel1_2")

        layout7.addWidget(self.textLabel1_2,2,1)

        self.textLabel4 = QLabel(LayoutWidget_2,"textLabel4")

        layout7.addWidget(self.textLabel4,2,0)

        self.hostnEdit = QLineEdit(LayoutWidget_2,"hostnEdit")

        layout7.addWidget(self.hostnEdit,1,0)

        self.uidEdit = QLineEdit(LayoutWidget_2,"uidEdit")

        layout7.addWidget(self.uidEdit,3,0)

        self.modSpec = QGroupBox(self.Widget8,"modSpec")
        self.modSpec.setGeometry(QRect(6,6,500,140))

        self.scriptNameEdit = QLineEdit(self.modSpec,"scriptNameEdit")
        self.scriptNameEdit.setGeometry(QRect(10,50,305,25))

        self.chooseButton = QPushButton(self.modSpec,"chooseButton")
        self.chooseButton.setGeometry(QRect(320,50,82,27))

        self.editButton = QPushButton(self.modSpec,"editButton")
        self.editButton.setGeometry(QRect(410,50,82,27))

        self.textLabel1 = QLabel(self.modSpec,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,20,300,27))

        self.textLabel1_11 = QLabel(self.Widget8,"textLabel1_11")
        self.textLabel1_11.setGeometry(QRect(6,156,230,20))
        self.tabWidget.insertTab(self.Widget8,QString.fromLatin1(""))

        self.Widget9 = QWidget(self.tabWidget,"Widget9")

        self.textLabel5 = QLabel(self.Widget9,"textLabel5")
        self.textLabel5.setGeometry(QRect(0,60,60,23))

        self.textLabel2_2 = QLabel(self.Widget9,"textLabel2_2")
        self.textLabel2_2.setGeometry(QRect(3,19,60,23))

        self.unameEdit = QLineEdit(self.Widget9,"unameEdit")
        self.unameEdit.setGeometry(QRect(70,20,172,28))

        self.editorEdit = QLineEdit(self.Widget9,"editorEdit")
        self.editorEdit.setGeometry(QRect(70,60,172,28))

        self.textLabel1_5 = QLabel(self.Widget9,"textLabel1_5")
        self.textLabel1_5.setGeometry(QRect(0,139,110,33))

        self.pdfEdit = QLineEdit(self.Widget9,"pdfEdit")
        self.pdfEdit.setGeometry(QRect(149,98,172,25))

        self.textLabel2_3 = QLabel(self.Widget9,"textLabel2_3")
        self.textLabel2_3.setGeometry(QRect(-1,98,150,23))

        self.langCombo = QComboBox(0,self.Widget9,"langCombo")
        self.langCombo.setGeometry(QRect(112,139,190,33))
        self.tabWidget.insertTab(self.Widget9,QString.fromLatin1(""))

        self.TabPage = QWidget(self.tabWidget,"TabPage")

        self.textEdit1 = QTextEdit(self.TabPage,"textEdit1")
        self.textEdit1.setGeometry(QRect(0,30,281,300))

        self.line1 = QFrame(self.TabPage,"line1")
        self.line1.setGeometry(QRect(289,35,20,320))
        self.line1.setFrameShape(QFrame.VLine)
        self.line1.setFrameShadow(QFrame.Sunken)
        self.line1.setLineWidth(3)
        self.line1.setFrameShape(QFrame.VLine)

        self.line2 = QFrame(self.TabPage,"line2")
        self.line2.setGeometry(QRect(321,138,178,16))
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.line2.setLineWidth(2)
        self.line2.setFrameShape(QFrame.HLine)

        self.repOpen = QPushButton(self.TabPage,"repOpen")
        self.repOpen.setGeometry(QRect(321,196,178,33))

        self.textLabel5_2 = QLabel(self.TabPage,"textLabel5_2")
        self.textLabel5_2.setGeometry(QRect(10,10,260,23))

        self.textLabel1_3 = QLabel(self.TabPage,"textLabel1_3")
        self.textLabel1_3.setGeometry(QRect(320,10,178,20))
        self.textLabel1_3.setAlignment(QLabel.AlignCenter)

        self.textLabel1_4 = QLabel(self.TabPage,"textLabel1_4")
        self.textLabel1_4.setGeometry(QRect(321,167,178,20))
        self.textLabel1_4.setMargin(0)
        self.textLabel1_4.setAlignment(QLabel.AlignCenter)

        self.dbInfo = QPushButton(self.TabPage,"dbInfo")
        self.dbInfo.setEnabled(0)
        self.dbInfo.setGeometry(QRect(321,89,178,33))

        self.dbBackup = QPushButton(self.TabPage,"dbBackup")
        self.dbBackup.setEnabled(0)
        self.dbBackup.setGeometry(QRect(320,40,178,33))
        self.tabWidget.insertTab(self.TabPage,QString.fromLatin1(""))

        self.visPage = QWidget(self.tabWidget,"visPage")

        self.rateSpinBox = QSpinBox(self.visPage,"rateSpinBox")
        self.rateSpinBox.setGeometry(QRect(399,115,58,28))
        self.rateSpinBox.setMinValue(20)

        self.textLabel1_8 = QLabel(self.visPage,"textLabel1_8")
        self.textLabel1_8.setGeometry(QRect(359,65,140,47))

        self.playButton = QPushButton(self.visPage,"playButton")
        self.playButton.setGeometry(QRect(324,161,176,34))

        self.consensusButton = QPushButton(self.visPage,"consensusButton")
        self.consensusButton.setGeometry(QRect(8,293,240,34))

        self.textLabel1_9 = QLabel(self.visPage,"textLabel1_9")
        self.textLabel1_9.setGeometry(QRect(8,263,320,25))

        self.line3 = QFrame(self.visPage,"line3")
        self.line3.setGeometry(QRect(-2,243,520,20))
        self.line3.setFrameShape(QFrame.HLine)
        self.line3.setFrameShadow(QFrame.Sunken)
        self.line3.setFrameShape(QFrame.HLine)

        self.tableList = QComboBox(0,self.visPage,"tableList")
        self.tableList.setGeometry(QRect(0,50,330,36))

        self.mapList = QComboBox(0,self.visPage,"mapList")
        self.mapList.setEnabled(1)
        self.mapList.setGeometry(QRect(0,212,310,32))

        self.variableList = QComboBox(0,self.visPage,"variableList")
        self.variableList.setGeometry(QRect(0,130,310,31))

        self.dbscanButton = QPushButton(self.visPage,"dbscanButton")
        self.dbscanButton.setGeometry(QRect(340,10,160,36))

        self.textLabel1_7 = QLabel(self.visPage,"textLabel1_7")
        self.textLabel1_7.setGeometry(QRect(10,20,310,23))

        self.textLabel1_10 = QLabel(self.visPage,"textLabel1_10")
        self.textLabel1_10.setGeometry(QRect(8,100,300,20))

        self.textLabel2_4 = QLabel(self.visPage,"textLabel2_4")
        self.textLabel2_4.setEnabled(1)
        self.textLabel2_4.setGeometry(QRect(10,180,290,23))
        self.tabWidget.insertTab(self.visPage,QString.fromLatin1(""))

        self.languageChange()

        self.resize(QSize(560,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Epigrass Control Panel"))
        self.buttonHelp.setText(self.__tr("&Help"))
        self.buttonHelp.setAccel(self.__tr("F1"))
        QToolTip.add(self.buttonHelp,self.__tr("Click here to open the userguide in the web browser"))
        self.buttonRun.setText(self.__tr("&Run"))
        self.buttonRun.setAccel(self.__tr("Alt+R"))
        QToolTip.add(self.buttonRun,self.__tr("Click here to start your simulation"))
        self.buttonExit.setText(self.__tr("&Exit"))
        self.buttonExit.setAccel(self.__tr("Alt+E"))
        QToolTip.add(self.buttonExit,self.__tr("Click here to leave Epigrass"))
        self.textLabel1_6.setText(self.__tr("Progress:"))
        QToolTip.add(self.stepLCD,self.__tr("Simulation step"))
        QToolTip.add(self.tabWidget,QString.null)
        self.dbType.clear()
        self.dbType.insertItem(self.__tr("MySQL"))
        self.dbType.insertItem(self.__tr("SQLite"))
        self.dbType.setCurrentItem(1)
        QToolTip.add(self.dbType,self.__tr("Select your database type"))
        self.dbSpecGroupBox.setTitle(self.__tr("Database Specification"))
        self.textLabel2.setText(self.__tr("Host:"))
        self.portEdit.setText(self.__tr("3306"))
        QToolTip.add(self.portEdit,self.__tr("Enter the port  the server listens to."))
        self.textLabel3.setText(self.__tr("Port:"))
        QToolTip.add(self.pwEdit,self.__tr("Database password for the userid entered"))
        self.textLabel1_2.setText(self.__tr("Password:"))
        self.textLabel4.setText(self.__tr("Userid:"))
        self.hostnEdit.setText(self.__tr("localhost"))
        QToolTip.add(self.hostnEdit,self.__tr("This is the url of your database server."))
        QToolTip.add(self.uidEdit,self.__tr("This is the userid for accessing the database server"))
        self.modSpec.setTitle(self.__tr("Model Specification"))
        QToolTip.add(self.scriptNameEdit,self.__tr("write the name of the your script or press the choose button on the right to select one."))
        self.chooseButton.setText(self.__tr("Choose"))
        self.editButton.setText(self.__tr("Edit"))
        self.textLabel1.setText(self.__tr("Script Name:"))
        self.textLabel1_11.setText(self.__tr("Database type:"))
        self.tabWidget.changeTab(self.Widget8,self.__tr("Run Options"))
        self.textLabel5.setText(self.__tr("Editor"))
        self.textLabel2_2.setText(self.__tr("Name"))
        QToolTip.add(self.unameEdit,self.__tr("Enter your full name. This will be added to the report."))
        QToolTip.add(self.editorEdit,self.__tr("Enter your preferred text editor"))
        self.textLabel1_5.setText(self.__tr("Language"))
        self.pdfEdit.setText(QString.null)
        QToolTip.add(self.pdfEdit,self.__tr("Enter the name of your preferred PDF viewer"))
        self.textLabel2_3.setText(self.__tr("PDF Viewer"))
        self.langCombo.clear()
        self.langCombo.insertItem(self.__tr("English"))
        self.langCombo.insertItem(self.__tr("Brazilian portuguese"))
        self.langCombo.insertItem(self.__tr("French"))
        QToolTip.add(self.langCombo,self.__tr("Select the language for the GUI"))
        self.tabWidget.changeTab(self.Widget9,self.__tr("Settings"))
        self.repOpen.setText(self.__tr("Open"))
        self.textLabel5_2.setText(self.__tr("Simulation Status"))
        self.textLabel1_3.setText(self.__tr("Database"))
        self.textLabel1_4.setText(self.__tr("Report"))
        self.dbInfo.setText(self.__tr("Info"))
        QToolTip.add(self.dbInfo,self.__tr("Click here for a short description of the epigrass database"))
        self.dbBackup.setText(self.__tr("Backup"))
        QToolTip.add(self.dbBackup,self.__tr("Click here to backup the epigrass database "))
        self.tabWidget.changeTab(self.TabPage,self.__tr("Utilities"))
        self.textLabel1_8.setText(self.__tr("Animation\n"
"rate"))
        self.playButton.setText(self.__tr("Start animation"))
        self.consensusButton.setText(self.__tr("Consensus Tree"))
        QToolTip.add(self.consensusButton,self.__tr("Select a directory with tree-files to build consensus on."))
        self.textLabel1_9.setText(self.__tr("Spread Trees"))
        QToolTip.add(self.tableList,self.__tr("Select a database stored simulation"))
        self.mapList.clear()
        self.mapList.insertItem(self.__tr("No map"))
        QToolTip.add(self.mapList,self.__tr("Select a map"))
        QToolTip.add(self.variableList,self.__tr("Select a variable to display in the animation"))
        self.dbscanButton.setText(self.__tr("Scan DB"))
        self.textLabel1_7.setText(self.__tr("Simulations stored:"))
        self.textLabel1_10.setText(self.__tr("Variable to display:"))
        self.textLabel2_4.setText(self.__tr("Maps available:"))
        self.tabWidget.changeTab(self.visPage,self.__tr("Visualization"))


    def __tr(self,s,c = None):
        return qApp.translate("MainPanel",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = MainPanel()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
