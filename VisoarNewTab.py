from VisoarSettings             import *
from datetime import datetime

from PyQt5.QtWebEngineWidgets         import QWebEngineView

from OpenVisus                        import *
from OpenVisus.gui                    import *

from PyQt5.QtGui 					  import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFileDialog

from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem


import xml.etree.ElementTree as ET
import xml.dom.minidom
from selectBestMatch import *


def addLogo(app_dir):
    logo = QPushButton('')
    logo.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
    ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
    logo.setIcon(QIcon(os.path.join(app_dir, 'icons', 'visoar_logo.png')))
    logo.setIconSize(QSize(480, 214))
    return logo

class VisoarSlamSettingsDefault(QDialog):
    def __init__(self, parent):
        super(VisoarSlamSettingsDefault, self).__init__( parent)
        self.setStyleSheet(LOOK_AND_FEEL)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowStaysOnTopHint)  # set always on top flag, makes window disappear

        self.parent = parent
        self.layout = QVBoxLayout()
        self.layout.setSpacing(GRID_SPACING)

        self.generate_bbox = False
        self.color_matching = False
        self.blending_exp = "output=voronoi()"

        self.bbox_switch = QCheckBox("Generate BBox")
        self.bbox_switch.stateChanged.connect(lambda: self.flipGenerateBBOX(self.bbox_switch))
        #self.bboxLabel = QLabel('Generate BBox')
        #self.bbox_switch = MySwitch()
        self.bbox_switch.setChecked(False)
        self.bbox_switch.setStyleSheet(QCHECKBOX_LOOK_AND_FEEL)
        #self.bbox_switch.clicked.connect(self.flipGenerateBBOX)

        self.cmatch_switch = QCheckBox("Color Matching Preprocess")
        self.cmatch_switch.stateChanged.connect(lambda: self.flipColorMatch(self.cmatch_switch))
        #        self.cmatchLabel = QLabel('Color Matching Preprocess')
        #self.cmatch_switch = MySwitch()
        self.cmatch_switch .setChecked(False)
        self.cmatch_switch.setStyleSheet(QCHECKBOX_LOOK_AND_FEEL)
        #self.cmatch_switch .clicked.connect(self.flipColorMatch)

        self.blendingPythonTextEdit = QTextEdit(self)
        self.blendingPythonTextEdit.setText(self.blending_exp)
        self.blendingPythonTextEdit.resize(480, 440)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.blendingPythonTextEdit.sizePolicy().hasHeightForWidth())
        # self.pythontextbox.setSizePolicy(sizePolicy)
        self.blendingPythonTextEdit.setStyleSheet(MY_SCROLL_LOOK)

        self.closebutton = QPushButton()
        self.closebutton.clicked.connect(self.close)
        self.closebutton.setIcon(QIcon('icons/Close.png'))
        self.closebutton.setStyleSheet("""background-color: #045951;""")
        self.closebutton.setIconSize(QSize(30, 30))
        self.closebutton.resize(40, 40)
        self.closebutton.setFixedSize(50, 50)

        #self.layout.addWidget(self.bboxLabel)
        self.layout.addWidget(self.bbox_switch )
        #self.layout.addWidget(self.cmatchLabel)
        self.layout.addWidget(self.cmatch_switch)
        self.layout.addWidget(self.blendingPythonTextEdit)
        self.layout.addWidget(self.closebutton)

        self.setLayout(self.layout)
        self.setGeometry(300, 300, 440, 900)


    def  flipGenerateBBOX(self, btn):
        self.generate_bbox = not self.generate_bbox
        self.bbox_switch.setChecked( self.generate_bbox)
        print('Flipped BBOX: {0}'.format(self.generate_bbox))

    def flipColorMatch(self,btn):
        self.color_matching = not self.color_matching
        self.cmatch_switch.setChecked(self.color_matching)
        print('Flipped color_matching: {0}'.format(self.color_matching))

    def close(self):
        self.updateSlamSettings(generate_bbox=self.generate_bbox,
            color_matching=self.color_matching ,
            blending_exp=self.blendingPythonTextEdit.toPlainText().strip())
        self.on_close()

    def on_close(self):
        self.hide()
        self.update()

    def on_show(self):
        self.show()
        self.raise_()
        self.activateWindow()

class VisoarAskSensor(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.DEBUG = True
        self.setStyleSheet(LOOK_AND_FEEL)
        class Buttons:
            pass
        self.buttons = Buttons

        self.sublayout = QVBoxLayout()
        self.sublayout.addWidget(addLogo(self.parent.app_dir))

        self.inputModeNewTabLabel = QLabel("Sensor:", self)

        self.comboBoxNewTab = QComboBox(self)
        self.comboBoxNewTab.addItem("R G B")
        self.comboBoxNewTab.addItem("O C NIR (MapIR)")
        self.comboBoxNewTab.addItem("Agrocam")
        self.comboBoxNewTab.addItem("R G NIR")
        self.comboBoxNewTab.addItem("R NIR (Sentera NDVI)")
        self.comboBoxNewTab.addItem("RedEdge NIR (Sentera NDRE)")
        self.comboBoxNewTab.setStyleSheet(MY_COMBOX)
        self.comboBoxNewTab.currentIndexChanged.connect(lambda: self.parent.setSensor(self.comboBoxNewTab.currentText()))
        self.comboBoxNewTab.setFixedSize(100, 40)
        self.comboBoxNewTab.resize(100, 40)
        self.comboBoxNewTab.setFixedWidth(100)
        self.comboBoxNewTab.setFixedHeight(40)
        width = self.comboBoxNewTab.minimumSizeHint().width()
        self.comboBoxNewTab.setMinimumWidth(width)

        self.comboBoxNewTab.setToolTip('Set sensor/image input format')
        self.sublayoutForm = QFormLayout()
        self.sublayout.addStretch(True)

        self.sublayoutForm.addRow(self.inputModeNewTabLabel, self.comboBoxNewTab)

        self.sublayout.addLayout(self.sublayoutForm)

        self.buttons.home = QPushButton('', self)
        self.buttons.home.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.home.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'home.png')))
        self.buttons.home.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.home.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        #self.sublayout.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        self.buttons.home.clicked.connect(self.parent.goHome)

        self.buttons.nextBtn = QPushButton('Next', self)
        self.buttons.nextBtn.resize(180, 80)
        self.buttons.nextBtn.setStyleSheet(GREEN_PUSH_BUTTON)
        #self.buttons.nextBtn.hide()
        # connect button to function on_click
        self.buttons.nextBtn.clicked.connect(lambda: self.parent.next("AfterAskSensor"))

        self.sublayoutLastRow = QHBoxLayout()
        self.sublayoutLastRow.addWidget(self.buttons.home, alignment=Qt.AlignRight)
        self.sublayoutLastRow.addStretch(20)
        self.sublayoutLastRow.addWidget(self.buttons.nextBtn, alignment=Qt.AlignLeft)
        self.sublayout.addStretch(True)
        self.sublayout.addLayout(self.sublayoutLastRow)


        self.setLayout(self.sublayout)


class VisoarAskSource(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.DEBUG = True
        self.setStyleSheet(LOOK_AND_FEEL)
        class Buttons:
            pass

        self.buttons = Buttons

        self.sublayout = QVBoxLayout()
        self.sublayout.addWidget(addLogo(self.parent.app_dir))
        self.sublayout.addStretch(True)

        self.buttonAddImagesSource = QPushButton('Add Images', self)
        self.buttonAddImagesSource.resize(180, 40)
        self.buttonAddImagesSource.clicked.connect(self.parent.addImages)
        self.buttonAddImagesSource.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttonAddImagesSource.setToolTip('Specify directory of image for stitching')


        # Ability to change location
        #self.parent.projectInfo.projDir = ''  # os.getcwd()
        #self.parent.projectInfo.srcDir = ''  # os.getcwd()
        self.curDir = QLabel('Image Directory: ')
        self.curDir2 = QLabel(self.parent.projectInfo.projDir)
        self.curDir2.setStyleSheet("""font-family: Roboto;font-style: normal;font-size: 14pt; padding:20px """)
        self.curDir.resize(280, 40)


        self.sublayoutFormInputDir = QHBoxLayout()


        self.sublayoutFormInputDir.addWidget(self.curDir)
        self.sublayoutFormInputDir.addWidget(self.curDir2)
        self.sublayoutFormInputDir.addWidget(  self.buttonAddImagesSource)

        self.sublayoutFormInputDir.addStretch(True)

        self.createErrorLabel = QLabel('*')
        self.createErrorLabel.setStyleSheet("""color: #59040c""")
        self.sublayoutFormInputDir.addWidget(self.createErrorLabel)

        self.sublayout.addLayout(self.sublayoutFormInputDir)


        self.buttons.home = QPushButton('', self)
        self.buttons.home.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.home.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'home.png')))
        self.buttons.home.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.home.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.home.clicked.connect(self.parent.goHome)
        self.buttons.home.setToolTip('Return to home screen')

        #self.sublayout.addWidget(self.buttons.home, alignment=Qt.AlignLeft)

        self.buttons.nextBtn = QPushButton('Next', self)
        self.buttons.nextBtn.resize(180, 80)
        self.buttons.nextBtn.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttons.nextBtn.hide()
        # connect button to function on_click
        self.buttons.nextBtn.clicked.connect(lambda: self.parent.next("AfterAskSource"))

        self.sublayoutLastRow = QHBoxLayout()
        self.sublayoutLastRow.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        self.sublayoutLastRow.addStretch(100)
        self.sublayoutLastRow.addWidget(self.buttons.nextBtn, alignment=Qt.AlignRight)
        self.sublayout.addStretch(True)
        self.sublayout.addLayout(self.sublayoutLastRow)

        self.setLayout(self.sublayout)


class VisoarAskSourceRGBNDVI(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.DEBUG = True

        self.OPT_FOR_ACCEPT_ALL = True

        self.setStyleSheet(LOOK_AND_FEEL)
        class Buttons:
            pass

        self.buttons = Buttons

        self.sublayout = QVBoxLayout()
        self.sublayout.addWidget(addLogo(self.parent.app_dir))
        self.sublayout.addStretch(True)

        # Ability to change location
        self.parent.projectInfo.projDir = ''  # os.getcwd()
        self.parent.projectInfo.srcDir = ''  # os.getcwd()
        self.curDir = QLabel('RGB Image Directory: ')

        self.curDir2 = QLabel(self.parent.projectInfo.srcDir)
        #self.curDir2.setText('/Volumes/ViSUSAg/smallRGB/')
        self.curDir2.setStyleSheet("""font-family: Roboto;font-style: normal;font-size: 14pt; padding:20px """)
        self.curDir.resize(280, 40)
        self.buttons.btnSetRGBDir = QPushButton("")
        self.buttons.btnSetRGBDir.clicked.connect(self.setRGBInputDirectoryUI)
        #self.buttons.btnSetRGBDir.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttons.btnSetRGBDir.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        self.buttons.btnSetRGBDir.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'Edit_green.png')))
        self.buttons.btnSetRGBDir.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.btnSetRGBDir.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)

        # if self.parent.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam':
            # Ability to change location
            #self.parent.projectInfo.projDir = ''  # os.getcwd()
            #self.parent.projectInfo.srcDir = ''  # os.getcwd()
        self.curDirNDVI = QLabel('NDVI Image Directory: ')

        self.curDir2NDVI = QLabel(self.parent.projectInfo.srcDirNDVI)
        self.curDir2NDVI.setStyleSheet("""font-family: Roboto;font-style: normal;font-size: 14pt; padding:20px """)
        self.curDirNDVI.resize(280, 40)
        #self.curDir2NDVI.setText('/Volumes/ViSUSAg/smallNDVI/')
        self.buttons.btnSetNDVIDir = QPushButton("")
        self.buttons.btnSetNDVIDir.clicked.connect(self.setNDVIInputDirectoryUI)
        self.buttons.btnSetNDVIDir.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        self.buttons.btnSetNDVIDir.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'Edit_green.png')))
        self.buttons.btnSetNDVIDir.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.btnSetNDVIDir.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)

        self.sublayoutFormInputDir = QHBoxLayout()
        self.sublayoutFormInputDir.addWidget(self.curDir)
        self.sublayoutFormInputDir.addWidget(self.curDir2)
        self.sublayoutFormInputDir.addWidget(self.buttons.btnSetRGBDir)
        self.sublayoutFormInputDir.addStretch(True)

        self.createErrorLabel = QLabel('*')
        self.createErrorLabel.setStyleSheet("""color: #59040c""")
        self.sublayoutFormInputDir.addWidget(self.createErrorLabel)

        self.sublayoutFormNDVIInputDir = QHBoxLayout()
        self.sublayoutFormNDVIInputDir.addWidget(self.curDirNDVI)
        self.sublayoutFormNDVIInputDir.addWidget(self.curDir2NDVI)
        self.sublayoutFormNDVIInputDir.addWidget(self.buttons.btnSetNDVIDir)
        self.sublayoutFormNDVIInputDir.addStretch(True)

        self.sublayout.addLayout(self.sublayoutFormInputDir)
        self.sublayout.addLayout(self.sublayoutFormNDVIInputDir)


        self.matchWidget = MatchRGBNDVIWidget(self)
        self.matchWidget.setHidden(True)
        self.sublayout.addWidget(self.matchWidget)
        # if   self.parent.projectInfo.srcDir.strip() and self.parent.projectInfo.srcDirNDVI.strip():
        #     self.enableMatchView()

        self.buttons.home = QPushButton('', self)
        self.buttons.home.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.home.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'home.png')))
        self.buttons.home.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.home.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.home.clicked.connect(self.parent.goHome)
        self.buttons.home.setToolTip('Return to home screen')

        #self.sublayout.addWidget(self.buttons.home, alignment=Qt.AlignLeft)

        self.buttons.nextBtn = QPushButton('Next', self)
        self.buttons.nextBtn.resize(180, 80)
        self.buttons.nextBtn.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttons.nextBtn.hide()
        # connect button to function on_click
        self.buttons.nextBtn.clicked.connect(self.next )

        self.sublayoutLastRow = QHBoxLayout()
        self.sublayoutLastRow.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        self.sublayoutLastRow.addStretch(100)
        self.sublayoutLastRow.addWidget(self.buttons.nextBtn, alignment=Qt.AlignRight)
        self.sublayout.addStretch(True)
        self.sublayout.addLayout(self.sublayoutLastRow)

        self.setLayout(self.sublayout)

        self.setRGBInputDirectory( '/Volumes/ViSUSAg/smallRGB/')
        self.setNDVIInputDirectory('/Volumes/ViSUSAg/smalNDVI')



    def next(self):
        if (self.OPT_FOR_ACCEPT_ALL):
            self.matchWidget.renameFilesRGBNDVI(  self.parent.projectInfo.srcDir, self.parent.projectInfo.srcDirNDVI)
        self.parent.next("AfterAskSource")

    def setRGBInputDirectoryUI(self):
        self.parent.projectInfo.srcDir= str(
            QFileDialog.getExistingDirectory(self, "Select Directory containing RGB Images"))

        self.setRGBInputDirectory(self.parent.projectInfo.srcDir)

    def setRGBInputDirectory(self,fpath):
        self.parent.projectInfo.srcDir = fpath
        self.curDir2.setText(self.parent.projectInfo.srcDir)
        #self.buttons.btnSetRGBDir.setStyleSheet(WHITE_PUSH_BUTTON)
        #self.buttons.btnSetRGBDir.setText('Edit RGB Directory')
        if self.curDir2.text() != '' and self.curDir2NDVI.text() != '':
            self.buttons.nextBtn.show()
            self.enableMatchView()
        self.update()

    def setNDVIInputDirectoryUI(self):
        self.parent.projectInfo.srcDirNDVI = str(
            QFileDialog.getExistingDirectory(self, "Select Directory containing NDVI Images"))

        self.setNDVIInputDirectory(self.parent.projectInfo.srcDirNDVI)

    def setNDVIInputDirectory(self,fpath):
        self.parent.projectInfo.srcDirNDVI = fpath
        self.curDir2NDVI.setText(self.parent.projectInfo.srcDirNDVI)
        #self.buttons.btnSetNDVIDir.setStyleSheet(WHITE_PUSH_BUTTON)
        #self.buttons.btnSetNDVIDir.setText('Edit NDVI Directory')
        if self.curDir2.text() != '' and self.curDir2NDVI.text() != '':
            self.buttons.nextBtn.show()
            self.enableMatchView()
        self.update()

    def enableMatchView(self):
        if not self.OPT_FOR_ACCEPT_ALL:
            #RGB_DIR = '/Volumes/ViSUSAg/RGB_Agrocam/108_10.14.20/'
            #NDVI_DIR = '/Volumes/ViSUSAg/NDVI_Agrocam/108 10.14.20 NDVI/'
            self.matchWidget.setRGB(self.curDir2.text())
            self.matchWidget.setNDVI(self.curDir2NDVI.text())
            self.matchWidget.init( )
            self.matchWidget.setHidden(False)

    def matchSet(self):
        #now that match has been set, files should be renamed, and then slam started
        self.parent.next("AfterAskSource")

class VisoarAskName(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.DEBUG = True
        self.setStyleSheet(LOOK_AND_FEEL)
        class Buttons:
            pass

        self.buttons = Buttons

        self.sublayout= QVBoxLayout()
        self.sublayout.addWidget(addLogo(self.parent.app_dir))
        self.sublayout.addStretch(True)
        self.sublayoutFormProjName = QHBoxLayout()
        self.projNameLabel = QLabel('New Project Name:')
        self.projNametextbox = QLineEdit(self)
        self.projNametextbox.setToolTip('Specify a unique name for this project')
        self.projNametextbox.move(20, 20)

        self.createErrorLabel = QLabel('*')
        self.createErrorLabel.setStyleSheet("""color: #59040c""")
        self.sublayoutFormProjName.addWidget(self.projNameLabel)
        self.sublayoutFormProjName.addWidget(self.projNametextbox)
        self.sublayoutFormProjName.addWidget(self.createErrorLabel)

        self.sublayout.addLayout(self.sublayoutFormProjName)

        self.buttons.home = QPushButton('', self)
        self.buttons.home.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.home.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'home.png')))
        self.buttons.home.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.home.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.home.clicked.connect(self.parent.goHome)
        #self.sublayout.addWidget(self.buttons.home, alignment=Qt.AlignLeft)

        self.buttons.nextBtn = QPushButton('Next', self)
        self.buttons.nextBtn.resize(180, 80)
        self.buttons.nextBtn.setStyleSheet(GREEN_PUSH_BUTTON)
        #self.buttons.nextBtn.hide()
        # connect button to function on_click
        self.buttons.nextBtn.clicked.connect(lambda: self.parent.next("AfterAskName"))

        self.sublayoutLastRow = QHBoxLayout()
        self.sublayoutLastRow.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        self.sublayoutLastRow.addStretch(True)
        self.sublayoutLastRow.addWidget(self.buttons.nextBtn, alignment=Qt.AlignRight)
        self.sublayout.addStretch(True)
        self.sublayout.addLayout(self.sublayoutLastRow)

        self.setLayout(self.sublayout)


class VisoarAskDest(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.DEBUG = True
        self.setStyleSheet(LOOK_AND_FEEL)
        class Buttons:
            pass
        self.buttons = Buttons

        # self.copySourceBox_switch = QCheckBox("Copy Source")
        # self.copySourceBox_switch.stateChanged.connect(lambda: self.parent.copySourceBBOXFlip(self.copySourceBox_switch))
        # self.copySourceBox_switch.setChecked(self.parent.copySourceBool)
        # self.copySourceBox_switch.setStyleSheet(QCHECKBOX_LOOK_AND_FEEL)

        self.sublayout = QVBoxLayout()
        self.sublayout.addWidget(addLogo(self.parent.app_dir))
        self.sublayout.addStretch(True)
        # self.sublayout.addWidget(self.copySourceBox_switch)


        self.sublayoutFormDestName = QHBoxLayout()
        self.destNameLabel = QLabel('ViSOAR Output Destination:')
        self.destNametextbox = QLabel('')
        # self.destNametextbox.clicked.connect(self.setDestName)
        # self.destNametextbox.move(20, 20)
        self.destNewDir = QPushButton("Choose Directory")
        self.destNewDir.setToolTip('Specify directory to save project to')

        self.destNewDir.clicked.connect(self.setDestName)
        self.destNewDir.setStyleSheet(GREEN_PUSH_BUTTON)
        # self.destNametextbox.setHidden(not self.parent.copySourceBool)
        # self.destNameLabel.setHidden(not self.parent.copySourceBool)
        # self.destNewDir.setHidden(not self.parent.copySourceBool)
        self.sublayoutFormDestName.addWidget(self.destNameLabel)
        self.sublayoutFormDestName.addWidget(self.destNametextbox)
        self.sublayoutFormDestName.addWidget(self.destNewDir)
        self.createErrorLabel = QLabel('*')
        self.createErrorLabel.setStyleSheet("""color: #59040c""")
        self.sublayoutFormDestName.addWidget(self.createErrorLabel)
        self.sublayoutFormDestName.addStretch(True)
        self.sublayout.addLayout(self.sublayoutFormDestName)



        self.buttons.create_project = QPushButton('Create Project', self)
        self.buttons.create_project.resize(180, 80)
        self.buttons.create_project.setStyleSheet(GREEN_PUSH_BUTTON)
        #self.buttons.create_project.hide()
        # connect button to function on_click
        self.buttons.create_project.clicked.connect(lambda: self.parent.next('AfterAskDest'))
        self.buttons.create_project.setToolTip('Create project and stitch all images into a mosaic')

        self.buttons.home = QPushButton('', self)
        self.buttons.home.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.home.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'home.png')))
        self.buttons.home.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.home.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.home.clicked.connect(self.parent.goHome)

        self.sublayoutLastRow = QHBoxLayout()
        self.sublayoutLastRow.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        self.sublayoutLastRow.addStretch(True)
        self.sublayoutLastRow.addWidget(self.buttons.create_project, alignment=Qt.AlignRight)
        self.sublayout.addStretch(True)
        self.sublayout.addLayout(self.sublayoutLastRow)

        self.setLayout(self.sublayout)

    def setDestName(self):
        self.parent.projectInfo.projDir = str(
            QFileDialog.getExistingDirectory(self, "Select Directory containing Images"))
        self.destNametextbox.setText(self.parent.projectInfo.projDir )
        self.buttons.create_project.show()
        self.destNewDir.setText('Edit Directory')
        self.destNewDir.setStyleSheet(WHITE_PUSH_BUTTON)
        self.update()


class VisoarNewTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.DEBUG = True
        self.setStyleSheet(LOOK_AND_FEEL)
    #def tabNewUI(self):
        # Create New Tab:

        class Buttons:
            pass

        self.copySourceBool = self.parent.copySourceBool
        self.buttons = Buttons

        self.visoarSlamSettingsDefault = VisoarSlamSettingsDefault(self)
            #,generate_bbox=False,
			#					color_matching=False,
			#					blending_exp="output=voronoi()")
        # AAG: 05152020 was:
        # self.sublayoutTabNew= QVBoxLayout(self)
        self.sublayoutTabNew = QVBoxLayout()
        self.sublayoutTabbar = QHBoxLayout()

        self.sublayoutFormTab = QFormLayout()

        self.buttonAddImagesTab = QPushButton('Add Images', self)
        self.buttonAddImagesTab.resize(180, 40)
        self.buttonAddImagesTab.clicked.connect(self.addImages)
        self.buttonAddImagesTab.setStyleSheet(GREEN_PUSH_BUTTON)
        #self.sublayoutTabbar.addWidget(self.buttonAddImages, alignment=Qt.AlignLeft)

        self.buttonSetSaveDir = QPushButton('Set Save Directory', self)
        self.buttonSetSaveDir.resize(180, 40)
        self.buttonSetSaveDir.clicked.connect(self.setSaveDir)
        self.buttonSetSaveDir.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttonSetSaveDir.setToolTip('Specify directory of image saving files')

        self.settingsButton = QToolButton()
        self.settingsButton.setText('Settings')
        self.settingsButton.resize(V_BUTTON_SIZE, V_BUTTON_SIZE)
        self.settingsButton.clicked.connect(self.adjustSlamSettings)
        self.settingsButton.setStyleSheet(GREEN_PUSH_BUTTON)
        self.settingsButton.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'settings_green.png')))
        self.settingsButton.setIconSize(QSize(V_BUTTON_SIZE, V_BUTTON_SIZE))
        self.settingsButton.setFixedSize(V_BUTTON_SIZE, V_BUTTON_SIZE)
        self.settingsButton.setMinimumSize(V_BUTTON_SIZE, V_BUTTON_SIZE)
        self.settingsButton.setStyleSheet("""padding:10; border-radius:10px;""")

        #		self.sublayoutTabNew.addLayout(self.sublayoutForm) #, row, 1,4)


        self.detailsBox = QGroupBox('Create mosaic:')
        self.detailsBox.setStyleSheet(QGROUPBOX_LOOK_AND_FEEL)

        self.detailsBox.setLayout(self.sublayoutFormTab)
        self.sublayoutTabNew.addWidget(self.detailsBox)  # , row, 1,4)

        self.createErrorLabel = QLabel('*')
        # self.sublayoutTabNew.addWidget(  self.createErrorLabel, alignment=Qt.AlignCenter    )
        # print("to do: fix bug on createErrorLable style sheet")
        self.createErrorLabel.setStyleSheet("""color: #59040c""")

        # Ability to change location
        #self.parent.projectInfo.projDir = ''  # os.getcwd()
        #self.parent.projectInfo.srcDir = ''  # os.getcwd()
        self.curDirTab = QLabel('Save Images to:')
        self.curDir2Tab = QLabel(self.parent.projectInfo.projDir)
        self.curDir2Tab.setStyleSheet("""font-family: Roboto;font-style: normal;font-size: 14pt; padding:20px """)
        self.curDirTab.resize(280, 40)

        self.srcDir = QLabel('Source Images')
        self.srcDir2 = QLabel(self.parent.projectInfo.srcDir)
        self.srcDir2.setStyleSheet("""font-family: Roboto;font-style: normal;font-size: 14pt; padding:20px """)
        self.srcDir.resize(280, 40)

        self.inputModeNewTabLabel = QLabel("Sensor:", self)

        self.comboBoxNewTab = QComboBox(self)
        self.comboBoxNewTab.addItem("R G B")
        self.comboBoxNewTab.addItem("O C NIR (MapIR)")
        self.comboBoxNewTab.addItem("R G NIR")
        self.comboBoxNewTab.addItem("R NIR (Sentera NDVI)")
        self.comboBoxNewTab.addItem("RedEdge NIR (Sentera NDRE)")
        self.comboBoxNewTab.setStyleSheet(MY_COMBOX)
        self.comboBoxNewTab.currentIndexChanged.connect(self.inputModeChangedNewTab)
        self.comboBoxNewTab.setFixedSize(100, 40)
        self.comboBoxNewTab.resize(100, 40)
        self.comboBoxNewTab.setFixedWidth(100)
        self.comboBoxNewTab.setFixedHeight(40)

        # pal = self.comboBoxNewTab.palette();
        # visoarGreen = QColor('#045951')  #visoar green
        # pal.setColor(QPalette.Background, visoarGreen);
        # self.comboBoxNewTab.setPalette(pal);
        self.sublayoutFormInputDir = QHBoxLayout()

        self.sublayoutFormInputDir.addWidget(self.srcDir)
        self.sublayoutFormInputDir.addWidget(self.srcDir2)
        self.sublayoutFormInputDir.addWidget(self.buttonAddImagesTab)
        self.sublayoutFormInputDir.addStretch(True)

        self.sublayoutFormInputDir2 = QHBoxLayout()
        self.sublayoutFormInputDir2.addWidget(self.curDirTab)
        self.sublayoutFormInputDir2.addWidget(self.curDir2Tab)
        self.sublayoutFormInputDir2.addWidget(self.buttonSetSaveDir)

        self.sublayoutFormTab.addRow(self.inputModeNewTabLabel, self.comboBoxNewTab)

        self.sublayoutFormTab.addRow(self.sublayoutFormInputDir)
        self.sublayoutFormTab.addRow(self.sublayoutFormInputDir2)

        print('combobox new tab: ' + str(self.comboBoxNewTab.currentIndex()))

        # Ask for Project Name
        self.sublayoutDetails = QVBoxLayout()
        self.sublayoutFormProjName = QHBoxLayout()
        self.projNameLabel = QLabel('New Project Name:')
        self.projNametextbox = QLineEdit(self)
        self.projNametextbox.move(20, 20)

        # self.copySourceBox_switch = QCheckBox("Copy Source")
        # self.copySourceBox_switch.stateChanged.connect(lambda: self.copySourceBBOXFlip(self.copySourceBox_switch))
        # self.copySourceBox_switch.setChecked(self.copySourceBool)
        # self.copySourceBox_switch.setStyleSheet(QCHECKBOX_LOOK_AND_FEEL)

        # self.sublayoutFormDestName = QHBoxLayout()
        # self.destNameLabel = QLabel('Copy Source To:')
        # self.destNametextbox = QLabel('')
        # #self.destNametextbox.clicked.connect(self.setDestName)
        # #self.destNametextbox.move(20, 20)
        # self.destNewDir = QPushButton(". . .")
        # self.destNewDir.clicked.connect(self.setDestName)
        # self.destNewDir.setStyleSheet(GREEN_PUSH_BUTTON)
        # self.destNametextbox.setHidden(not self.copySourceBool)
        # self.destNameLabel.setHidden(not self.copySourceBool)
        # self.destNewDir.setHidden(not self.copySourceBool)
        #
        # self.sublayoutFormDestName.addWidget(self.destNameLabel)
        # self.sublayoutFormDestName.addWidget(self.destNametextbox)
        # self.sublayoutFormDestName.addWidget(self.destNewDir)

        self.comboBoxNewTab.setFixedSize(180, 40)
        self.projNametextbox.resize(180, 40)
        self.projNametextbox.setStyleSheet(
            "min-height:30; min-width:180; padding:0px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")

        self.sublayoutFormProjName.addWidget(self.projNametextbox)
        self.sublayoutDetails.addLayout(self.sublayoutFormProjName)
        # self.sublayoutDetails.addWidget(self.copySourceBox_switch)
        # self.sublayoutDetails.addLayout(self.sublayoutFormDestName)
        # self.sublayoutFormProjName.addWidget(self.createErrorLabel)
        container = QWidget()
        container.setLayout(self.sublayoutDetails)

        self.sublayoutFormTab.addRow(self.projNameLabel, container)
        self.sublayoutFormTab.addRow(self.createErrorLabel)

        # toolbar.addWidget(self.inputModeLabel)
        # toolbar.addWidget(self.comboBox)

        # Button that says: "Create Project"
        self.buttons.create_project = QPushButton('Create Project', self)
        # self.buttons.create_project.move(20,80)
        self.buttons.create_project.resize(180, 80)
        self.buttons.create_project.setStyleSheet(GREEN_PUSH_BUTTON)
        # self.spaceLabel2 = QLabel('')
        # self.spaceLabel2.resize(380,40)

        # self.sublayoutTabNew.addWidget(self.inputModeNewTabLabel)
        # self.sublayoutTabNew.addWidget(self.comboBoxNewTab)

        self.buttons.home = QPushButton('', self)
        self.buttons.home.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.home.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'home.png')))
        self.buttons.home.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.home.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.home.clicked.connect(self.parent.goHome)

        self.buttons.create_project.hide()
        # connect button to function on_click
        self.buttons.create_project.clicked.connect(self.createProject)

        self.setLayout(self.sublayoutTabNew)


        #self.sublayoutTabbar.addWidget(self.buttons.create_project)
        self.sublayoutTabNew.addLayout(self.sublayoutTabbar)  # ,row,0)

        self.sublayoutTabNew.addWidget(self.parent.logo)  # ,row,0)
        #self.sublayoutTabNew.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        #self.sublayoutTabNew.addWidget(self.settingsButton, alignment=Qt.AlignRight)

        self.sublayoutLastRow = QHBoxLayout()
        self.sublayoutLastRow.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        self.sublayoutLastRow.addWidget(self.settingsButton, alignment=Qt.AlignLeft)
        self.sublayoutLastRow.addStretch(True)
        self.sublayoutLastRow.addWidget(self.buttons.create_project, alignment=Qt.AlignRight)
        self.sublayoutTabbar.addLayout(self.sublayoutLastRow)

        if self.DEBUG:
            print('tabNewUI finished')

    def setDestName(self):
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory to copy all files to"))
        self.destNametextbox.setText(dir)
        print(self.destNametextbox.text())
        self.parent.projectInfo.projDir = dir
        return dir

    def copySourceBBOXFlip(self, btn):
        self.copySourceBool = not self.copySourceBool
        self.destNameLabel.setHidden(not self.copySourceBool)
        self.destNametextbox.setHidden(not self.copySourceBool)
        self.destNewDir.setHidden(not self.copySourceBool)
        self.copySourceBox_switch.setChecked( self.copySourceBool)
        print('copySourceBool BBOX: {0}'.format(self.copySourceBool))


    def adjustSlamSettings(self):
        self.visoarSlamSettingsDefault.on_show()

    def updateSlamSettings(self,generate_bbox,color_matching,blending_exp ):
        print('Set Defaults for updateSlamSettings: bbox[{0}] Color[{1]] Blend[{2}]'.format, (generate_bbox,
                                                                                    color_matching,blending_exp ))
        self.parent.generate_bbox = generate_bbox
        self.parent.color_matching = color_matching
        self.parent.blending_exp = blending_exp
        print("Note to self, taking out slam default changes")
        #self.parent.slam_widget.setDefaults(generate_bbox=generate_bbox,color_matching=color_matching,blending_exp=blending_exp)

    def addImages(self):
        # if self.DEBUG:
        print('DEBUG: will create Project')
        self.parent.projectInfo.projName = self.projNametextbox.text()
        self.parent.projectInfo.srcDir = str(QFileDialog.getExistingDirectory(self, "Select Directory containing Images"))

        #self.parent.projectInfo.projDir = self.parent.projectInfo.srcDir
        if not self.parent.projectInfo.projName:
            tempName = os.path.basename(os.path.normpath(self.parent.projectInfo.srcDir))
            self.projNametextbox.setText(tempName)
            self.parent.projectInfo.projName = tempName

        self.srcDir2.setText(self.parent.projectInfo.srcDir)
        self.curDir2Tab.setText(self.parent.projectInfo.projDir)
        # if ((not (self.parent.projectInfo.projDir.strip() == "")) and (not (self.parent.projectInfo.projName.strip() == ""))):
        #     self.parent.tabs.setTabEnabled(2, True)
        #     # self.tabs.setTabEnabled(3,True)
        #     self.parent.tabs.setCurrentIndex(2)
        #     if self.DEBUG:
        #         print('DEBUG: will create Project')
        #     #self.createProject()
        # else:
        errorStr = ''
        if not self.parent.projectInfo.srcDir.strip():
            print(self.parent.projectInfo.srcDir)
            errorStr = 'Please Provide a directory of images or click on the load tab to load a dataset you\'ve already stitched\n'
        if not self.parent.projectInfo.projName.strip():
            print(self.parent.projectInfo.projName)
            errorStr = errorStr + 'Please provide a unique name for your project'
        self.createErrorLabel.setText(errorStr)

        self.buttons.create_project.show()
        self.buttonAddImages.setStyleSheet(WHITE_PUSH_BUTTON)
        self.buttonAddImages.setText('Edit Directory')
        if self.DEBUG:
            print('Images Added')
        self.update()

    def setSaveDir(self):
        # if self.DEBUG:
        print('DEBUG: will set Save dir')

        self.parent.projectInfo.projDir = str(
            QFileDialog.getExistingDirectory(self, "Select Directory containing Images"))
        self.curDir2Tab.setText(self.parent.projectInfo.projDir)
        self.srcDir2.setText(self.parent.projectInfo.srcDir)
        if not os.path.exists( os.path.join(self.parent.projectInfo.projDir, self.parent.projectInfo.projName) ):
            os.makedirs(os.path.join(self.parent.projectInfo.projDir, self.parent.projectInfo.projName ))
        self.parent.projectInfo.projDir=os.path.join(self.parent.projectInfo.projDir, self.parent.projectInfo.projName )
        # errorStr = ''
        # if not self.parent.projectInfo.projDir.strip():
        #     print(self.parent.projectInfo.projDir)
        #     errorStr = 'Please Provide a directory of images or click on the load tab to load a dataset you\'ve already stitched\n'
        # if not self.parent.projectInfo.projName.strip():
        #     print(self.parent.projectInfo.projName)
        #     errorStr = errorStr + 'Please provide a unique name for your project'
        # self.createErrorLabel.setText(errorStr)
        #
        # self.buttons.create_project.show()
        # self.buttonAddImages.setStyleSheet(WHITE_PUSH_BUTTON)
        # self.buttonAddImages.setText('Edit Directory')
        # if self.DEBUG:
        #     print('Images Added')
        self.update()

    def inputModeChangedNewTab(self):
        self.parent.inputMode = self.comboBoxNewTab.currentText()
        self.parent.inputModeChanged()

    def checkNameOriginal(self, name):
        return self.parent.visoarUserLibraryData.isUniqueName(name)

    def createProject(self):
        if self.DEBUG:
            print('DEBUG: in createProject')
        self.createErrorLabel.setText('')
        self.parent.projectInfo.projName = self.projNametextbox.text()
        #self.parent.projectInfo.projDir = self.curDir2.text()
        # reset text boxes
        self.projNametextbox.setText('')
        self.curDir2.setText('')
        print(self.parent.projectInfo.projName)
        print(self.parent.projectInfo.projDir)
        checkName = self.checkNameOriginal(self.parent.projectInfo.projName)
        print('Check name unique?')
        print('Create Proj')
        print(self.parent.projectInfo.projName)
        print(self.parent.projectInfo.projDir)

        if ((not self.parent.projectInfo.projDir.strip() == "") and
                (not self.parent.projectInfo.srcDir.strip() == "") and
                (not self.parent.projectInfo.projName.strip() == "") and
                checkName
                #and
                #(not self.destNametextbox.text() == "")
            ):
            # if self.copySourceBool:
            #     copyret = recursive_copy_files( self.parent.projectInfo.projDir, self.destNametextbox.text())
            # print('copied {0} files'.format(copyret))

            if self.DEBUG:
                print('DEBUG: createProject: read userFileHistory')
            self.parent.visoarUserLibraryData.createProject(self.parent.projectInfo.projName,self.parent.projectInfo.projDir,self.parent.projectInfo.srcDir,self.parent.projectInfo.projDirNDVI,self.parent.projectInfo.srcDirNDVI)
            print('Change tabs')
            # Check to see if midx files exists, if it does, go to Analytics
            if self.stitchAlreadyDone():
                self.parent.enableViewStitching()
                self.parent.goToAnalyticsTab()
            else:
                self.parent.enableViewStitching()
                self.parent.changeViewStitching()
                print("Note to self, taking out slam default changes")
                #                self.parent.slam_widget.setDefaults(generate_bbox=self.parent.generate_bbox,color_matching=self.parent.color_matching,blending_exp=self.parent.blending_exp)
                self.parent.startViSUSSLAM()
            print('started slam')
        else:
            errorStr = ''
            if not checkName:
                errorStr = 'Please Provide a Unique name for your project\n'
            elif not self.parent.projectInfo.projDir.strip():
                errorStr = 'Please Provide a directory of images or click on the load tab to load a dataset you\'ve already stitched\n'
            if not self.parent.projectInfo.projName.strip():
                errorStr = errorStr + 'Please provide a unique name for your project'
            self.createErrorLabel.setText(errorStr)
            self.projNametextbox.setText(self.parent.projectInfo.projName)
            self.srcDir2.setText(self.parent.projectInfo.srcDir)
            self.curDir2.setText(self.parent.projectInfo.projDir )

        if self.DEBUG:
            print('createProject finished')

    def stitchAlreadyDone(self):
       # return os.path.exists(os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles', 'visus.midx'))
        return os.path.exists(os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles', 'idx', '0000.bin'))
        #or
        #        os.path.exists(os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles', 'idx', '000.bin')) or
        #       os.path.exists(os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles', 'idx', '00000.bin'))



