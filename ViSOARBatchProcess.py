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

from editUserLibrary			import *
from VisoarStartTab			import *
from VisoarNewTab			import *
#from VisoarNewTimeSeriesTab			import *
from VisoarLoadTab			import *
#from VisoarStitchTab			import *
from VisoarAnalyzeTab			import *
from ViSOARUIWidget             import *

#from slam2dWidget 				import *
from gmail_visoar				import *

# IMPORTANT for WIndows
# Mixing C++ Qt5 and PyQt5 won't work in Windows/DEBUG mode
# because forcing the use of PyQt5 means to use only release libraries (example: Qt5Core.dll)
# but I'm in need of the missing debug version (example: Qt5Cored.dll)
# as you know, python (release) does not work with debugging versions, unless you recompile all from scratch

# on windows rememeber to INSTALL and CONFIGURE
class TabBar(QTabBar):
    def tabSizeHint(self, index):
        size = QTabBar.tabSizeHint(self, index)
        w = int(self.width() / self.count())
        return QSize(w, size.height())

class Logger(QtCore.QObject):

	"""Redirects console output to text widget."""
	my_signal = QtCore.pyqtSignal(str)

	# constructor
	def __init__(self, terminal=None, filename="", qt_callback=None):
		super().__init__()
		self.terminal=terminal
		self.log=open(filename,'w')
		self.my_signal.connect(qt_callback)

	# write
	def write(self, message):
		message=message.replace("\n", "\n" + str(datetime.datetime.now())[0:-7] + " ")
		self.terminal.write(message)
		self.log.write(message)
		self.my_signal.emit(str(message))

	# flush
	def flush(self):
		self.terminal.flush()
		self.log.flush()


class MyPopup(QWidget):
    def __init__(self):
        QWidget.__init__(self)

    def paintEvent(self, e):
        dc = QPainter(self)
        dc.drawLine(0, 0, 100, 100)
        dc.drawLine(100, 0, 0, 100)

#select directory of project files
#choose mode: assume the mode is the same for all the directories
#Choose directory of images
#Choose place to save them all
#Add entry in User's xml history file
#for each file
#  run slam
#  save midx
#  convert to idx
#  upload idx to server

class VisoarAgExplorerBatchProcessWidget(ViSOARUIWidget):
    def __init__(self, parent):
        super(ViSOARUIWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.app_dir = os.getcwd()
        self.SHOW_GOGGLE_MAP = False
        self.ANNOTATIONS_MODE = False
        self.isWINDOWS = (sys.platform.startswith("win") or
                   (sys.platform == 'cli' and os.name == 'nt'))

        self.inputMode = "R G B"
        self.projectInfo = VisoarProject()
        self.userFileHistory = os.path.join(os.getcwd(), 'userFileHistory.xml')
        self.generate_bbox = False
        self.color_matching = False
        self.blending_exp = "output=voronoi()"
        self.ADD_VIEWER = True  # Flag for removing viewers for testing
        self.USER_TAB_UI = False

        self.scriptNames = MASTER_SCRIPT_LIST
        self.LINK_CAMERAS = True
        self.DEBUG = True
        self.copySourceBool = False

        self.dir_of_rgb_source = "/Volumes/ViSUSAg/DirOfDirs"
        self.dir_of_nir_source = ""
        self.dir_of_result = "/Volumes/ViSUSAg/OutputOfDirOfDirs"

        self.loadWidgetDict = {}
        self.loadLabelsWidgetDict = {}

        if os.path.exists(self.userFileHistory):
            print('All app settings will be saved to: ' + self.userFileHistory)
        else:
            f = open(self.userFileHistory, "wt")
            today =    datetime.now()
            todayFormated = today.strftime("%Y%m%d_%H%M%S")
            f.write('<data>\n' +
                    '\t<project>\n' +
                    '\t\t<projName>TestData</projName>\n' +
                    '\t\t<projDir>./data/TestData</projDir>\n' +
                    '\t\t<srcDir>./data/TestData</srcDir>\n' +
                    '\t\t<createdAt>'+todayFormated+'</createdAt>\n' +
                    '\t\t<updatedAt>'+todayFormated+'</updatedAt>\n' +
                    '\t</project>\n' +
                    '</data>\n')
            f.close()

        if self.ADD_VIEWER:
            self.viewerW = MyViewerWidget(self)
            self.viewerW2 = MyViewerWidget(self)
            self.viewer = self.viewerW.viewer  # MyViewer()
            self.viewer2 = self.viewerW2.viewer  # MyViewer()

            # self.viewer.hide()
            self.viewer.setMinimal()
            self.viewer2.setMinimal()

            self.cam1 = self.viewer.getGLCamera()
            self.cam2 = self.viewer2.getGLCamera()

            # disable smoothing
            if isinstance(self.cam1, GLOrthoCamera): self.cam1.toggleDefaultSmooth()
            if isinstance(self.cam2, GLOrthoCamera): self.cam2.toggleDefaultSmooth()

            self.viewer.on_camera_change = lambda: self.onCameraChange12()
            self.viewer2.on_camera_change = lambda: self.onCameraChange21()
            # self.viewer_subwin = sip.wrapinstance(FromCppQtWidget(self.viewer.c_ptr()), QtWidgets.QMainWindow)
            # self.viewer_subwin2 = sip.wrapinstance(FromCppQtWidget(self.viewer2.c_ptr()), QtWidgets.QMainWindow)
            self.viewer_subwin = self.viewerW.viewer_subwin
            self.viewer_subwin2 = self.viewerW2.viewer_subwin

        else:
            self.viewer_subwin = QWidget(self)

        self.pythonScriptingWindow = PythonScriptWindow(self)
        self.pythonScriptingWindow.resize(600, 640)
        self.logo = QPushButton('', self)
        self.logo.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.logo.setIcon(QIcon(os.path.join(self.app_dir, 'icons', 'visoar_logo.png')))
        self.logo.setIconSize(QSize(480, 214))
        self.logo.setText('')

        self.openfilenameLabelS = QLabel()
        self.openfilenameLabelS.resize(480, 40)
        self.openfilenameLabelS.setStyleSheet(
            "min-height:30; min-width:180; padding:0px; background-color: #ffffff; color: rgb(0, 0, 0);  border: 0px")

        self.openfilenameLabel = QLabel()
        self.openfilenameLabel.resize(480, 40)
        self.openfilenameLabel.setStyleSheet(
            "min-height:30; min-width:180; padding:0px; background-color: #ffffff; color: rgb(0, 0, 0);  border: 0px")
        self.openfilenameLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # if self.ADD_VIEWER:
        #     self.slam_widget = Slam2DWidget(self)

        self.visoarUserLibraryData = VisoarUserLibraryData(self.userFileHistory)

        self.tabStart = VisoarStartTabWidget(self)  # QWidget()
        self.tabAskSensor = VisoarAskSensor(self)
        self.tabAskSource = VisoarAskSource(self)
        self.tabAskSourceRGBNDVI = VisoarAskSourceRGBNDVI(self)
        #self.tabAskName = VisoarAskName(self)
        self.tabAskDest = VisoarAskDest(self)
        self.tabLoad = VisoarLoadTabWidget(self)  # QWidget()
        self.tabViewer = VisoarAnalyzeTabWidget(self)  # QWidget()

        #self.log = QTextEdit()
        #self.log.setLineWrapMode(QTextEdit.NoWrap)
        self.log = QTextEdit(self, readOnly=True)
        self.log.ensureCursorVisible()
        self.log.setLineWrapColumnOrWidth(500)
        self.log.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.log.setFixedWidth(400)
        self.log.setFixedHeight(150)
        self.log.move(30, 100)

        self.ASKSENSOR_TAB = 0
        self.ASKSOURCE_TAB = 1
        self.ASKSOURCERGBNDVI_TAB = 2
        self.ASKDEST_TAB = 3
        self.LOG_TAB = 4
        self.LOAD_TAB = 5
        self.ANALYTICS_TAB = 6
        self.START_TAB = 7

        self.leftlist = QListWidget()
        self.leftlist.insertItem(self.ASKSENSOR_TAB, 'One Screen New')
        self.leftlist.insertItem(self.ASKSOURCE_TAB, 'Directory of Directories')
        self.leftlist.insertItem(self.ASKSOURCERGBNDVI_TAB, 'Directory of Directories')
        #self.leftlist.insertItem(self.ASKNAME_TAB, 'Name for new project')
        self.leftlist.insertItem(self.ASKDEST_TAB, 'Directory to save MIDX/IDX')
        self.leftlist.insertItem(self.LOG_TAB, 'Log of Computation')
        self.leftlist.insertItem(self.LOAD_TAB, 'Load Library of MIDX/IDX')
        self.leftlist.insertItem(self.ANALYTICS_TAB, 'Viewer')
        self.leftlist.insertItem(self.START_TAB, 'Start')

        self.leftlist.currentRowChanged.connect(self.display)

        # use stack
        self.tabs = QStackedWidget()

        self.tabAskSensor = VisoarAskSensor(self)
        self.tabAskSource = VisoarAskSource(self)
        self.tabAskSourceRGBNDVI = VisoarAskSourceRGBNDVI(self)
        #self.tabAskName = VisoarAskName(self)
        self.tabAskDest = VisoarAskDest(self)

        self.tabStart = VisoarStartTabWidget(self)  # QWidget()
        #self.tabNewStitching = VisoarNewTabWidget(self)  # QWidget()
        #self.tabNewTimeSeries = VisoarNewTimeSeriesTabWidget(self)  # QWidget()
        self.tabLoad = VisoarLoadTabWidget(self)  # QWidget()

        if self.ADD_VIEWER:
            #self.tabStitcher = VisoarStitchTabWidget(self)  # QWidget()
            self.tabViewer = VisoarAnalyzeTabWidget(self)  # QWidget()

        #self.tabs.addWidget(self.tabStart)
        self.tabs.addWidget(self.tabAskSensor)
        self.tabs.addWidget(self.tabAskSource)
        self.tabs.addWidget(self.tabAskSourceRGBNDVI)
        #self.tabs.addWidget(self.tabAskName)
        self.tabs.addWidget(self.tabAskDest)
        self.tabs.addWidget(self.log)
        self.tabs.addWidget(self.tabLoad)
        self.tabs.addWidget(self.tabViewer)
        self.tabs.addWidget(self.tabStart)

        self.tabs.setCurrentIndex(0)
        self.layout.addWidget(self.tabs)
        # _stdout = sys.stdout
        # _stderr = sys.stderr
        logger=Logger(terminal=sys.stdout, filename="~visusslam.log", qt_callback=self.printLog)
        # sys.stdout = logger
        # sys.stderr = logger

    # def onUpdateText(self, text):
    #     cursor = self.process.textCursor()
    #     cursor.movePosition(QtGui.QTextCursor.End)
    #     cursor.insertText(text)
    #     self.process.setTextCursor(cursor)
    #     self.process.ensureCursorVisible()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def printLog(self, text):
        self.log.moveCursor(QtGui.QTextCursor.End)
        self.log.insertPlainText(text)
        self.log.moveCursor(QtGui.QTextCursor.End)
        if hasattr(self, "__print_log__") and self.__print_log__.elapsedMsec() < 200: return
        self.__print_log__ = Time.now()

    def display(self, i):
        self.tabs.setCurrentIndex(i)

    def addImages(self):
        # if self.DEBUG:
        print('DEBUG: will create Project')
        self.dir_of_rgb_source = str(
            QFileDialog.getExistingDirectory(self, "Select Directory containing Images"))
        # self.projectInfo.projDir = self.projectInfo.srcDir
        print( self.dir_of_rgb_source)
        self.tabAskSource.curDir2.setText( self.dir_of_rgb_source)
        self.tabAskSource.buttonAddImagesSource.setStyleSheet(WHITE_PUSH_BUTTON)
        self.tabAskSource.buttonAddImagesSource.setText('Edit Directory')
        self.tabAskSource.buttons.nextBtn.show()
        self.update()

    def goHome(self):

        self.tabAskDest.destNametextbox.setText('')
        self.tabAskDest.createErrorLabel.setText('')
        # self.tabAskName.projNametextbox.setText('')
        # self.tabAskName.createErrorLabel.setText('')
        self.tabAskSource.curDir2.setText('')
        self.tabAskSource.buttonAddImagesSource.setText('Choose Directory')
        self.tabAskSource.buttonAddImagesSource.setStyleSheet(GREEN_PUSH_BUTTON)
        self.tabAskDest.destNewDir.setText('Choose Directory')
        self.tabAskDest.destNewDir.setStyleSheet(GREEN_PUSH_BUTTON)
        # self.tabNewStitching.buttonAddImagesTab.setText('Choose Directory')
        # self.tabNewStitching.buttonAddImagesTab.setStyleSheet(GREEN_PUSH_BUTTON)

        self.tabs.setCurrentIndex(self.START_TAB)
        self.update()

    def next(self, s):
        # implement next button on stacked view, s = current tab, need to move to what comes next
        if s == 'AfterAskSensor':
            print('AfterAskSensor')
            if (self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam') or (self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
                self.tabs.setCurrentIndex(self.ASKSOURCERGBNDVI_TAB)
            else:
                self.tabs.setCurrentIndex(self.ASKSOURCE_TAB)
            self.tabAskSource.curDir2.setText(self.dir_of_rgb_source)
            self.tabAskDest.destNametextbox.setText(self.dir_of_result)
        elif s == 'AfterAskSource':
            self.dir_of_rgb_source =  self.tabAskSource.curDir2.text()
            if self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam' or (self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
                self.dir_of_nir_source = self.tabAskSource.curDir2.text()
                print('AfterAskSource')
                if (not self.dir_of_rgb_source.strip()) or (not self.dir_of_nir_source ):
                    errorStr = 'Please Provide both RGB and NDVI directories or go back home and use a different sensor type\n'
                    self.tabAskSource.createErrorLabel.setText(errorStr)
                else:
                    tempName = '' #os.path.basename(os.path.normpath(self.dir_of_rgb_source.strip()))
                    #self.tabAskName.projNametextbox.setText(tempName)
                    self.projectInfo.projName = tempName
                    self.tabAskDest.destNametextbox.setText('')
                    self.tabs.setCurrentIndex(self.ASKDEST_TAB)
            else:
                print('AfterAskSource')
                if not self.dir_of_rgb_source.strip():
                    errorStr = 'Please Provide a directory of directories of images \n'
                    self.tabAskSource.createErrorLabel.setText(errorStr)
                else:
                    tempName = '' #os.path.basename(os.path.normpath(self.dir_of_rgb_source.strip()))
                    #self.tabAskName.projNametextbox.setText(tempName)
                    self.projectInfo.projName = tempName
                    self.tabAskDest.destNametextbox.setText('')
                    self.tabs.setCurrentIndex(self.ASKDEST_TAB)

        elif s == 'AfterAskName':
            # v = self.setProjName()
            # if v:
            #     self.tabs.setCurrentIndex(self.ASKDEST_TAB)
            print('---------->  ERROR: AfterAskName')
            # self.tabAskName.projNametextbox.setText('')
        #FIX FROM HERE
        elif s == 'AfterAskDest':
            self.tabs.setCurrentIndex(self.LOG_TAB)
            self.update()

            if self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam' or (self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
                self.dir_of_result = self.destNametextbox
                # self.projectInfo.projDir = self.projectInfo.srcDir
                # self.projectInfo.projDirNDVI = self.projectInfo.srcDirNDVI

            self.startProcessing()

            print('end of AfterAskDest')
            # self.tabAskDest.destNametextbox.setText('')
            # self.tabAskName.projNametextbox.setText('')
            # self.tabAskSource.curDir2.setText('')

        elif s == 'AfterStitching':
            self.tabs.setCurrentIndex(self.ANALYTICS_TAB)
        else:
            print(s)

    def startProcessing(self):

        for aSrcPath in os.listdir(self.dir_of_rgb_source):
            self.projectInfo.srcDir = os.path.join(self.dir_of_rgb_source, aSrcPath)
            if os.path.isdir( self.projectInfo.srcDir):
                print( self.projectInfo.srcDir)
                self.projectInfo.projDir =  self.projectInfo.srcDir
                self.projectInfo.projName = os.path.basename(os.path.normpath(self.projectInfo.srcDir))
                #self.projectInfo.projDirNDVI =
                #self.projectInfo.srcDirNDVI =

                self.projectInfo.cache_dir = os.path.join(self.projectInfo.projDir, 'VisusSlamFiles')
                if not os.path.exists(self.projectInfo.cache_dir):
                    os.makedirs(self.projectInfo.cache_dir)
                if not  os.path.exists(os.path.join(self.projectInfo.cache_dir,'visus.midx')):
                    self.setAndRunSlam( self.projectInfo.srcDir, cache_dir=self.projectInfo.cache_dir )



                    self.visoarUserLibraryData.createProject(self.projectInfo.projName,
                                                             self.projectInfo.projDir,
                                                             self.projectInfo.srcDir,
                                                             self.projectInfo.projDirNDVI,
                                                             self.projectInfo.srcDirNDVI)
                else:
                    print(self.projectInfo.cache_dir+' MIDX already exists..')

        #Load Load screen and enable viewer
        self.tabViewer.buttons.comboBoxATab.setCurrentIndex(self.tabAskSensor.comboBoxNewTab.currentIndex())
        import time
        time.sleep(3)

        self.tabs.setCurrentIndex(self.LOAD_TAB)
        self.update()

    def generateImage(self, img):
        t1 = Time.now()
        print("Generating image", img.filenames[0])
        generated = self.provider.generateImage(img)
        ret = InterleaveChannels(generated)
        print("done", img.id, "range", ComputeImageRange(ret), "shape", ret.shape, "dtype", ret.dtype, "in",
              t1.elapsedMsec() / 1000, "msec")
        return ret

    def setAndRunSlam(self, image_dir, cache_dir=None, telemetry=None, plane=None, calibration=None,
                          physic_box=None):
        self.slam.setImageDirectory(image_dir,  cache_dir= cache_dir, telemetry=telemetry, plane=plane, calibration=calibration, physic_box=physic_box)
        retSlamSetup = self.slam_widget.run(self.slam)
        self.slam_widget.onRunClicked()
        retSlamRan = self.slam_widget.slam.run()
        self.setUpRClone()

#
# class VisoarAgExplorerBatchProcess(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle('ViSOAR Ag Explorer Batch Process')
#         # print('OpenCV version:  ')
#         # print(cv2.__version__)
#         self.setMinimumSize(QSize(600, 800))
#         self.setStyleSheet(LOOK_AND_FEEL)
#         #self.showMaximized()
#         #self.setWindowFlags(
#         #    self.windowFlags() | Qt.WindowStaysOnTopHint)  # set always on top flag, makes window disappear
#
#         self.central_widget = QFrame()
#         self.central_widget.setFrameShape(QFrame.NoFrame)
#
#
#         self.DEBUG = True
#
#         QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
#
#         self.tab_widget = VisoarAgExplorerBatchProcessWidget(self)
#         self.setCentralWidget(self.tab_widget)
#         # self.setWindowFlags(Qt.WindowStaysOnTopHint)
#         # self.showNormal()
#         # self.raise_()
#         # self.activateWindow()
#         if self.DEBUG:
#             print('VisoarAgExplorer init finished')
#
#     def on_click(self):
#         print("\n")
#         for currentQTableWidgetItem in self.tabWidget.selectedItems():
#             print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
#         if self.DEBUG:
#             print('on_click finished')
#
#     def onChange(self):
#         QMessageBox.information(self,
#                                 "Tab Index Changed!",
#                                 "Current Tab Index: ")
#         if self.DEBUG:
#             print('onChange finished')
#
#     def printLog(self, text):
#         self.tab_widget.printLog(text)
#         if self.DEBUG:
#             print('printLog finished')
#
#
# # //////////////////////////////////////////////////////////////////////////////
#
# # //////////////////////////////////////////////
# def Main(argv):
#     SetCommandLine("__main__")
#     app = QApplication(sys.argv)
#     app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
#     app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
#
#     app.setStyle("Fusion")
#
#     visoarGreen = '#045951'  # 4,89,81
#     visoarGreenRGB = QColor(4, 89, 81)
#     visoarRed = '#59040c'
#     visoarBlue = '#043759'
#     visoarLightGreen = '#067f73'
#     visoarDarkGreen = '#02332f'  # 2,51,47
#     visoarDarkGreenRGB = QColor(2, 51, 47)
#     visoarGreenWebSafe = '#006666'
#     visoarHighlightYellow = '#d6d2b1'  # 214,210,177
#     visoarHighlightYellowRGB = QColor(214, 210, 177)
#     if True:
#         palette =  QPalette()
#         palette.setColor(QPalette.Window, Qt.white)
#         palette.setColor(QPalette.WindowText, Qt.black)
#         palette.setColor(QPalette.Base,  visoarGreenRGB)
#         palette.setColor(QPalette.AlternateBase, visoarDarkGreenRGB)
#         palette.setColor(QPalette.ToolTipBase, Qt.black)
#         palette.setColor(QPalette.ToolTipText, Qt.white)
#         palette.setColor(QPalette.Text, Qt.white)
#         palette.setColor(QPalette.Button,visoarGreenRGB)
#         palette.setColor(QPalette.ButtonText, Qt.white)
#         palette.setColor(QPalette.BrightText, visoarHighlightYellowRGB)
#         palette.setColor(QPalette.Highlight, visoarHighlightYellowRGB.lighter())
#         palette.setColor(QPalette.HighlightedText, Qt.white)
#         palette.setColor(QPalette.Disabled, QPalette.Text, Qt.lightGray)
#         palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.lightGray)
#         palette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.lightGray)
#         palette.setColor(QPalette.Background, Qt.white)
#         palette.setColor(QPalette.Foreground, visoarDarkGreenRGB)
#         palette.setColor(QPalette.PlaceholderText, Qt.white)
#         palette.setColor(QPalette.BrightText, visoarHighlightYellowRGB)
#         app.setPalette(palette)
#
#     # GuiModule.createApplication()
#     GuiModule.attach()
#
#     if DEBUG:
#         print('Main after attach')
#
#     # since I'm writing data serially I can disable locks
#     os.environ["VISUS_DISABLE_WRITE_LOCK"] = "1"
#     if DEBUG:
#         print('Main after VISUS_DISABLE_WRITE_LOCK')
#
#     if True:
#         # Create and display the splash screen
#         splash_pix = QPixmap('icons/visoar_logo.png')
#         # print('Error with Qt.WindowStaysOnTopHint')
#         splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
#         splash.setMask(splash_pix.mask())
#         splash.show()
#         if DEBUG:
#             print('Main after splash init')
#
#     if True:
#         print('Setting Fonts.... ' + str(QDir("Roboto")))
#         dir_ = QDir("Roboto")
#         _id = QFontDatabase.addApplicationFont("./Roboto-Regular.ttf")
#         print(QFontDatabase.applicationFontFamilies(_id))
#
#         font = QFont("Roboto")
#         font.setStyleHint(QFont.Monospace)
#         font.setPointSize(20)
#         print('ERROR: not sure how to set the font in ViSUS')
#         if DEBUG:
#             print('Main after fonts')
#
#     # app.setFont(font);
#
#     window = VisoarAgExplorerBatchProcess()
#     if DEBUG:
#         print('Main after visoar window')
#
#     window.show()
#     if DEBUG:
#         print('Main after window show')
#
#     # window.showMaximized()
#
#     if True:
#         splash.finish(window)
#     if DEBUG:
#         print('Main after splash close')
#
#     app.exec()
#     # GuiModule.execApplication()
#     if DEBUG:
#         print('Main after app exec')
#
#     # sys.stdout = _stdout
#     # sys.stderr = _stderr
#
#     # viewer=None
#     GuiModule.detach()
#     print("Main All done")
#
#
# # sys.exit(0)
#
# # //////////////////////////////////////////////
# if __name__ == '__main__':
#     Main(sys.argv)
#
# # 	<<project>
# # 	<projName> "Project2" </projName>
# # 	<dir> "/Users/amygooch/GIT/SCI/DATA/FromDale/ag1" </dir>
# # </project>
# # <<project>
# # 	<projName> "Project3" </projName>
# # 	<dir> "/Users/amygooch/GIT/SCI/DATA/TaylorGrant/rgb/" </dir>
# # </project>
