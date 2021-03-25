import sys, os
import platform,subprocess,glob

from datetime import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom

from functools import partial

from PyQt5.QtGui 					  import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFileDialog
from PyQt5.QtWebEngineWidgets         import QWebEngineView
from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem



#from analysis_scripts			import *
from lookAndFeel  				import *
from gmail_visoar				import *

from pathlib import Path
from datetime import datetime
import os.path
from os import path

DEBUG = True


class EditUserLibraryWindow(QDialog):
    def __init__(self, userFileHistory, parent):
        super(EditUserLibraryWindow, self).__init__( parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.userFileHistory = userFileHistory
        self.DEBUG = True
        self.setStyleSheet(LOOK_AND_FEEL)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(GRID_SPACING)

        self.layout1 = QHBoxLayout()
        self.inputOldDirLabel = QLabel("Old Directory", self)
        self.oldPathLineEdit = QLineEdit(self)
        self.oldPathLineEdit.resize(180,40)
        self.oldPathLineEdit.setStyleSheet("padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
        self.btnOldDir = QPushButton(". . .")
        self.btnOldDir.clicked.connect(self.setOldLibrary)
        self.btnOldDir.setStyleSheet(GREEN_PUSH_BUTTON)
        self.layout1.addWidget(self.inputOldDirLabel)
        self.layout1.addWidget(self.oldPathLineEdit)
        self.layout1.addWidget(self.btnOldDir)

        self.layout2 = QHBoxLayout()
        self.inputNewDirLabel = QLabel("New Directory", self)
        self.newPathLineEdit = QLineEdit(self)
        self.newPathLineEdit.resize(180,40)
        self.newPathLineEdit.setStyleSheet("padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
        self.btnNewDir = QPushButton(". . .")
        self.btnNewDir.clicked.connect(self.setNewLibrary)
        self.btnNewDir.setStyleSheet(GREEN_PUSH_BUTTON)
        self.layout2.addWidget(self.inputNewDirLabel)
        self.layout2.addWidget(self.newPathLineEdit)
        self.layout2.addWidget(self.btnNewDir)

        self.btnChangeDir = QPushButton("Change Directory")
        self.btnChangeDir.clicked.connect(self.changeDirectory)
        self.btnChangeDir.setStyleSheet(WHITE_PUSH_BUTTON)
        self.layout.addLayout(self.layout1)
        self.layout.addLayout(self.layout2)
        self.layout.addWidget(self.btnChangeDir, alignment=Qt.AlignLeft)

        self.setLayout(self.layout)
        self.setGeometry(200, 200, 600, 250)

    def setOldLibrary(self):
        #'Select Old Directory'
        dir = str(QFileDialog.getExistingDirectory(self, "Select Old Directory"))
        self.oldPathLineEdit.setText(dir)
        return dir

    def setNewLibrary(self):
        #'Select Old Directory'
        dir = str(QFileDialog.getExistingDirectory(self, "Select New Directory"))
        self.newPathLineEdit.setText(dir)
        return dir

    def changeDirectory(self):
        olddir =self.oldPathLineEdit.text()
        newdir =self.newPathLineEdit.text()

        ret = self.parent.parent.visoarUserLibraryData.changeDirectoryAllProjects(olddir,newdir)
        if ret:
            self.close()
            msg = QMessageBox()
            msg.setWindowTitle('Saved User Library')
            msg.setText('Saved backup of UserLibrary and updated Current.')
            msg.setStyleSheet(POPUP_LOOK_AND_FEEL)
            x = msg.exec_()

        if self.DEBUG:
            print('LoadFromFile finished')



class EditUserLibraryItemWindow(QDialog):
    def __init__(self, userFileHistory, projName, projDir, parent):
        super(EditUserLibraryItemWindow, self).__init__( parent)
        self.parent = parent
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.userFileHistory = userFileHistory
        self.projName = projName
        self.projDir = projDir
        print('EditUserLibraryItemWindow {0} {1} {2}'.format(self.userFileHistory, self.projName, self.projDir))
        self.DEBUG = True
        self.setStyleSheet(LOOK_AND_FEEL)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(GRID_SPACING)

        self.layout1 = QHBoxLayout()
        self.inputNameLabel = QLabel("Project Name", self)
        self.nameLineEdit = QLineEdit(self)
        self.nameLineEdit.setText(self.projName)
        self.nameLineEdit.resize(180,40)
        self.nameLineEdit.setStyleSheet("padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
#         self.btnOldDir = QPushButton(". . .")
#         self.btnOldDir.clicked.connect(self.setOldLibrary)
#         self.btnOldDir.setStyleSheet(GREEN_PUSH_BUTTON)
        self.layout1.addWidget(self.inputNameLabel)
        self.layout1.addWidget(self.nameLineEdit)
#         self.layout1.addWidget(self.btnOldDir)

        self.layout2 = QHBoxLayout()
        self.inputDirLabel = QLabel("Project Directory", self)
        self.dirLineEdit = QLineEdit(self)
        self.dirLineEdit.setText(self.projDir)
        self.dirLineEdit.resize(180,40)
        self.dirLineEdit.setStyleSheet("padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
        self.btnNewDir = QPushButton(". . .")
        self.btnNewDir.clicked.connect(self.setNewDir)
        self.btnNewDir.setStyleSheet(GREEN_PUSH_BUTTON)
        self.layout2.addWidget(self.inputDirLabel)
        self.layout2.addWidget(self.dirLineEdit)
        self.layout2.addWidget(self.btnNewDir)

        self.btnChangeDir = QPushButton("Change Project")
        self.btnChangeDir.clicked.connect(self.changeDirectory)
        self.btnChangeDir.setStyleSheet(WHITE_PUSH_BUTTON)
        self.layout.addLayout(self.layout1)
        self.layout.addLayout(self.layout2)
        self.layout.addWidget(self.btnChangeDir, alignment=Qt.AlignLeft)

        self.setLayout(self.layout)
        self.setGeometry(200, 200, 600, 250)

    def setNewDir(self):
        #'Select Old Directory'
        dir = str(QFileDialog.getExistingDirectory(self, "Select New Directory"))
        self.dirLineEdit.setText(dir)
        return dir

    def changeDirectory(self):
        olddir =self.projDir
        newdir =self.dirLineEdit.text()
        oldName =self.projName
        newName =self.nameLineEdit.text()
        ret = self.parent.parent.visoarUserLibraryData.changeDirectoryForAProject(olddir, newdir, oldName, newName)
        if ret:
            self.parent.parent.loadWidgetDict[newName] = self.parent.parent.loadWidgetDict[oldName]
            self.parent.parent.loadLabelsWidgetDict[newName] = self.parent.parent.loadLabelsWidgetDict[oldName]
            self.parent.refreshLoadButtonWidgetWithName(oldName,newName)
            self.parent.parent.visoarUserLibraryData.refreshProjectsFromXML()

            self.close()
            msg = QMessageBox()
            msg.setWindowTitle('Saved User Library')
            msg.setText('Saved backup of UserLibrary and updated Current.')
            msg.setStyleSheet(POPUP_LOOK_AND_FEEL)
            x = msg.exec_()

        if self.DEBUG:
            print('LoadFromFile finished')