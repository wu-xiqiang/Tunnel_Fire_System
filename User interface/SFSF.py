# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QWidget, QHeaderView
from PyQt5.QtWidgets import QDialog,QTableWidgetItem
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib
matplotlib.use('Agg')

import cv2
from PIL import Image
from io import BytesIO
import time
import threading
import numpy as np
import mysql.connector
import sys, os
global Results_history, Fire_Loc, H_RR, Wind_Spe

class Manual_show(QWidget):
    
    def __init__(self):
        super(Manual_show, self).__init__()
        self.resize(500, 500)
        self.setWindowTitle("User Manual")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(50, 20, 400, 50))
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(50, 50, 400, 450))
        
       
        palette = QtGui.QPalette()
        self.label.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setText("This is the manual of the firefighting system (v2107):\n\n")
        self.label.setWordWrap(True)
        self.label.setStyleSheet("color:blue")
        
        palette = QtGui.QPalette()
        self.label_2.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_2.setFont(font)
        self.label_2.setWordWrap(True)
        self.label_2.setAlignment(QtCore.Qt.AlignJustify)
        self.label_2.setText("(1) Fill in the required information for the database and press the button ''connect'' to connect to the database. ''Server is connected successfully'' will be given in the command prompt area. \n\n" +
                              "(2) Then, input the length, width, and height of the tunnel for displaying the first graph in the display area.\n\n" +
                              "(3) Choose the displaying mode of the quantities from the list of temperature, smoke and toxic gases, and set the refresh interval of the display and output.\n\n" +
                              "(4) Press the ''Start'' button for the beginning of the display and predictions. The displaying and output can be paused for closely checking by pressing the ''Pause'' button and restart again by pressing the ''Start'' button.\n\n" + 
                              "The history of the predictions, including the fire location, fire size, occurrence of the critical events is available for review by prestressing the button ''History.''")     
        

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(800, 500)
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setGeometry(QtCore.QRect(50, 50, 700, 400))
        self.tableWidget.setRowCount(60)
        self.tableWidget.setColumnCount(20)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(80)
        self.tableWidget.setColumnWidth(0, 100)
        # self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        column_name = ['Date&Time'] + ['Loc (m)', 'HRR (kW)', 'Vent (m/s)'] + ['Sensor ' + str(i) + ' (C)'  for i in np.arange(1,17,1)]
        self.tableWidget.setHorizontalHeaderLabels(column_name)
        self.tableWidget.setObjectName("tableWidget")
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
 
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Results History"))

class History_results_show(QDialog):
    def __init__(self):
        super().__init__()
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.hist_data=Results_history
        
        
        self.addcontent()
    
    def addcontent(self):
        row=0

        for tup in self.hist_data:
            col=0
            for item in tup:
                oneitem=QTableWidgetItem(str(item))
                
                oneitem.setFont(QFont('Times', 8))
                
                oneitem.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.ui.tableWidget.setItem(row,col,oneitem)
                col+=1
            row+=1


def crt_folder(path):
    #check whether the directory exists or not
    #exist：True
    #not：False
    folder = os.path.exists(path)
 
    #result of check
    if not folder:
        #if not exist
        os.makedirs(path)

class Ui_IFTool(object):
    def setupUi(self, IFTool):
        IFTool.setObjectName("IFTool")
        IFTool.resize(800, 653)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(IFTool.sizePolicy().hasHeightForWidth())
        IFTool.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(IFTool)
        self.centralwidget.setObjectName("centralwidget")
        self.DatabaseConnect = QtWidgets.QGroupBox(self.centralwidget)
        self.DatabaseConnect.setGeometry(QtCore.QRect(10, 330, 220, 220))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DatabaseConnect.sizePolicy().hasHeightForWidth())
        self.DatabaseConnect.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.DatabaseConnect.setFont(font)
        self.DatabaseConnect.setMouseTracking(False)
        self.DatabaseConnect.setObjectName("DatabaseConnect")
        self.label = QtWidgets.QLabel(self.DatabaseConnect)
        self.label.setGeometry(QtCore.QRect(20, 20, 71, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self.DatabaseConnect)
        self.lineEdit.setGeometry(QtCore.QRect(20, 45, 180, 25))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.textChanged.connect(self.Button2Action)
        
        self.label_2 = QtWidgets.QLabel(self.DatabaseConnect)
        self.label_2.setGeometry(QtCore.QRect(20, 120, 91, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.DatabaseConnect)
        self.label_3.setGeometry(QtCore.QRect(20, 70, 91, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        
        self.pushButton = QtWidgets.QPushButton(self.DatabaseConnect)
        self.pushButton.setGeometry(QtCore.QRect(70, 190, 80, 25))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setStyleSheet('''QPushButton{background:#F5F5DC;}''')
        self.pushButton.pressed.connect(self.Button2Action)
        
        self.lineEdit_2 = QtWidgets.QLineEdit(self.DatabaseConnect)
        self.lineEdit_2.setGeometry(QtCore.QRect(20, 95, 180, 25))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.textChanged.connect(self.Button2Action)
        
        self.lineEdit_3 = QtWidgets.QLineEdit(self.DatabaseConnect)
        self.lineEdit_3.setGeometry(QtCore.QRect(20, 145, 180, 25))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_3.textChanged.connect(self.Button2Action)
        
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 100, 780, 220))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(40, 60, 720, 50))
        self.label_4.setPixmap(QtGui.QPixmap(Path_image + "Distribution.png"))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        
        self.label_25 = QtWidgets.QLabel(self.groupBox)
        self.label_25.setGeometry(QtCore.QRect(330, 30, 120, 16))
        self.label_25.setScaledContents(True)
        self.label_25.setObjectName("label_25")
        
        self.label_26 = QtWidgets.QLabel(self.groupBox)
        self.label_26.setGeometry(QtCore.QRect(460, 30, 150, 16))
        self.label_26.setScaledContents(True)
        self.label_26.setObjectName("label_26")
        
        self.label_27 = QtWidgets.QLabel(self.groupBox)
        self.label_27.setGeometry(QtCore.QRect(610, 30, 120, 16))
        self.label_27.setScaledContents(True)
        self.label_27.setObjectName("label_27")

        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit_4.setGeometry(QtCore.QRect(350, 115, 100, 20))
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.lineEdit_4.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_4.setPlaceholderText("Tunnel length")
        self.lineEdit_4.setStyleSheet('''background:#DCDCDC;border-with:0;border-style:outset''')
        
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(20, 30, 291, 16))
        self.label_5.setObjectName("label_5")
        
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(20, 135, 300, 15))
        self.label_7.setObjectName("label_7")
        
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(35, 160, 725, 55))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName("label_6")
        self.label_6.setPixmap(QtGui.QPixmap(Path_image + "Sensor.png"))
        
        
        self.DatabaseConnect_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.DatabaseConnect_2.setGeometry(QtCore.QRect(240, 330, 550, 220))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DatabaseConnect_2.sizePolicy().hasHeightForWidth())
        self.DatabaseConnect_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.DatabaseConnect_2.setFont(font)
        self.DatabaseConnect_2.setMouseTracking(False)
        self.DatabaseConnect_2.setObjectName("DatabaseConnect_2")
        self.label_8 = QtWidgets.QLabel(self.DatabaseConnect_2)
        self.label_8.setGeometry(QtCore.QRect(10, 30, 141, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        
        self.pushButton_2 = QtWidgets.QPushButton(self.DatabaseConnect_2)
        self.pushButton_2.setGeometry(QtCore.QRect(30, 190, 80, 25))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setStyleSheet('''QPushButton{background:#F5F5DC;}''')
        self.pushButton_2.pressed.connect(self.Button2Action)
        
        self.pushButton_3 = QtWidgets.QPushButton(self.DatabaseConnect_2)
        self.pushButton_3.setGeometry(QtCore.QRect(140, 190, 80, 25))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setStyleSheet('''QPushButton{background:#F5F5DC;}''')
        self.pushButton_3.pressed.connect(self.Button2Action)
        
        self.pushButton_4 = QtWidgets.QPushButton(self.DatabaseConnect_2)
        self.pushButton_4.setGeometry(QtCore.QRect(319, 190, 91, 25))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setStyleSheet('''QPushButton{background:#F5F5DC;}''')
        self.pushButton_4.pressed.connect(self.Button2Action)
        self.pushButton_5 = QtWidgets.QPushButton(self.DatabaseConnect_2)
        self.pushButton_5.setGeometry(QtCore.QRect(440, 190, 80, 25))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setStyleSheet('''QPushButton{background:#F5F5DC;}''')
        self.pushButton_5.pressed.connect(self.Button2Action)
        
        self.spinBox = QtWidgets.QSpinBox(self.DatabaseConnect_2)
        self.spinBox.setGeometry(QtCore.QRect(170, 30, 40, 25))
        self.spinBox.setMaximum(120)
        self.spinBox.setSingleStep(1)
        self.spinBox.setProperty("value", 1)
        self.spinBox.setObjectName("spinBox")
        self.spinBox.valueChanged.connect(self.Button2Action)
        
        self.groupBox_3 = QtWidgets.QGroupBox(self.DatabaseConnect_2)
        self.groupBox_3.setGeometry(QtCore.QRect(260, 30, 280, 140))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.label_13 = QtWidgets.QLabel(self.groupBox_3)
        self.label_13.setGeometry(QtCore.QRect(10, 20, 150, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.comboBox = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox.setGeometry(QtCore.QRect(160, 20, 115, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.comboBox.setFont(font)
        self.comboBox.setToolTip("")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.label_14 = QtWidgets.QLabel(self.groupBox_3)
        self.label_14.setGeometry(QtCore.QRect(10, 50, 130, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        
        self.spinBox_2 = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBox_2.setGeometry(QtCore.QRect(160, 50, 115, 25))
        self.spinBox_2.setMaximum(1000)
        self.spinBox_2.setSingleStep(10)
        self.spinBox_2.setProperty("value", 200)
        self.spinBox_2.setObjectName("spinBox_2")
        self.spinBox_2.valueChanged.connect(self.Button2Action)
        
        self.label_15 = QtWidgets.QLabel(self.groupBox_3)
        self.label_15.setGeometry(QtCore.QRect(10, 80, 130, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.spinBox_3 = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBox_3.setGeometry(QtCore.QRect(160, 110, 115, 25))
        self.spinBox_3.setMaximum(3000)
        self.spinBox_3.setSingleStep(100)
        self.spinBox_3.setProperty("value", 1500)
        self.spinBox_3.setObjectName("spinBox_3")
        self.label_16 = QtWidgets.QLabel(self.groupBox_3)
        self.label_16.setGeometry(QtCore.QRect(10, 110, 130, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.spinBox_4 = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBox_4.setGeometry(QtCore.QRect(160, 80, 115, 25))
        self.spinBox_4.setMaximum(30)
        self.spinBox_4.setSingleStep(1)
        self.spinBox_4.setProperty("value", 10)
        self.spinBox_4.setObjectName("spinBox_4")
        self.groupBox_4 = QtWidgets.QGroupBox(self.DatabaseConnect_2)
        self.groupBox_4.setGeometry(QtCore.QRect(0, 60, 241, 110))
        self.groupBox_4.setObjectName("groupBox_4")
        self.label_21 = QtWidgets.QLabel(self.groupBox_4)
        self.label_21.setGeometry(QtCore.QRect(10, 20, 130, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_21.setFont(font)
        self.label_21.setObjectName("label_21")
        self.spinBox_5 = QtWidgets.QSpinBox(self.groupBox_4)
        self.spinBox_5.setGeometry(QtCore.QRect(159, 20, 61, 25))
        self.spinBox_5.setMaximum(1000)
        self.spinBox_5.setSingleStep(10)
        self.spinBox_5.setProperty("value", 200)
        self.spinBox_5.setDisplayIntegerBase(10)
        self.spinBox_5.setObjectName("spinBox_5")
        self.label_22 = QtWidgets.QLabel(self.groupBox_4)
        self.label_22.setGeometry(QtCore.QRect(10, 50, 130, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_22.setFont(font)
        self.label_22.setObjectName("label_22")
        
        self.doubleSpinBox_6 = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_6.setGeometry(QtCore.QRect(159, 80, 61, 25))
        self.doubleSpinBox_6.setDecimals(1)
        self.doubleSpinBox_6.setMaximum(10.0)
        self.doubleSpinBox_6.setSingleStep(0.1)
        self.doubleSpinBox_6.setProperty("value", 1.5)
        self.doubleSpinBox_6.setObjectName("doubleSpinBox_6")
        self.doubleSpinBox_6.valueChanged.connect(self.Button2Action)
        
        self.label_23 = QtWidgets.QLabel(self.groupBox_4)
        self.label_23.setGeometry(QtCore.QRect(10, 80, 130, 25))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_23.setFont(font)
        self.label_23.setObjectName("label_23")
        self.spinBox_7 = QtWidgets.QSpinBox(self.groupBox_4)
        self.spinBox_7.setGeometry(QtCore.QRect(159, 50, 61, 25))
        self.spinBox_7.setMaximum(30)
        self.spinBox_7.setSingleStep(1)
        self.spinBox_7.setProperty("value", 10)
        self.spinBox_7.setObjectName("spinBox_7")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(10, -1, 721, 91))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.pushButton_6 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_6.setGeometry(QtCore.QRect(70, 50, 60, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setStyleSheet('''QPushButton{background:#AFEEEE;border-style: outset;border-radius: 10px;}''')
        self.pushButton_7 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_7.setGeometry(QtCore.QRect(170, 50, 60, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_7.setFont(font)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.setStyleSheet('''QPushButton{background:#AFEEEE;border-style: outset;border-radius: 10px;}''')
        self.pushButton_8 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_8.setGeometry(QtCore.QRect(270, 50, 60, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_8.setFont(font)
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_8.setStyleSheet('''QPushButton{background:#AFEEEE;border-style: outset;border-radius: 10px;}''')
        self.pushButton_9 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_9.setGeometry(QtCore.QRect(370, 50, 60, 30))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton_9.setFont(font)
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_9.setStyleSheet('''QPushButton{background:#AFEEEE;border-style: outset;border-radius: 10px;}''')
        self.label_17 = QtWidgets.QLabel(self.groupBox_2)
        self.label_17.setGeometry(QtCore.QRect(75, 20, 60, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.label_18 = QtWidgets.QLabel(self.groupBox_2)
        self.label_18.setGeometry(QtCore.QRect(175, 20, 60, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.label_19 = QtWidgets.QLabel(self.groupBox_2)
        self.label_19.setGeometry(QtCore.QRect(270, 20, 71, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.label_20 = QtWidgets.QLabel(self.groupBox_2)
        self.label_20.setGeometry(QtCore.QRect(385, 20, 30, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_20.setFont(font)
        self.label_20.setObjectName("label_20")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(739, 0, 41, 41))
        self.label_10.setText("")
        self.label_10.setPixmap(QtGui.QPixmap(Path_image + "PolyU.png"))
        self.label_10.setScaledContents(True)
        self.label_10.setObjectName("label_10")
        self.groupBox_5 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_5.setGeometry(QtCore.QRect(10, 550, 780, 80))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.groupBox_5.setFont(font)
        self.groupBox_5.setObjectName("groupBox_5")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.groupBox_5)
        self.plainTextEdit.setGeometry(QtCore.QRect(20, 30, 740, 40))
        self.plainTextEdit.setObjectName("plainTextEdit")
        IFTool.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(IFTool)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        IFTool.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(IFTool)
        self.statusbar.setObjectName("statusbar")
        IFTool.setStatusBar(self.statusbar)
        
        # display the text on the setted widgets
        self.retranslateUi(IFTool)
        self.Flag_Start_Pause = 0
        self.a = 0
        
        QtCore.QMetaObject.connectSlotsByName(IFTool)
        QApplication.processEvents()
        
        self.lineEdit_4.setText('')
    
    def retranslateUi(self, IFTool):
        _translate = QtCore.QCoreApplication.translate
        IFTool.setWindowTitle(_translate("IFTool", "SFSF"))
        self.DatabaseConnect.setTitle(_translate("IFTool", "Database Connection Zone"))
        self.label.setText(_translate("IFTool", "Server IP:"))
        self.lineEdit.setText(_translate("IFTool", "158.132.171.182"))
        self.label_3.setText(_translate("IFTool", "Username:"))
        self.lineEdit_2.setText(_translate("IFTool", "user1"))
        self.label_2.setText(_translate("IFTool", "Password:"))
        self.lineEdit_3.setText(_translate("IFTool", "StrongPassword123"))
        
        # pushButton is the connect
        self.pushButton.setText(_translate("IFTool", "Connect"))
        
        self.DatabaseConnect_2.setTitle(_translate("IFTool", "Calculation Input Zone"))
        self.label_8.setText(_translate("IFTool", "Refresh Interval (s):"))
        
        self.groupBox.setTitle(_translate("IFTool", "Display Area"))
        self.groupBox_4.setTitle(_translate("IFTool", "Criteria Settings"))
        self.label_21.setText(_translate("IFTool", "Max Temp. (C):"))
        self.label_22.setText(_translate("IFTool", "Max Visibility (m):"))
        self.label_23.setText(_translate("IFTool", "Max HRR (kW):"))        
        self.label_5.setText(_translate("IFTool", "Temperature/Visibility/CO Distribution"))
        self.label_7.setText(_translate("IFTool", "Sensor Temperaturs (0-1000 C)"))
        
        self.label_25.setText(_translate("IFTool", "Loc (m)"))        
        self.label_26.setText(_translate("IFTool", "HRR (kW)"))        
        self.label_27.setText(_translate("IFTool", "Vent (m/s)"))        
        
        # Start is connected to pushButton_2
        # Pause is connected to pushButton_3
        self.pushButton_2.setText(_translate("IFTool", "Start"))
        self.pushButton_3.setText(_translate("IFTool", "Pause"))
        
        
        self.groupBox_3.setTitle(_translate("IFTool", "Display Settings"))
        self.label_13.setText(_translate("IFTool", "Display Quantity:"))
        self.comboBox.setItemText(0, _translate("IFTool", "Temperature"))
        self.comboBox.setItemText(1, _translate("IFTool", "Visibility"))
        self.comboBox.setItemText(2, _translate("IFTool", "CO"))
        self.label_14.setText(_translate("IFTool", "Max Temp. (C):"))
        self.label_15.setText(_translate("IFTool", "Max Visibility (m):"))
        self.label_16.setText(_translate("IFTool", "Max CO (ppm):"))


        self.groupBox_2.setTitle(_translate("IFTool", "Warning Area"))
        self.pushButton_6.setText(_translate("IFTool", " Safe"))
        self.pushButton_7.setText(_translate("IFTool", "5 min"))
        self.pushButton_8.setText(_translate("IFTool", "5 min"))
        self.pushButton_9.setText(_translate("IFTool", "5 min"))
        self.label_17.setText(_translate("IFTool", "Overall"))
        self.label_18.setText(_translate("IFTool", "Temp."))
        self.label_19.setText(_translate("IFTool", "Visibility"))
        self.label_20.setText(_translate("IFTool", "CO"))
        
        # Print Results is connected to pushButton_4
        # Guide is connected to pushButton_5
        self.pushButton_4.setText(_translate("IFTool", "Print Results"))
        self.pushButton_5.setText(_translate("IFTool", "Manual"))
        
        self.groupBox_5.setTitle(_translate("IFTool", "Command Prompt Area"))
        
        # information shown on prompt area is connected to plainTextEdit
        self.plainTextEdit.setPlainText(_translate("IFTool", "Prompt message is shown here!\n" + "To use the system, Connect the server and then Start." ))
        
    def Button2Action(self):
        
        self.promp_text = ''
        
        # if the Connect button is pressed
        if self.pushButton.isDown():
            IP_address = self.lineEdit.text()
            User_name = self.lineEdit_2.text()
            Pass_word = self.lineEdit_3.text()
            try:
                self.mydb = mysql.connector.connect(host=IP_address,
                                              user=User_name,
                                               passwd=Pass_word,
                                               database='SureFire_Demo'
                                              )
                self.promp_text = 'Cloud database is connected!'
                self.update_prompt_area()
            except:
                self.promp_text = 'Cloud database is not connected! Check the Server IP, Username and Password.'
                self.update_prompt_area()
        
        # if the Start button is pressed
        if self.pushButton_2.isDown():
            
            
            self.refresh_time = self.spinBox.value()
            self.criteria_HRR = self.doubleSpinBox_6.value()
            self.Display_Temp = self.spinBox_2.value()
            self.promp_text = 'The system starts working.'
            self.update_prompt_area()
            self.specified_thread = threading.Thread(target=self.fetchdata, name='t')
            self.specified_thread.start()
        
        # if the Pause button is pressed
        if self.pushButton_3.isDown():
            self.promp_text = 'The system is paused.'
            self.update_prompt_area()
            self.Flag_Start_Pause = 0
        
        # if the Print Results button is pressed
        if self.pushButton_4.isDown():
            
            IP_address = self.lineEdit.text()
            User_name = self.lineEdit_2.text()
            Pass_word = self.lineEdit_3.text()
            self.mydb = mysql.connector.connect(host=IP_address,
                                          user=User_name,
                                          passwd=Pass_word,
                                          database='SureFire_Demo'
                                          )
            mycursor = self.mydb.cursor()
            mycursor.execute("SELECT * from Prediction_AI order by CurrentTime desc limit 1 ")
            query_Pred_AI = mycursor.fetchone()
            time_query = query_Pred_AI[1]
            
            query_AI_fetch = "SELECT * FROM Prediction_AI WHERE CurrentTime <= %s ORDER BY ABS(TIMEDIFF(CurrentTime, %s)) ASC LIMIT 60"
            query_sensor_fetch = "SELECT * FROM Temp_Sensor WHERE CurrentTime <= %s ORDER BY ABS(TIMEDIFF(CurrentTime, %s)) ASC LIMIT 60"
            
            mycursor.execute(query_AI_fetch, (time_query, time_query,))
            query_AI_data_tuple = mycursor.fetchmany(60)
            mycursor.execute(query_sensor_fetch, (time_query, time_query,))
            query_sensor_data_tuple = mycursor.fetchmany(60)
            
            query_AI_data = []
            for data in query_AI_data_tuple:
                query_AI_data.append(data[1:])
            query_AI_data = np.array(query_AI_data)
            query_sensor_data = []
            for data in query_sensor_data_tuple:
                query_sensor_data.append(data[2:])
            query_sensor_data = np.array(query_sensor_data)
            
            query_rows_display = min(query_sensor_data.shape[0], query_AI_data.shape[0])
            query_AI_data = query_AI_data[:query_rows_display]
            query_sensor_data = query_sensor_data[:query_rows_display]
            global Results_history
            Results_history = np.hstack((query_AI_data,query_sensor_data))
            self.ss = History_results_show()
            self.ss.show()
            
            mycursor.close()
            self.mydb.close()
            
        
        # if the Manual button is pressed
        if self.pushButton_5.isDown():
            self.manual_show = Manual_show()
            self.manual_show.show()
        
    
    def fetchdata(self):
        self.Flag_Start_Pause = 1
        while True:
            if self.Flag_Start_Pause == 1:
                IP_address = self.lineEdit.text()
                User_name = self.lineEdit_2.text()
                Pass_word = self.lineEdit_3.text()
                self.mydb = mysql.connector.connect(host=IP_address,
                                              user=User_name,
                                              passwd=Pass_word,
                                              database='SureFire_Demo'
                                              )
                mycursor = self.mydb.cursor()
                
                # get the time of the latest data
                mycursor.execute("SELECT * from Prediction_AI order by CurrentTime desc limit 1 ")
                Fetch_Pred_AI = mycursor.fetchone()
                time_row = Fetch_Pred_AI[1]
                
                # fetch the measured sensor data
                query = "SELECT * FROM Temp_Sensor WHERE CurrentTime <= %s ORDER BY ABS(TIMEDIFF(CurrentTime, %s)) ASC LIMIT 1"
                mycursor.execute(query, (time_row, time_row,))
                self.Temp_meas = mycursor.fetchone()
                self.Temp_meas = list(self.Temp_meas[2:])
                
                # save the image of the sensor data
                plt.clf()
                plt.figure(figsize = (30,2))
                ax = plt.subplot(111)
                plt.plot(np.arange(0.1,1.7,0.1),self.Temp_meas, marker ='o', markersize=15, color = 'r')
                xmajorLocator = MultipleLocator(0.1)
                ymajorLocator = MultipleLocator(1000)
                plt.xlim(0, 1.7)
                plt.ylim(0, 1000)
                # set the axes
                ax.xaxis.set_major_locator(xmajorLocator)
                ax.yaxis.set_major_locator(ymajorLocator)
                frame = plt.gca()
                frame.axes.get_yaxis().set_visible(False)
                frame.axes.get_xaxis().set_visible(False)
                plt.savefig(Path_image + "Sensor.png",bbox_inches='tight')
                
                self.label_6.setPixmap(QtGui.QPixmap(Path_image + "Sensor.png"))
                
                # fetch image
                Loc, HRR, Vent = np.round(Fetch_Pred_AI[2],2), np.round(Fetch_Pred_AI[3],2), np.round(Fetch_Pred_AI[4],2)
                loc_match = round(Fire_Loc[(np.abs(Fire_Loc - Loc)).argmin()],3)
                HRR_match = round(H_RR[(np.abs(H_RR - HRR)).argmin()],3)
                Vent_match = round(Wind_Spe[(np.abs(Wind_Spe - Vent)).argmin()],3)
                query = 'SELECT * FROM ' + 'Stored_Scenario' + ' WHERE (round(Location,3),round(HRR,3), round(Ventilation,3))  = ( %s, %s, %s)'
                mycursor.execute(query, (str(loc_match),str(HRR_match),str(Vent_match),))
                # get the image in format of bytes
                img_fetch = mycursor.fetchone()[4]
                
                # convert bytes to bytes stream
                img_bytestream = BytesIO(img_fetch)
                # convert bytes stream to image
                img_show = Image.open(img_bytestream)
                Img_grey = np.array(img_show, dtype = 'f')
                Img_grey = Img_grey * 255.0 / self.Display_Temp
                Img_grey[Img_grey > self.Display_Temp] = 255
                Img_rgb = cv2.applyColorMap(255-Img_grey.astype(np.uint8), cv2.COLORMAP_JET)
                # save the image of the temperature/smoke/CO distribution
                matplotlib.image.imsave(Path_image + "Distribution.png",Img_rgb)
                
                if max(self.Temp_meas) <= 100:
                     self.label_4.setStyleSheet("background-color: White ")
                     self.label_4.setPixmap(QtGui.QPixmap(""))
                     self.label_25.setText('Loc is ' + str(Loc,) + ' m')
                     self.label_26.setText('HRR is ' + str(0) + ' kW')
                     self.label_27.setText('Vent is ' + str(Vent) + ' m/s')
                elif max(self.Temp_meas) > 100:
                    self.label_4.setPixmap(QtGui.QPixmap(Path_image + "Distribution.png"))
                    self.label_25.setText('Loc is ' + str(Loc) + ' m')
                    self.label_26.setText('HRR is ' + str(HRR) + ' kW')
                    self.label_27.setText('Vent is ' + str(Vent) + ' m/s')
                
                plt.close("all")
                
                # show the values of the fire scenarios

                
                # change the color of the button in warning area
                if HRR >= self.criteria_HRR:
                    self.pushButton_6.setStyleSheet('''QPushButton{background:#F08080;border-style: outset;border-radius: 10px;}''')
                    self.pushButton_6.setText(" Danger")
                elif HRR < self.criteria_HRR:
                    self.pushButton_6.setStyleSheet('''QPushButton{background:#AFEEEE;border-style: outset;border-radius: 10px;}''')
                    self.pushButton_6.setText(" Safe")
                
                
                time.sleep(self.refresh_time)
            
            
            else:
                mycursor = self.mydb.cursor()
                break
            
    def update_prompt_area(self):
        self.plainTextEdit.setPlainText(self.promp_text)


if __name__ == "__main__":
    Path_image = 'C:\\IFAST\\'
    crt_folder(Path_image)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    Fire_Loc = np.arange(0.1,1.7,0.1)
    H_RR = np.array([0.674, 1.225, 1.545, 2.453, 4.412])
    Wind_Spe = np.array([0.0,  -0.2, -0.4, 0.2, 0.4])
    app = QtWidgets.QApplication(sys.argv)
    IFTool = QtWidgets.QMainWindow()
    ui = Ui_IFTool()
    ui.setupUi(IFTool)
    IFTool.show()
    sys.exit(app.exec_())