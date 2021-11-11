from VisoarSettings             import *
from datetime import datetime
from PyQt5.QtWebEngineWidgets         import QWebEngineView

from OpenVisus                        import *
from OpenVisus.gui                    import *

from PyQt5.QtGui                      import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFileDialog

from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem

from editUserLibrary			    import *
from VisoarStartTab			        import *
from VisoarNewTab			        import *
from VisoarNewTimeSeriesTab		    import *
from VisoarLoadTab			        import *
from VisoarStitchTab			    import *
from VisoarAnalyzeTab			    import *
from ViSOARUIWidget                 import *
from ViSOARQuickNDVI                import *
from slampy.sync_gui                import VisoarMoveDataWidget
from slampy.slam_2d                 import *
from slampy.slam_2d_gui             import *


# commented
# from slampy.slam_2d_gui     import *


from slam2dWidget 				import *
from gmail_visoar				import *

class MyViewerWidget(QWidget):
    def __init__(self, parent):
        #super().__init__()
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.setStyleSheet(LOOK_AND_FEEL)
        self.viewer = MyViewer()
        self.toolbar = QHBoxLayout()
        self.sublayout = QVBoxLayout()
        self.myGradientWidget = ViSOARGradientMapViewWidget(self, self.viewer )
        self.comboBoxATab = QComboBox(self)
        self.comboBoxATab.addItem("R G B")
        self.comboBoxATab.addItem("R G NIR")
        self.comboBoxATab.addItem("MapIR only (OCNIR)")
        self.comboBoxATab.addItem("NIR G B (agrocam)")
        self.comboBoxATab.addItem("R NIR (Sentera NDVI)")
        self.comboBoxATab.addItem("RedEdge NIR (Sentera NDRE)")
        self.comboBoxATab.addItem("Unknown")
        self.comboBoxATab.setStyleSheet(MY_COMBOX)
        self.comboBoxATab.currentIndexChanged.connect(self.inputModeChangedATab)
        #self.comboBoxATab.setCurrentIndex(self.parent.tabNewStitching.comboBoxNewTab.currentIndex())
        #print('combobox new tab: ' + str(self.parent.tabNewStitching.comboBoxNewTab.currentIndex()))
        self.comboBoxATab.setToolTip('Sensor/Image mode for input images')
        self.toolbar.addWidget(self.comboBoxATab)
        #self.comboBoxATab.setGeometry(200, 150, 200, 50)
        # self.comboBoxATab.setFixedSize(400, 100)
        # self.comboBoxATab.setFixedWidth(400)
        # self.comboBoxATab.setFixedHeight(100)
        # self.comboBoxATab.setMinimumContentsLength(100)

        width = self.comboBoxATab.minimumSizeHint().width()
        self.comboBoxATab.setMinimumWidth(width)

        #self.comboBoxATab.setSizePolicy(QSizePolicy.Preferred, self.comboBoxATab.sizePolicy().verticalPolicy())
        #self.comboBoxATab.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        #self.comboBoxATab.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.comboBoxATabScripts = QComboBox(self)
        # self.buttons.comboBoxATabScripts.setToolTip('Sensor/Image mode for input images')
        self.addScriptActionCombobox(self.comboBoxATabScripts)
        self.toolbar.addWidget(self.comboBoxATabScripts)
        self.comboBoxATab.setCurrentText("Unknown")

        self.openMyMapWidget = createPushButton("", lambda: self.addMyMapWidgetWindow(self.viewer))

        self.openLayersWindowBtn = createPushButton("",
                                                            lambda: self.openLayersWindow())
        self.openLayersWindowBtn.setIcon(QIcon('icons/LayersGreen.png'))
        fixButtonsLookFeel(self.openLayersWindowBtn)
        self.openLayersWindowBtn.setToolTip('View Layers controls')
        self.toolbar.addWidget(self.openLayersWindowBtn, alignment=Qt.AlignRight)

        self.toolbar.addStretch(10)

        self.openMyMapWidget.setIcon(QIcon('icons/palette.png'))
        fixButtonsLookFeel(self.openMyMapWidget)
        self.openMyMapWidget.setToolTip('Allows changing of color map used for NDVI/TGI scripts')
        self.toolbar.addWidget(self.openMyMapWidget, alignment=Qt.AlignRight)
        #self.toolbar.addStretch(10)

        self.resetViewBtn = createPushButton("", lambda: self.resetView())
        self.resetViewBtn.setToolTip('Reset Viewpoint to see full mosaic')
        self.resetViewBtn.setIcon(QIcon('icons/resetView.png'))
        fixButtonsLookFeel(self.resetViewBtn)
        #self.resetView.setStyleSheet(WHITE_PUSH_BUTTON)
        self.toolbar.addWidget(self.resetViewBtn, alignment=Qt.AlignRight)

        self.sublayout.addLayout(self.toolbar)

        self.myinit()
        self.sublayout.addWidget(self.viewer_subwin)
        self.setLayout(self.sublayout)

    def getNewImageForImageView(self):
        imagedataFilename = self.saveScreenshot(withDate=False)
        from PIL import Image
        image = numpy.array(Image.open(imagedataFilename)) #.astype(numpy.float32)
        image = numpy.swapaxes(image, 0, 1)
        self.myGradientWidget.imv.setImage(image)

    def saveScreenshot(self, withDate=True):
        if withDate:
            now = datetime.now()
            date_time = now.strftime("_%Y%m%d_%H%M%S")
        else:
            date_time = ''
        path = os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX')
        if not os.path.exists(path):
            os.makedirs(path)
        fileName = os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX', self.parent.projectInfo.projName + date_time + '.png')
        self.viewer.takeSnapshot(True, fileName)
        visoarLog(self.parent.visoarLogFile, 'saveScreenshot finished: ' + fileName)
        return fileName

    def setSensor(self, sensor):
        self.comboBoxATab.setCurrentText(sensor)
    # def hide(self):
    #     self.viewer_subwin.hide()
    #     self.openMyMapWidget.hide()
    #     self.comboBoxATab.hide()
    #     self.comboBoxATabScripts.hide()
    #
    # def show(self):
    #     self.viewer_subwin.show()
    #     self.openMyMapWidget.show()
    #     self.comboBoxATab.show()
    #     self.comboBoxATabScripts.show()

    def resetView(self):
        db = self.viewer.getDataset()
        if len(self.parent.visoarLayerList) > 0:
            for alayer in self.parent.visoarLayerList:
                # for all layers not google should do a union of all boxes
                if alayer.name != 'google' and db.getChild(alayer.name):
                    db2 = self.viewer2.getDataset()
                    # try:
                    #     if db:
                    #         db.setEnableAnnotations(False)
                    #     if db2:
                    #         db2.setEnableAnnotations(False)
                    # except:
                    #     print('Could not shut off annotations in ResetView')
                    box = db.getChild(alayer.name).getDatasetBounds().toAxisAlignedBox()
                    self.viewer.getGLCamera().guessPosition(box)
                    self.viewer2.getGLCamera().guessPosition(box)
                    return

        elif db.getChild("visus"):
            #db2 = self.viewer2.getDataset()
            # Causes a crash
            # db.setEnableAnnotations(False)
            # if (db2):
            #     db2.setEnableAnnotations(False)
            box = db.getChild("visus").getDatasetBounds().toAxisAlignedBox()
            self.viewer.getGLCamera().guessPosition(box)
            #self.viewer2.getGLCamera().guessPosition(box)
        else:
            self.viewer.guessGLCameraPosition()
            #self.viewer2.guessGLCameraPosition()

    def openLayersWindow(self):
        v = VisoarLayerView(self.parent, self.parent.visoarLayerList, self.viewer)
        v.show()
        v.raise_()
        v.activateWindow()

    def addMyMapWidgetWindow(self, viewer):
        self.getNewImageForImageView()
        self.myGradientWidget.show()
        self.myGradientWidget.raise_()
        self.myGradientWidget.activateWindow()

    def runThisScript(self, script, viewer):
        fieldname = "output=ArrayUtils.interleave(ArrayUtils.split(voronoi())[0:3])"
        viewer.setFieldName(fieldname)
        viewer.setScriptingCode(script)
        self.getNewImageForImageView()
        self.myGradientWidget.update()

    def myinit(self):
        self.viewer.setMinimal()
        self.cam = self.viewer.getGLCamera()

        # disable smoothing
        if isinstance(self.cam, GLOrthoCamera): self.cam.toggleDefaultSmooth()
        self.viewer_subwin = sip.wrapinstance(FromCppQtWidget(self.viewer.c_ptr()), QtWidgets.QMainWindow)

    def addScriptActionCombobox(self, cbox):
        if (self.parent.scriptNames):
            for item in self.parent.scriptNames:
                cbox.addItem(item)
            cbox.setToolTip('Available scripts')
            cbox.setStyleSheet(MY_COMBOX)
            cbox.currentIndexChanged.connect(partial(self.loadScript, cbox))

    def loadScript(self, cbox):
        print('FUNCTION  Load Script...')
        scriptName = cbox.currentText()
        print(scriptName)
        if scriptName == "Original" or scriptName == "Unknown":
            print('\tShow Original')
            self.viewer.setScriptingCode(
                """
                output=input
                """.strip())
            # cbox.setText('output = input')
            return
        # self.app_dir = os.getcwd()
#        if self.comboBoxATab.currentText() == 'R G B':
#            scriptName = 'TGI_normalized'
        if self.comboBoxATab.currentText() == 'R NIR (Sentera NDVI)':
            scriptName = 'NDVI_Sentera'
#        elif self.comboBoxATab.currentText() == 'MapIR only (OCNIR)':
 #           scriptName = 'NDVI_MAPIR'
        elif self.comboBoxATab.currentText() == 'RedEdge NIR (Sentera NDRE)':
            scriptName = 'NDRE_Sentera'
        else:
            scriptName = cbox.currentText()
        script = getTextFromScript(os.path.join(self.parent.app_dir, 'scripts', scriptName + '.py'))
        print('\tGot script content is: ')
        print(script)
        if script:
            fieldname = "output=ArrayUtils.interleave(ArrayUtils.split(voronoi())[0:3])"
            print("Running script ")

            # self.viewer.setFieldName(fieldname)
            # self.viewer.setScriptingCode(script)
            self.viewer.setFieldName(fieldname)
            self.viewer.setScriptingCode(script)

    def inputModeChangedATab(self):
        self.parent.inputMode = self.comboBoxATab.currentText()

        if (self.parent.inputMode == "R G B"):
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR_normalized', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Agrocam', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Threshold', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_normalized', True)
        elif (self.parent.inputMode == "Unknown"):
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR_normalized', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Agrocam', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_normalized', True)
        elif (self.parent.inputMode == "MapIR only (OCNIR)"):
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR_normalized', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Agrocam', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_Threshold', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_normalized', False)
        elif (self.parent.inputMode == "R NIR (Sentera NDVI)"):
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR_normalized', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Agrocam', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_Threshold', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_normalized', False)
        elif (self.parent.inputMode == "RedEdge NIR (Sentera NDRE)"):
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR_normalized', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Agrocam', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_Threshold', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_normalized', False)
        elif (self.parent.inputMode == "R G NIR"):
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_MAPIR_normalized', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Agrocam', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'NDVI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_Threshold', False)
            self.parent.setEnabledCombobxItem(self.comboBoxATabScripts, 'TGI_normalized', False)

        #self.parent.inputModeChanged()


class MyViewer(Viewer):
    # constructor
    def __init__(self, name="", url=""):
        super(MyViewer, self).__init__()
        super(MyViewer, self).setMinimal()

        prefs = ViewerPreferences()
        prefs.panels = ""
        self.setPreferences(prefs)
        self.name = name
        self.setBackgroundColor( Color(0, 0, 0, 255))
        if url:
            try:
                self.open(url)
            except:
                popUP('Error', 'Error ViSOARUIWidget 280 loading: {0}'.format(url))

        self.on_camera_change = None

    # glCameraChangeEvent
    def glCameraChangeEvent(self):
        super(MyViewer, self).glCameraChangeEvent()
        if self.on_camera_change:
            self.on_camera_change()

def visoarLog(f,msg):
    from datetime import datetime
    if f is not None:
        f.write("%s %s, 1\n" % (str(datetime.now())[0:-7] ,msg,))
        f.flush()


class ViSOARUIWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.DEBUG = True
        self.BATCH_MODE = False

        self.layout = QVBoxLayout(self)
        self.app_dir = os.getcwd()

        self.USER_TAB_UI = False
        self.visoarLayerList = []
        self.START_TAB = 0
        self.NEW_STITCH_TAB = 1
        self.NEW_TIME_SERIES_TAB = 2
        self.LOAD_TAB = 3
        self.STITCHING_VIEW_TAB = 4
        self.ANALYTICS_TAB = 5
        self.ASKSENSOR_TAB = 6
        self.ASKSOURCE_TAB = 7
        self.ASKNAME_TAB = 8
        self.ASKDEST_TAB = 9
        self.ASKSOURCERGBNDVI_TAB = 10
        self.MOVE_DATA_TAB = 11
        self.QUICK_NDVI_TAB = 12
        self.LOG_TAB = 13

        self.copySourceBool = False
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

        self.generate_bbox = False
        self.color_matching = False
        self.blending_exp = "output=voronoi()"
        self.stitchTime = "0"
        self.stitchNumImages = 0

        self.dir_of_rgb_source = "/Volumes/ViSUSAg/DirOfDirs"
        self.dir_of_nir_source = ""
        self.dir_of_result = "/Volumes/ViSUSAg/OutputOfDirOfDirs"

        self.loadWidgetDict = {}
        self.loadLabelsWidgetDict = {}
        self.DEBUG = True
        self.ADD_VIEWER = True  # Flag for removing viewers for testing
        self.visoarLogFilePath = os.path.join(os.getcwd(), "~visoarLog.txt")
        self.visoarLogFile = open(self.visoarLogFilePath, "w")
        print(os.path.join(os.getcwd(), "~visoarLog.txt"))
        visoarLog(self.visoarLogFile, 'Start Log: ')

        if os.path.exists(self.userFileHistory):
            visoarLog(self.visoarLogFile, 'All app settings will be saved to: ' + self.userFileHistory)
        else:
            f = open(self.userFileHistory, "wt")
            today = datetime.now()
            todayFormated = today.strftime("%Y%m%d_%H%M%S")
            f.write('<data>\n' +
                    '\t<project>\n' +
                    '\t\t<projName>TestData</projName>\n' +
                    '\t\t<projDir>./data/TestData</projDir>\n' +
                    '\t\t<srcDir>./data/TestData</srcDir>\n' +
                    '\t\t<createdAt>' + todayFormated + '</createdAt>\n' +
                    '\t\t<updatedAt>' + todayFormated + '</updatedAt>\n' +
                    '\t</project>\n' +
                    '</data>\n\n\n\n')
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

        if self.ADD_VIEWER:
            self.slam_widget = Slam2DWidgetForVisoar()
            self.slam = Slam2D()
            #self.redirect_log.setCallback(self.slam.printLog)
            print("Log from ViSOARUIWidget....")
            self.slam.enable_svg = False

            #self.slam_widget.slam = self.slam


        self.visoarUserLibraryData = VisoarUserLibraryData(self.userFileHistory)

        self.tabAskSensor = VisoarAskSensor(self)
        self.tabAskSource = VisoarAskSource(self)
        self.tabAskSourceRGBNDVI = VisoarAskSourceRGBNDVI(self)
        self.tabAskName = VisoarAskName(self)
        self.tabAskDest = VisoarAskDest(self)

        self.tabStart = VisoarStartTabWidget(self)  # QWidget()
        self.tabNewStitching = VisoarNewTabWidget(self)  # QWidget()
        self.tabNewTimeSeries = VisoarNewTimeSeriesTabWidget(self)  # QWidget()
        self.tabLoad = VisoarLoadTabWidget(self)  # QWidget()

        #self.tabBatchProcess = VisoarBatchProcessWidget(self)  # QWidget()
        self.tabMoveDataFromCards = VisoarMoveDataWidget(self)  # QWidget()
        self.tabQuickNDVI = VisoarQuickNDVIWidget(self)  # QWidget()

        if self.ADD_VIEWER:
            self.tabStitcher = VisoarStitchTabWidget(self)  # QWidget()
            self.tabViewer = VisoarAnalyzeTabWidget(self)  # QWidget()


        self.logTab = QTextEdit()
        self.logTab.setLineWrapMode(QTextEdit.NoWrap)
        self.logTab = QTextEdit(self, readOnly=True)
        self.logTab.ensureCursorVisible()
        self.logTab.setLineWrapColumnOrWidth(500)
        self.logTab.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.logTab.setFixedWidth(400)
        self.logTab.setFixedHeight(150)
        self.logTab.move(30, 100)

        # self.ASKSENSOR_TAB = 0
        # self.ASKSOURCE_TAB = 1
        # self.ASKSOURCERGBNDVI_TAB = 2
        # self.ASKDEST_TAB = 3
        # self.LOG_TAB = 4
        # self.LOAD_TAB = 5
        # self.ANALYTICS_TAB = 6
        # self.START_TAB = 7

        self.leftlist = QListWidget()
        self.leftlist.insertItem(self.START_TAB, 'Start')
        self.leftlist.insertItem(self.NEW_STITCH_TAB, 'One Screen New')
        self.leftlist.insertItem(self.NEW_TIME_SERIES_TAB, 'Create Time Series')
        self.leftlist.insertItem(self.LOAD_TAB, 'Load Dataset')
        self.leftlist.insertItem(self.STITCHING_VIEW_TAB, 'Stich Moasic')
        self.leftlist.insertItem(self.ANALYTICS_TAB, 'Viewer')
        self.leftlist.insertItem(self.ASKSENSOR_TAB, 'Sensor')
        self.leftlist.insertItem(self.ASKSOURCE_TAB, 'Image Directory')
        self.leftlist.insertItem(self.ASKNAME_TAB, 'Project Name')
        self.leftlist.insertItem(self.ASKDEST_TAB, 'Save Directory')
        self.leftlist.insertItem(self.ASKSOURCERGBNDVI_TAB, 'RGB and NDVI Image Directory')
        self.leftlist.insertItem(self.MOVE_DATA_TAB, 'Move Data from Drone Cards')
        self.leftlist.insertItem(self.QUICK_NDVI_TAB, 'Quick NDVI of images')
        self.leftlist.currentRowChanged.connect(self.display)

        # use stack
        self.tabs = QStackedWidget()
        self.tabs.addWidget(self.tabStart)
        self.tabs.addWidget(self.tabNewStitching)
        self.tabs.addWidget(self.tabNewTimeSeries)
        self.tabs.addWidget(self.tabLoad)
        self.tabs.addWidget(self.tabStitcher)
        self.tabs.addWidget(self.tabViewer)
        self.tabs.addWidget(self.tabAskSensor)
        self.tabs.addWidget(self.tabAskSource)
        self.tabs.addWidget(self.tabAskName)
        self.tabs.addWidget(self.tabAskDest)
        self.tabs.addWidget(self.tabAskSourceRGBNDVI)
        self.tabs.addWidget(self.tabMoveDataFromCards)
        self.tabs.addWidget(self.tabQuickNDVI)
        self.tabs.addWidget(self.logTab)

        self.tabs.setCurrentIndex(0)

        self.layout.addWidget(self.tabs)
        # _stdout = sys.stdout
        # _stderr = sys.stderr
        print('Amy add logging...')
        #logger = Logger(terminal=sys.stdout, filename="~visusslam.log", qt_callback=self.printLog)
        # sys.stdout = logger
        # sys.stderr = logger

        if self.DEBUG:
            visoarLog(self.visoarLogFile, 'ViSOARTabWidget init finished')

    def getSrcDir(self, RGB=True ):
        if (RGB):
            return self.projectInfo.srcDir
        else:
            return self.projectInfo.srcDirNDVI
    def getProjDir(self, RGB=True, TIMESERIES = False):
        if TIMESERIES or RGB:
            return self.projectInfo.projDir
        else:
            return self.projectInfo.projDirNDVI

    def getCacheDir(self, RGB=True, TIMESERIES = False):
        if TIMESERIES:
            return os.path.join(self.projectInfo.projDir, 'VisusSlamFiles')
        else:
            return os.path.join(self.projectInfo.srcDir, 'VisusSlamFiles')
    def getMidxPath(self, RGB=True, TIMESERIES = False):
        if (RGB):
            return os.path.join(self.projectInfo.srcDir, 'VisusSlamFiles', 'visus.midx')
        else:
            return os.path.join(self.projectInfo.projDir, 'VisusSlamFiles', 'visus.midx')
    def getGoogleMidxPath(self, RGB=True, TIMESERIES = False):
        if (RGB):
            return os.path.join(self.projectInfo.srcDir, 'VisusSlamFiles', 'google.midx')
        else:
            return os.path.join(self.projectInfo.projDir, 'VisusSlamFiles', 'google.midx')



#Three Cases:
    # if RGB and NDVI
    # then midx holds both and is in projdir
    #  each dataset's midx is in srcdir and srcdirndvi
    # if Time series:
    # then midx holds both and is in projdir
    #  each dataset's midx referenced in that midx
    # just single, then srcdir, srcdir, cachedir = srcdir/VisusSlamFiles


    def display(self, i):
        self.tabs.setCurrentIndex(i)

    def next(self, s):
        #implement next button on stacked view, s = current tab, need to move to what comes next
        if s=='goToLoadData':
            visoarLog(self.visoarLogFile, 'LoadData')
            self.tabs.setCurrentIndex(self.LOAD_TAB)
        elif s=='goToTimeSeries':
            visoarLog(self.visoarLogFile, 'TimeSeries')
            self.tabs.setCurrentIndex(self.NEW_TIME_SERIES_TAB )
        elif s=='AfterAskSensor':
            self.inputMode = self.tabAskSensor.comboBoxNewTab.currentText()
            visoarLog(self.visoarLogFile, 'AfterAskSensor')
            if self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam' or self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB':
                self.tabAskSource.curDir.setHidden(True)
                self.tabAskSource.curDir2.setHidden(True)
                self.tabAskSource.buttonAddImagesSource.setHidden(True)
                self.tabAskSource.mapirCalibrationWidget.setHidden(False)
                self.tabAskSource.mapirCalibrationWidget.on_show()
                self.tabs.setCurrentIndex(self.ASKSOURCERGBNDVI_TAB)
            else:
                if (self.tabAskSensor.comboBoxNewTab.currentText() == 'MapIR only (OCNIR)'):
                    self.tabAskSource.curDir.setHidden(True)
                    self.tabAskSource.curDir2.setHidden(True)
                    self.tabAskSource.buttonAddImagesSource.setHidden(True)
                    self.tabAskSource.mapirCalibrationWidget.setHidden(False)
                    self.tabAskSource.mapirCalibrationWidget.on_show()
                self.tabs.setCurrentIndex(self.ASKSOURCE_TAB)
            if self.BATCH_MODE:
                self.tabAskSource.curDir2.setText(self.dir_of_rgb_source)
                self.tabAskDest.destNametextbox.setText(self.dir_of_result)
        elif s == 'AfterAskSource':
            if self.BATCH_MODE:
                self.dir_of_rgb_source = self.tabAskSource.curDir2.text()
                if self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam' or (self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
                    self.dir_of_nir_source = self.tabAskSource.curDir2.text()
                    visoarLog(self.visoarLogFile, 'AfterAskSource')
                    if (not self.dir_of_rgb_source.strip()) or (not self.dir_of_nir_source):
                        errorStr = 'Please Provide both RGB and NDVI directories or go back home and use a different sensor type\n'
                        self.tabAskSource.createErrorLabel.setText(errorStr)
                    else:
                        tempName = ''  # os.path.basename(os.path.normpath(self.dir_of_rgb_source.strip()))
                        # self.tabAskName.projNametextbox.setText(tempName)
                        self.projectInfo.projName = tempName
                        self.tabAskDest.destNametextbox.setText('')
                        #self.tabs.setCurrentIndex(self.ASKDEST_TAB)
                        self.tabs.setCurrentIndex(self.LOG_TAB)
                        self.update()

                        if self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam' or (
                                self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
                            self.dir_of_result = self.destNametextbox
                            # self.projectInfo.projDir = self.projectInfo.srcDir
                            # self.projectInfo.projDirNDVI = self.projectInfo.srcDirNDVI

                        self.startProcessing()
                else:
                    visoarLog(self.visoarLogFile, 'AfterAskSource')
                    if not self.dir_of_rgb_source.strip():
                        errorStr = 'Please Provide a directory of directories of images \n'
                        self.tabAskSource.createErrorLabel.setText(errorStr)
                    else:
                        tempName = ''  # os.path.basename(os.path.normpath(self.dir_of_rgb_source.strip()))
                        # self.tabAskName.projNametextbox.setText(tempName)
                        self.projectInfo.projName = tempName
                        self.tabAskDest.destNametextbox.setText('')
                        #self.tabs.setCurrentIndex(self.ASKDEST_TAB)
                        self.tabs.setCurrentIndex(self.LOG_TAB)
                        self.update()

                        if self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam' or (
                                self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
                            self.dir_of_result = self.destNametextbox
                            # self.projectInfo.projDir = self.projectInfo.srcDir
                            # self.projectInfo.projDirNDVI = self.projectInfo.srcDirNDVI

                        self.startProcessing()
            else:
                if self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam' or (self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
                    visoarLog(self.visoarLogFile, 'AfterAskSource')
                    if not self.projectInfo.srcDir.strip() or not self.projectInfo.srcDirNDVI.strip():
                        errorStr = 'Please Provide both RGB and NDVI directories or go back home and use a different sensor type\n'
                        self.tabAskSource.createErrorLabel.setText(errorStr)
                    else:
                        tempName = datetime.now().strftime("%Y%m%d-%H%M%S_")+os.path.basename(os.path.normpath(self.projectInfo.srcDir))
                        self.tabAskName.projNametextbox.setText(tempName)
                        self.projectInfo.projName = tempName
                        self.tabAskDest.destNametextbox.setText(self.projectInfo.srcDir.strip())
                        self.projectInfo.projDir = self.projectInfo.srcDir.strip()
                        self.projectInfo.projDirNDVI = self.projectInfo.srcDirNDVI.strip()
                        self.projectInfo.cache_dir = self.getCacheDir(  TIMESERIES = True) # os.path.join(self.projectInfo.projDir, 'VisusSlamFiles')
                        self.tabs.setCurrentIndex(self.ASKNAME_TAB)
                else:
                    visoarLog(self.visoarLogFile, 'AfterAskSource')
                    if not self.projectInfo.srcDir.strip():
                        errorStr = 'Please Provide a directory of images or click on the load tab to load a dataset you\'ve already stitched\n'
                        self.tabAskSource.createErrorLabel.setText(errorStr)
                    else:
                        tempName = datetime.now().strftime("%Y%m%d-%H%M%S_")+os.path.basename(os.path.normpath(self.projectInfo.srcDir))
                        self.tabAskName.projNametextbox.setText(tempName)
                        self.projectInfo.projName = tempName
                        self.tabAskDest.destNametextbox.setText(self.projectInfo.srcDir.strip())
                        self.projectInfo.projDir = self.projectInfo.srcDir.strip()
                        self.projectInfo.cache_dir = self.getCacheDir(TIMESERIES = True)
                        self.tabs.setCurrentIndex(self.ASKNAME_TAB)

        elif s == 'AfterAskName':
            v = self.setProjName()
            if v:
                if self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam' or (
                        self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
                    self.tabs.setCurrentIndex(self.ASKDEST_TAB)
                else:
                    self.projectInfo.projDir = self.projectInfo.srcDir
                    self.projectInfo.cache_dir = self.getCacheDir(TIMESERIES=False)
                    self.afterAskDestFn()
            visoarLog(self.visoarLogFile, 'AfterAskName')
            #self.tabAskName.projNametextbox.setText('')

        elif s == 'AfterAskDest':
            if self.BATCH_MODE:
                self.tabs.setCurrentIndex(self.LOG_TAB)
                self.update()

                if self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam' or (self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
                    self.dir_of_result = self.destNametextbox
                    # self.projectInfo.projDir = self.projectInfo.srcDir
                    # self.projectInfo.projDirNDVI = self.projectInfo.srcDirNDVI

                self.startProcessing()
            else:
                if self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam' or (self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
                    self.saveDir = self.projectInfo.projDir
                    #self.projectInfo.projDir = self.projectInfo.srcDir
                    #self.projectInfo.projDirNDVI = self.projectInfo.srcDirNDVI


                    if (not self.saveDir == self.projectInfo.srcDir) and (not  self.saveDir == self.projectInfo.srcDirNDVI):
                        if (self.projectInfo.projDir != self.projectInfo.srcDir):
                            if not (os.path.basename(self.projectInfo.projDir) == self.projectInfo.projName):
                                self.projectInfo.projDir = os.path.join(self.projectInfo.projDir, self.projectInfo.projName)

                            if not os.path.exists(self.projectInfo.projDir):
                                os.makedirs(self.projectInfo.projDir)
                        self.afterAskDestFn(   IS_TIMESERIES = True)
                        # self.visoarUserLibraryData.createProject(self.projectInfo.projName,
                        #                                          self.projectInfo.projDir,
                        #                                          self.projectInfo.srcDir,
                        #                                          self.projectInfo.projDirNDVI,
                        #                                          self.projectInfo.srcDirNDVI)
                        # self.changeViewStitching()
                        # print("Note to self, taking out slam default changes")
                        # #self.slam_widget.setDefaults(generate_bbox=self.generate_bbox,
                        # #                             color_matching=self.color_matching, blending_exp=self.blending_exp)
                        # self.tabs.setCurrentIndex(self.STITCHING_VIEW_TAB)
                        #
                        # # if self.stitchAlreadyDone():
                        # #     self.enableViewStitching()
                        # #     self.goToAnalyticsTab()
                        # # else:
                        # self.enableViewStitching()
                        # self.changeViewStitching()
                        # self.startViSUSSLAM()
                    else:
                        errorStr = 'Please Provide a unique directory for the destination, different from RGB or NDVI source directories  \n'
                        self.tabAskDest.createErrorLabel.setText(errorStr)
                        return
                elif not self.projectInfo.projDir.strip():
                    print(self.projectInfo.projDir)
                    errorStr = 'Please Provide a directory  \n'
                    #print('Fix me...')
                    self.tabAskDest.createErrorLabel.setText(errorStr)
                    return
                else:
                    if (self.projectInfo.projDir != self.projectInfo.srcDir):
                        if not (os.path.basename(self.projectInfo.projDir) == self.projectInfo.projName):
                            self.projectInfo.projDir = os.path.join(self.projectInfo.projDir, self.projectInfo.projName)

                        if not os.path.exists(  self.projectInfo.projDir ):
                            os.makedirs(self.projectInfo.projDir )

                    self.afterAskDestFn()

                visoarLog(self.visoarLogFile, 'end of AfterAskDest')
                #self.tabAskDest.destNametextbox.setText('')
                #self.tabAskName.projNametextbox.setText('')
                #self.tabAskSource.curDir2.setText('')

        elif s == 'AfterStitching':
            self.tabs.setCurrentIndex(self.ANALYTICS_TAB)
        else:
            print(s)

    def afterAskDestFn(self,  IS_TIMESERIES = False):
        self.visoarUserLibraryData.createProject(self.projectInfo.projName,
                                                 self.projectInfo.projDir,
                                                 self.projectInfo.srcDir,
                                                 self.projectInfo.projDirNDVI,
                                                 self.projectInfo.srcDirNDVI, sensorMode=self.inputMode)
        # self.enableViewStitching()
        self.changeViewStitching()
        # AAG Slam removal
        # self.slam_widget.setDefaults(generate_bbox=self.generate_bbox,
        #                                    color_matching=self.color_matching, blending_exp=self.blending_exp)
        self.tabs.setCurrentIndex(self.STITCHING_VIEW_TAB)
        # if   self.stitchAlreadyDone(IS_TIMESERIES):
        #     self.enableViewStitching()
        #     self.goToAnalyticsTab()
        # else:
        self.enableViewStitching()
        self.changeViewStitching()
        self.startViSUSSLAM()
    #
    # def stitchAlreadyDone(self,IS_TIMESERIES):
    #     if IS_TIMESERIES:
    #         return os.path.exists(os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles', 'visus.midx'))
    #     else:
    #
    #     return os.path.exists(os.path.join( dir,  'idx', '0000.bin'))

    #Part of batch processing
    def startProcessing(self):

        #PreProcessing
        #If mapIR images, use target to preprocess
        if (self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB') or (self.tabAskSensor.comboBoxNewTab.currentText() == 'MapIR only (OCNIR)'):
            outdir = self.tabAskSource.mapirCalibrationWidget.calibrateMapIRImages()
            self.projectInfo.srcDir = outdir

        for aSrcPath in os.listdir(self.dir_of_rgb_source):
            self.projectInfo.srcDir = os.path.join(self.dir_of_rgb_source, aSrcPath)
            if os.path.isdir(self.projectInfo.srcDir):
                print(self.projectInfo.srcDir)
                self.projectInfo.projDir = self.projectInfo.srcDir
                self.projectInfo.projName = os.path.basename(os.path.normpath(self.projectInfo.srcDir))
                # self.projectInfo.projDirNDVI =
                # self.projectInfo.srcDirNDVI =

                self.projectInfo.cache_dir = os.path.join(self.projectInfo.projDir, 'VisusSlamFiles')
                if not os.path.exists(self.projectInfo.cache_dir):
                    os.makedirs(self.projectInfo.cache_dir)
                if not os.path.exists(os.path.join(self.projectInfo.cache_dir, 'visus.midx')):
                    self.setAndRunSlam(self.projectInfo.srcDir, cache_dir=self.projectInfo.cache_dir)

                    self.visoarUserLibraryData.createProject(self.projectInfo.projName,
                                                             self.projectInfo.projDir,
                                                             self.projectInfo.srcDir,
                                                             self.projectInfo.projDirNDVI,
                                                             self.projectInfo.srcDirNDVI,sensorMode=self.parent.inputMode)
                else:
                    print(self.projectInfo.cache_dir + ' MIDX already exists..')
                    buttonReply = QMessageBox.question(self, 'Already Exists',
                                                       "MIDX already exists, would you like to restitch it?",
                                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if buttonReply == QMessageBox.Yes:
                        self.setAndRunSlam(self.projectInfo.srcDir, cache_dir=self.projectInfo.cache_dir)

                        self.visoarUserLibraryData.createProject(self.projectInfo.projName,
                                                                 self.projectInfo.projDir,
                                                                 self.projectInfo.srcDir,
                                                                 self.projectInfo.projDirNDVI,
                                                                 self.projectInfo.srcDirNDVI,sensorMode=self.parent.inputMode)


        # Load Load screen and enable viewer
        self.tabViewer.buttons.comboBoxATab.setCurrentIndex(self.tabAskSensor.comboBoxNewTab.currentIndex())
        import time
        time.sleep(3)

        self.tabs.setCurrentIndex(self.LOAD_TAB)
        self.update()

    def emailTrouble(self, logfile):
        from io import StringIO
        import logging
        visoarLog(self.visoarLogFile, 'dumping IO due to exception')
        log_stream = StringIO()
        logging.basicConfig(stream=log_stream, level=logging.INFO)
        logging.error("Exception occurred", exc_info=True)
        send_email_crash_notification(log_stream.getvalue(), logfile)



    def setAndRunSlam(self, image_dir, cache_dir=None, telemetry=None, plane=None, calibration=None,
                      physic_box=None):
        self.slam = None
        start = time.time()
        self.slam = Slam2D()
        self.slam.enable_svg = False

        if (  os.path.exists(cache_dir)) and (os.path.exists(os.path.join(cache_dir, 'idx', '0000.bin'))):
            buttonReply = QMessageBox.question(self, 'Already Exists',
                                               "MIDX already exists, would you like to restitch it?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                #       if  (not os.path.exists(cache_dir)) or (not os.path.exists(os.path.join(cache_dir, 'idx', '0000.bin'))):
                try:
                    self.slam.setImageDirectory(image_dir = image_dir,  cache_dir= cache_dir, telemetry=telemetry, plane=plane, calibration=calibration, physic_box=physic_box)
                     #Here we could ask whether you want to restitch or use old stitch
                    retSlamSetup = self.slam_widget.run(self.slam)
                    self.slam_widget.onRunClicked()
                    retSlamRan = self.slam_widget.slam.run()
                except:
                    self.emailTrouble(self.visoarLogFile)
            else:
                self.slam_widget.slam = self.slam
        else:
            try:
                self.slam.setImageDirectory(image_dir=image_dir, cache_dir=cache_dir, telemetry=telemetry, plane=plane,
                                            calibration=calibration, physic_box=physic_box)
                # Here we could ask whether you want to restitch or use old stitch
                retSlamSetup = self.slam_widget.run(self.slam)
                self.slam_widget.onRunClicked()
                retSlamRan = self.slam_widget.slam.run()
            except:
                self.emailTrouble(self.visoarLogFile)

        end = time.time()
        print(end - start)
        self.stitchTime = "{:.2f}".format((end - start)/60.0)
        self.stitchNumImages = len(self.slam.images)
        self.logTab.clear()
        if os.path.exists("~visusslam.log"):
            f2 = open("~visusslam.log", 'r')
            # appending the contents of the stitching log to the visoar log
            self.visoarLogFile.write(f2.read())
            f2.close()

        #self.setUpRClone()
        #These run functions above should return values of success.. but they don't
        return True, True #, end - start

    def createRGBNDVI_MIDX(self):
        # This function assumes that slam has been run on teh RGB and NDVI directories, resulting in two MIDX files
        # Now we combine these together in one MIDX file
        self.projectInfo.cache_dir =  self.getCacheDir(TIMESERIES=True) #os.path.join(self.projectInfo.projDir, 'VisusSlamFiles')
        self.listOfMidxFiles = []
        self.listOfMidxFiles.append(os.path.join(self.projectInfo.srcDir, 'VisusSlamFiles', 'visus.midx'))
        self.listOfMidxFiles.append(os.path.join(self.projectInfo.srcDirNDVI, 'VisusSlamFiles','visus.midx'))
        #self.saveDir = self.projectInfo.projDir
        #    def createTimeSeries(self):
        if len(self.listOfMidxFiles) > 1 and self.saveDir:

            # create file
            # visus.midx
            dataset = ET.Element('dataset',
                                 {'name': 'visus',
                                  'typename': 'IdxMultipleDataset'
                                  })

            field = ET.SubElement(dataset, 'field',
                                  {'name': 'voronoi',
                                   })
            code = ET.SubElement(field, 'code').text = 'output=voronoi()'

            googlemidx = ET.SubElement(dataset, 'dataset',
                                       {'name': 'google',
                                        'typename': 'GoogleMapsDataset',
                                        'tiles': 'http://mt1.google.com/vt/lyrs=s',
                                        'physic_box': '0.0 1.0 0.0 1.0'})
            i = 0
            for midx in self.listOfMidxFiles:
                i = i + 1
                dir, namestr, ext = getNameFromMIDX(midx)
                amidx = ET.SubElement(dataset, 'dataset',
                                      {'name': namestr,
                                       'url': midx,
                                       })

            # Add entry in load page
            #self.projectInfo.projName = self.buttons.projNametextbox.text()

            # make dir Name
            if not os.path.exists(os.path.join(self.saveDir, self.projectInfo.projName)):
                os.makedirs(os.path.join(self.saveDir, self.projectInfo.projName))
            # make dir VisusSlamFiles
            if not os.path.exists(os.path.join(self.saveDir, self.projectInfo.projName, 'VisusSlamFiles')):
                os.makedirs(os.path.join(self.saveDir, self.projectInfo.projName, 'VisusSlamFiles'))

            pretty_print_xml_given_root(ET.ElementTree(dataset).getroot(),os.path.join(self.saveDir, self.projectInfo.projName, 'VisusSlamFiles', 'visus.midx'))
            # ET.ElementTree(dataset).write(
            #     os.path.join(self.saveDir, self.projectInfo.projName, 'VisusSlamFiles', 'visus.midx'))

            self.projectInfo.projDir = os.path.join(self.saveDir, self.projectInfo.projName)
            # self.visoarUserLibraryData.createProject(self.projectInfo.projName,
            #                                                 self.projectInfo.projDir,
            #                                                 self.projectInfo.projDir,
            #                                                 self.projectInfo.projDirNDVI,
            #                                                 self.projectInfo.srcDirNDVI,
            #
            #                                                 )

            # open analytics
            self.goToAnalyticsTab()

    def setSensor(self, st):
        self.inputMode = st

    # def setDestName(self):
    #     self.projectInfo.projDir = str(
    #         QFileDialog.getExistingDirectory(self, "Select Directory containing Images"))
    #     self.tabAskDest.destNametextbox.setText(dir)
    #     self.tabAskDest.buttons.create_project.show()
    #     self.update()
    #
    #     if self.DEBUG:
    #         print('Images Added')

    def checkSpecialChar(self, text):
        return self.check_splcharacter(text)


    def checkNameOriginal(self, name):
        return self.visoarUserLibraryData.isUniqueName(name)

    def setProjName(self):
        self.projectInfo.projName = self.tabAskName.projNametextbox.text()
        self.projectInfo.projName = self.checkSpecialChar(self.projectInfo.projName )
        checkName = self.checkNameOriginal(self.projectInfo.projName)

        if  (not self.projectInfo.projName.strip() == "") and checkName:
            self.tabAskName.buttons.nextBtn.show()
            return True
        else:
            errorStr = 'Please provide a unique name for your project'
            self.tabAskName.createErrorLabel.setText(errorStr)
            return False
        self.update()

    def addImages(self):
        if self.BATCH_MODE:
            # if self.DEBUG:
            visoarLog(self.visoarLogFile, 'DEBUG: will create Project')
            self.dir_of_rgb_source = str(
                QFileDialog.getExistingDirectory(self, "Select Directory containing Images"))
            # self.projectInfo.projDir = self.projectInfo.srcDir
            print(self.dir_of_rgb_source)
            self.tabAskSource.curDir2.setText(self.dir_of_rgb_source)
            self.tabAskSource.buttonAddImagesSource.setStyleSheet(WHITE_PUSH_BUTTON)
            self.tabAskSource.buttonAddImagesSource.setText('Edit Directory')
            self.tabAskSource.buttons.nextBtn.show()
            self.update()
        else:
            # if self.DEBUG:
            visoarLog(self.visoarLogFile, 'DEBUG: will create Project')
            self.projectInfo.srcDir = str(
                QFileDialog.getExistingDirectory(self, "Select Directory containing Images"))
            #self.projectInfo.projDir = self.projectInfo.srcDir
            self.projectInfo.srcDir = self.checkSpecialChar(self.projectInfo.srcDir)
            print(self.projectInfo.srcDir)
            self.tabAskSource.curDir2.setText(self.projectInfo.srcDir)
            self.tabAskSource.buttonAddImagesSource.setStyleSheet(WHITE_PUSH_BUTTON)
            self.tabAskSource.buttonAddImagesSource.setText('Edit Directory')
            self.tabAskSource.buttons.nextBtn.show()
            self.update()
            # if ((not (self.parent.projectInfo.projDir.strip() == "")) and (not (self.parent.projectInfo.projName.strip() == ""))):
            #     self.parent.tabs.setTabEnabled(2, True)
            #     # self.tabs.setTabEnabled(3,True)
            #     self.parent.tabs.setCurrentIndex(2)
            #     if self.DEBUG:
            #         print('DEBUG: will create Project')
            #     #self.createProject()
            # else:
            errorStr = ''

    # @pyqtSlot()
    def onChange(self, i):  # changed!
        if i == self.STITCHING_VIEW_TAB:
            if not self.projectInfo.projDir:
                visoarLog(self.visoarLogFile, 'Project Directory is null')
                mb, ybtn, nbtn, abtn, cbtn = self.getLoadDataFirst(' ')
                ret = mb.exec()
                if mb.clickedButton() == abtn:
                    print('press action')
                    self.tabs.setCurrentIndex(self.LOAD_TAB)
                elif mb.clickedButton() == ybtn:
                    print('press yes')
                    self.tabs.setCurrentIndex(self.NEW_STITCH_TAB)
                elif mb.clickedButton() ==nbtn:
                    print('press no')
                    self.tabs.setCurrentIndex(self.NEW_TIME_SERIES_TAB)
                else:
                    print('press else')
                    self.tabs.setCurrentIndex(self.START_TAB)
            elif self.projectInfo.doesProjectHaveLayers( ):
                visoarLog(self.visoarLogFile, 'Project has layers...')
                mb, ybtn, nbtn,abtn,cbtn = self.getLoadDataFirst('Datasets with multiple MIDX can not be stitched.\n')

                ret = mb.exec()
                if mb.clickedButton() == abtn:
                    print('press action')
                    self.tabs.setCurrentIndex(self.LOAD_TAB)
                elif mb.clickedButton() == ybtn:
                    print('press yes')
                    self.tabs.setCurrentIndex(self.NEW_STITCH_TAB)
                elif mb.clickedButton() == nbtn:
                    print('press no')
                    self.tabs.setCurrentIndex(self.NEW_TIME_SERIES_TAB)
                elif mb.clickedButton() == cbtn:
                    print('press no')
                    self.tabs.setCurrentIndex(self.START_TAB)
                else:
                    print('press else')
                    self.tabs.setCurrentIndex(self.START_TAB)
            else:
                visoarLog(self.visoarLogFile, 'Switching to Stitching')
                #load stitching tab
                self.tabs.setCurrentIndex(self.STITCHING_VIEW_TAB)
                if not self.USER_TAB_UI:
                    self.startViSUSSLAM()
        elif i == self.LOAD_TAB:
            self.tabLoad.LoadFromFile()
        else:

            print('')

    def getLoadDataFirst(self, plusStr):
        mb = QMessageBox()
        mb.setStyleSheet(LOOK_AND_FEEL)
        mb.setWindowTitle("Please Load Data First")
        mb.setText(plusStr+ "You Must load data first\n \tDo want to create a new data set, create a time series, or load an MIDX file?")
        ybtn = mb.addButton('Stitch New', QMessageBox.ApplyRole)
        nbtn = mb.addButton('Create Time Series', QMessageBox.RejectRole)
        abtn = mb.addButton('Load MIDX', QMessageBox.NoRole)
        cbtn = mb.addButton('Cancel', QMessageBox.YesRole)

        # fixButtonsLookFeelGreen(ybtn)
        # fixButtonsLookFeelGreen(nbtn)
        # fixButtonsLookFeelGreen(abtn)
        # fixButtonsLookFeelGreen(cbtn)
        return mb, ybtn, nbtn,abtn,cbtn
    # //////////////////////////////////////////////////////////////////////////////

    def goToAnalyticsTab(self):
        self.viewerW.setSensor(self.projectInfo.sensor)
        self.viewerW2.setSensor(self.projectInfo.sensor)
        self.openfilenameLabel.setText("Viewing: " + self.projectInfo.projDir + "/" + self.projectInfo.projName+ " stitched "+ str(self.stitchNumImages)+" images in "+ self.stitchTime +" minutes")
        self.openfilenameLabelS.setText("Viewing: " + self.projectInfo.projDir + "/" + self.projectInfo.projName+ " stitched "+ str(self.stitchNumImages)+" images in "+ self.stitchTime +" minutes")
        print("Viewing: " + self.projectInfo.projDir + "/" + self.projectInfo.projName+ " stitched "+ str(self.stitchNumImages)+" images in "+self.stitchTime+" minutes")
        self.addScriptActionCombobox(self.tabViewer.buttons.comboBoxATabScripts)
        # self.visusGoogleWebAuth = VisusGoogleWebAutho()
        self.tabViewer.buttons.comboBoxATab.setCurrentIndex(self.tabNewStitching.comboBoxNewTab.currentIndex())
        visoarLog(self.visoarLogFile, '---->Loading midx from: ' + self.projectInfo.projDir)
        try:
            ret = self.tabLoad.loadMIDX()#self.projectInfo.projDir, self.projectInfo.projName, self.projectInfo.srcDir)

            self.changeViewAnalytics()
            #self.tabs.setCurrentIndex(self.ANALYTICS_TAB)
        except IOError as e:
            visoarLog(self.visoarLogFile, "I/O error({0}): {1}".format(e.errno, e.strerror))
        except ValueError:
            visoarLog(self.visoarLogFile, "Could not convert data to an integer.")
        except AttributeError as error:
            visoarLog(self.visoarLogFile, 'AttributError: ' + str(error) + str(sys.exc_info()[0]))
            raise
        except:
            visoarLog(self.visoarLogFile, "Unexpected error:"+ str(sys.exc_info()[0]))
            raise
        if self.DEBUG:
            visoarLog(self.visoarLogFile, 'goToAnalyticsTab finished')

    def printLog(self, text):
        self.slam_widget.printLog(text)
        if self.DEBUG:
            visoarLog(self.visoarLogFile, 'printLog finished')

    def mySetTabStyle(self):
        self.tabs.setStyleSheet(TAB_LOOK)
        if self.DEBUG:
            visoarLog(self.visoarLogFile, 'mySetTabStyle finished')

    def resetView(self):
        db = self.viewer.getDataset()
        if len(self.visoarLayerList) > 0:
            for alayer in self.visoarLayerList:
                #for all layers not google should do a union of all boxes
                if alayer.name!= 'google' and (db is not None) and db.getChild(alayer.name):
                    db2 = self.viewer2.getDataset()
                    # try:
                    #     if db:
                    #         db.setEnableAnnotations(False)
                    #     if db2:
                    #         db2.setEnableAnnotations(False)
                    # except:
                    #     print('Could not shut off annotations in ResetView')
                    box = db.getChild(alayer.name).getDatasetBounds().toAxisAlignedBox()
                    self.viewer.getGLCamera().guessPosition(box)
                    self.viewer2.getGLCamera().guessPosition(box)
                    return

        elif  db.getChild("visus"):
            db2 = self.viewer2.getDataset()
            #Causes a crash
            #db.setEnableAnnotations(False)
            # if (db2):
            #     db2.setEnableAnnotations(False)
            box = db.getChild("visus").getDatasetBounds().toAxisAlignedBox()
            self.viewer.getGLCamera().guessPosition(box)
            self.viewer2.getGLCamera().guessPosition(box)
        else:
            self.viewer.guessGLCameraPosition()
            self.viewer2.guessGLCameraPosition()

    def oneView(self):
        visoarLog(self.visoarLogFile, 'TBI')
        #self.viewer_subwin.hide()
        self.viewerW.hide()
        self.update()
        #self.viewer.setGLCamera(self.viewer2.getGLCamera())

    def sidebySideView(self):
        visoarLog(self.visoarLogFile, 'TBI')
        #self.viewer_subwin.show()
        self.viewerW.show()
        self.update()
        #self.viewer.setGLCamera(self.viewer2.getGLCamera())

    def saveScreenshot(self, withDate=True):
        if withDate:
            now = datetime.now()
            date_time = now.strftime("_%Y%m%d_%H%M%S")
        else:
            date_time = ''
        path = os.path.join(self.projectInfo.cache_dir, 'ViSOARIDX')
        if not os.path.exists(path):
            os.makedirs(path)
        # os.makedirs(path, exist_ok=True)
        # path.parent.mkdir(parents=True, exist_ok=True)
        #if withDate:
        fileName = os.path.join(self.projectInfo.cache_dir, 'ViSOARIDX', self.projectInfo.projName + date_time + '.png')
        #else :
        #    fileName = os.path.join(self.projectInfo.cache_dir, "ViSOARIDX", "Thumbnail.png")

        self.viewer2.takeSnapshot(True, fileName)
        #if self.DEBUG:
        visoarLog(self.visoarLogFile, 'saveScreenshot finished: '+fileName)
        popUP('Snapshot Saved', 'Saved Snapshot to: \n' + fileName)
        return fileName

    def mailScreenshot(self, withDate=True):
        if withDate:
            now = datetime.now()
            date_time = now.strftime("_%Y%m%d_%H%M%S")
        else:
            date_time = ''

        # self.cache_dir = self.projDir+'/VisusSlamFiles'
        path = os.path.join(self.projectInfo.cache_dir, 'ViSOARIDX')
        if not os.path.exists(path):
            os.makedirs(path)
        # os.makedirs(path, exist_ok=True)
        # path.parent.mkdir(parents=True, exist_ok=True)
        # self.viewer.takeSnapshot(True,  self.cache_dir+ '/'+self.projName+'IDX/'+self.projName+date_time+'.png')
        self.viewer2.takeSnapshot(True, os.path.join(self.projectInfo.cache_dir, 'ViSOARIDX', self.projectInfo.projName + date_time + '.png'))

        if self.DEBUG:
            visoarLog(self.visoarLogFile, 'saveScreenshot finished')
        # popUP( 'Snapshot Saved', 'Saved Snapshot to: \n' + self.cache_dir+ '/'+self.projName+'IDX/'+self.projName+date_time+'.png')
        imgWPath = os.path.join(self.projectInfo.cache_dir, 'ViSOARIDX', self.projectInfo.projName + date_time + '.png')
        print(imgWPath)
        self.myVisoarImageMailer = VisoarImageMailer(imgWPath, self.projectInfo.projName, self)
        self.myVisoarImageMailer.launch()

    def saveToCloud(self, withDate=True):
        self.setUpRClone()

    def mailBug(self, withDate=True):
        if withDate:
            now = datetime.now()
            date_time = now.strftime("_%Y%m%d_%H%M%S")
        else:
            date_time = ''

        # self.cache_dir = self.projDir+'/VisusSlamFiles'
        path = os.path.join(self.projectInfo.cache_dir, 'ViSOARIDX')
        if not os.path.exists(path):
            os.makedirs(path)
        # os.makedirs(path, exist_ok=True)
        # path.parent.mkdir(parents=True, exist_ok=True)
        # self.viewer.takeSnapshot(True,  self.cache_dir+ '/'+self.projName+'IDX/'+self.projName+date_time+'.png')
        self.viewer2.takeSnapshot(True, os.path.join(self.projectInfo.cache_dir, 'ViSOARIDX',
                                                    self.projectInfo.projName + date_time + '.png'))

        if self.DEBUG:
            visoarLog(self.visoarLogFile, 'saveScreenshot finished')
        # popUP( 'Snapshot Saved', 'Saved Snapshot to: \n' + self.cache_dir+ '/'+self.projName+'IDX/'+self.projName+date_time+'.png')
        imgWPath = os.path.join(self.projectInfo.cache_dir, 'ViSOARIDX', self.projectInfo.projName + date_time + '.png')
        print(imgWPath)
        self.myVisoarImageMailer = VisoarImageMailer(imgWPath, self.projectInfo.projName, self, True)
        self.myVisoarImageMailer.launch()

    def convertMIDXtoIDXFile(self):

        self.cache_dir = os.path.join(self.projectInfo.projDir, 'VisusSlamFiles')
        path = os.path.join(self.cache_dir, 'ViSOARIDX')
        pathAndName = os.path.join(path,self.projectInfo.projName)
        if not os.path.exists(path):
            os.makedirs(path)
        buttonReply = QMessageBox.question(self, 'Saving', "It will take about 10 minutes to save out the idx file. Do you wish to continue?",
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if self.isWINDOWS:
            cmd = 'python -m OpenVisus midx-to-idx --midx ' + os.path.join(self.cache_dir, 'visus.midx') + ' --idx ' + os.path.join(self.cache_dir, 'ViSOARIDX', 'visus.idx')
        else :
            cmd = '/Users/amygooch/.pyenv/shims/python -m OpenVisus midx-to-idx --midx ' + os.path.join(self.cache_dir,
                                                                  'visus.midx') + ' --idx ' + os.path.join(self.cache_dir, 'ViSOARIDX',  'visus.idx')
        if self.isWINDOWS:
            cmd2 = "cd {0} && C:\\tools\zip.exe -9 -r -X {1}.zip  visus  visus.idx  {2}.json ".format(path,
                                                                                                      self.projectInfo.projName,
                                                                                                      self.projectInfo.projName)
        else:
            cmd2 = "cd {0} && zip -9 -r -X {1}.zip  visus  visus.idx  {2}.json ".format(path, self.projectInfo.projName,self.projectInfo.projName)

        if buttonReply == QMessageBox.Yes:
            print(cmd)
            # #./visus.command midx-to-idx /Users/amygooch/GIT/SCI/DATA/Weston/Front_60_12.9.19/VisusSlamFiles/visus.midx Front60_12_9_19.id
            # os.system('python -m OpenVisus convert midx-to-idx '+ self.projDir + '/VisusSlamFiles/visus.midx '+ self.projDir+'.idx')
            try:
                os.system(cmd)
                visoarLog(self.visoarLogFile, 'convertMIDXtoIDXFile finished')
            except:
                print('Failed to issue command:\n\t {0}'.format(cmd))
            #print('Amy check this pathandName for binary')
                                                                                       #

            try:
                os.system(cmd2)
                visoarLog(self.visoarLogFile, cmd2)
                visoarLog(self.visoarLogFile, 'ziped idx files finished')
            except:
                visoarLog(self.visoarLogFile, 'Failed to issue command:\n\t {0}'.format(cmd2))

            popUP('Save IDX',
                  'Saved IDX file for use on the server: \n' + os.path.join(self.cache_dir, 'ViSOARIDX',
                                                                             'visus.idx'))
            return os.path.join(self.cache_dir, 'ViSOARIDX',  'visus.idx')

        #elif buttonReply == QMessageBox.No:
            #Write cmd to File

        else:
            return ''

    def setEnabledCombobxItem(self, cbox, itemName, enabled):
        itemNumber = self.scriptNames.index(itemName)
        cbox.model().item(itemNumber).setEnabled(enabled)

    def inputModeChanged(self):
        print(self.inputMode)

        # self.buttons.show_threshold_TGI.setEnabled(True)
        # self.buttons.show_threshold_TGI.setStyleSheet(GREEN_PUSH_BUTTON)
        # self.buttons.show_threshold_NDVI.setEnabled(True)
        # self.buttons.show_threshold_NDVI.setStyleSheet(GREEN_PUSH_BUTTON)
        # self.buttons.show_count.setEnabled(True)
        # self.buttons.show_count.setStyleSheet(GREEN_PUSH_BUTTON)
        #
        #
        # if (self.inputMode == "R G B"):
        # 	self.buttons.show_ndvi.setEnabled(False)
        # 	self.buttons.show_ndvi.setStyleSheet(DISABLED_PUSH_BUTTON)
        # 	self.buttons.show_tgi.setEnabled(True)
        # 	self.buttons.show_tgi.setStyleSheet(GREEN_PUSH_BUTTON)
        # 	self.buttons.show_rgb.setEnabled(True)
        # 	self.buttons.show_rgb.setStyleSheet(GREEN_PUSH_BUTTON)
        # if (self.inputMode == "R G NIR"):
        # 	self.buttons.show_ndvi.setEnabled(True)
        # 	self.buttons.show_ndvi.setStyleSheet(GREEN_PUSH_BUTTON)
        # 	self.buttons.show_tgi.setEnabled(False)
        # 	self.buttons.show_tgi.setStyleSheet(DISABLED_PUSH_BUTTON)
        # 	self.buttons.show_rgb.setEnabled(True)
        # 	self.buttons.show_rgb.setStyleSheet(GREEN_PUSH_BUTTON)
        if self.DEBUG:
            visoarLog(self.visoarLogFile, 'inputModeChanged finished')

    # def addQuitButton(self ):
    # 	quitButton=createPushButton("Quit",
    # 			lambda: self.quitApp())
    # 	#myWidget.addWidget(quitButton)
    # 	#ic = QIcon('icons/quit.png')
    # 	#quitButton.setIcon(ic)
    # 	#self.fixButtonsLookFeel(quitButton)
    # 	quitButton.setStyleSheet(WHITE_PUSH_BUTTON)
    # 	return quitButton
    #
    # def quitApp(self):
    # 	reply = QMessageBox.question(
    # 		self, "Message",
    # 		"Are you sure you want to quit? ",
    # 		QMessageBox.Close | QMessageBox.Cancel,
    # 		QMessageBox.Cancel)
    #
    # 	if reply == QMessageBox.Close:
    # 		#app.quit()
    # 		self.close()
    # 	else:
    # 		pass

    def keyPressEvent(self, event):
        """Close application from escape key.

        results in QMessageBox dialog from closeEvent, good but how/why?
        """
        if event.key() == Qt.Key_Escape:
            self.close()

    # If user changes the tab (from New to Load), then refresh to have new project
    def onTabChange(self):
        self.tabLoad.refreshLoadTab()
        if self.DEBUG:
            visoarLog(self.visoarLogFile, 'onTabChange finished')

    # def getDirectoryLocation(self):
    #     self.projectInfo.projDir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
    #     self.curDir2.setText(self.projectInfo.projDir)
    #     if not self.projNametextbox.text():
    #         tempName = os.path.basename(os.path.normpath(self.projectInfo.projDir))
    #         self.projNametextbox.setText(tempName)
    #     if self.DEBUG:
    #         print('getDirectoryLocation finished')

    def addScriptActionCombobox(self, cbox):

        for item in self.scriptNames:
            cbox.addItem(item)
        cbox.setToolTip('Filter data')
        cbox.setStyleSheet(MY_COMBOX)
        cbox.currentIndexChanged.connect(partial(self.loadScript, cbox))

    def loadScript(self, cbox):
        visoarLog(self.visoarLogFile, 'FUNCTION  Load Script...')
        scriptName = cbox.currentText()
        print(scriptName)
        if scriptName == "Original":
            visoarLog(self.visoarLogFile, '\tShow Original')
            self.tabViewer.showRGB()
            # cbox.setText('output = input')
            return
        #self.app_dir = os.getcwd()

        if self.tabViewer.buttons.comboBoxATab.currentText() == 'R NIR (Sentera NDVI)':
            scriptName = 'NDVI_Sentera'
        elif self.tabViewer.buttons.comboBoxATab.currentText() == 'RedEdge NIR (Sentera NDRE)':
            scriptName = 'NDRE_Sentera'
        else:
            scriptName = cbox.currentText()
        script = getTextFromScript(os.path.join(self.app_dir, 'scripts', scriptName + '.py'))
        visoarLog(self.visoarLogFile, '\tGot script content is: ')
        visoarLog(self.visoarLogFile, script)
        if script:
            fieldname = "output=ArrayUtils.interleave(ArrayUtils.split(voronoi())[0:3])"
            visoarLog(self.visoarLogFile, "Running script ")

            #self.viewer.setFieldName(fieldname)
            #self.viewer.setScriptingCode(script)
            self.viewer2.setFieldName(fieldname)
            self.viewer2.setScriptingCode(script)

            if self.DEBUG:
                visoarLog(self.visoarLogFile, 'run script finished')
        self.update()

    def onCameraChange12(self):
        #self.cam1 = self.viewer.getGLCamera()
        #self.cam2 = self.viewer2.getGLCamera()
        self.onCameraChange( self.cam1, self.cam2)

    def onCameraChange21(self):
        #self.cam1 = self.viewer.getGLCamera()
        #self.cam2 = self.viewer2.getGLCamera()
        self.onCameraChange(  self.cam2, self.cam1)
    # onCameraChange
    def onCameraChange(self, cam1, cam2):
        if self.LINK_CAMERAS:
            if cam1 == None:
                visoarLog(self.visoarLogFile, 'onCameraChange: error: cam 1 is none')
                return
            if cam2 == None:
                visoarLog(self.visoarLogFile, 'onCameraChange: error: cam 2 is none')
                return
            # avoid rehentrant calls
            if hasattr(self, "changing_camera") and self.changing_camera:
                return

            self.changing_camera = True

            # 3d
            if isinstance(cam1, GLLookAtCamera):
                pos1, center1, vup1 = [cam1.getPos(), cam1.getCenter(), cam1.getVup()]
                pos2, center2, vup2 = [cam2.getPos(), cam2.getCenter(), cam2.getVup()]
                cam2.beginTransaction()
                cam2.setLookAt(pos1, center1, vup1)
                # todo... projection?
                cam2.endTransaction()
            # 3d
            else:
                pos1, cen1, vup1, proj1 = cam1.getPos(), cam1.getCenter(), cam1.getVup(), cam1.getOrthoParams()
                pos2, cen2, vup2, proj2 = cam2.getPos(), cam2.getCenter(), cam2.getVup(), cam2.getOrthoParams()
                # print("pos",pos1.toString(),"cen",cen1.toString(),"vup",vup1.toString(),"proj",proj1.toString())
                # print("pos",pos2.toString(),"cen",cen2.toString(),"vup",vup2.toString(),"proj",proj2.toString())
                cam2.beginTransaction()
                cam2.setLookAt(pos1, cen1, vup1)
                cam2.setOrthoParams(proj1)
                cam2.endTransaction()

            self.changing_camera = False
    # destroy
    def destroy(self):
        self.viewer = None
        self.viewer2 = None

    def setUpCams(self):
        self.cam1 = self.viewer.getGLCamera()
        self.cam2 = self.viewer2.getGLCamera()
        if isinstance(self.cam1, GLOrthoCamera): self.cam1.toggleDefaultSmooth()
        if isinstance(self.cam2, GLOrthoCamera): self.cam2.toggleDefaultSmooth()

    def openMIDX(self):
        #AAG04.30.2021 self.projectInfo.cache_dir = os.path.join(self.projectInfo.projDir, 'VisusSlamFiles')
        if self.projectInfo.doesProjectHaveLayers( ) and self.USER_TAB_UI:
            self.tabs.setTabEnabled(self.STITCHING_VIEW_TAB, False)
        elif self.USER_TAB_UI:
            self.tabs.setTabEnabled(self.STITCHING_VIEW_TAB, True)
        if (self.stitchNumImages > 0):
            self.openfilenameLabel.setText(
                "Viewing: " + self.projectInfo.projDir + "/" + self.projectInfo.projName + " stitched " + str(
                    self.stitchNumImages) + " images in " +  self.stitchTime   + " minutes")
            self.openfilenameLabelS.setText(
                "Viewing: " + self.projectInfo.projDir + "/" + self.projectInfo.projName + " stitched " + str(
                    self.stitchNumImages) + " images in " + self.stitchTime  + " minutes")
        else:
            self.openfilenameLabel.setText(self.projectInfo.cache_dir)
            self.openfilenameLabelS.setText(self.projectInfo.cache_dir)
        googlefile = os.path.join(self.projectInfo.cache_dir,  'google.midx')
        self.midxfilename = os.path.join(self.projectInfo.cache_dir, 'visus.midx')
        if self.SHOW_GOGGLE_MAP and os.path.exists(googlefile):
            self.midxfilename = os.path.join(self.projectInfo.cache_dir,   'google.midx')
            self.turnOnShowGoogleMap()
        else:
            self.midxfilename = os.path.join(self.projectInfo.cache_dir, 'visus.midx')
            self.shutOffSHowGoogleMap()

        if self.projectInfo.projDirNDVI and (self.projectInfo.projDirNDVI != "" or self.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam') or (self.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB'):
            # if self.SHOW_GOGGLE_MAP and os.path.exists(googlefile):
            #     rgbfilename = os.path.join(self.projectInfo.projDir, 'VisusSlamFiles','google.midx')
            #     ndvifilename = os.path.join(self.projectInfo.projDirNDVI, 'VisusSlamFiles','google.midx')
            # else:
            rgbfilename = os.path.join(self.projectInfo.srcDir, 'VisusSlamFiles', 'visus.midx')
            ndvifilename = os.path.join(self.projectInfo.srcDirNDVI, 'VisusSlamFiles', 'visus.midx')
            try:
                ret1 = self.viewer.open(rgbfilename)
            except:
                popUP('Error', 'Error ViSOARUIWidget 1376 loading: {0}'.format(rgbfilename))

            try:
                ret2 = self.viewer2.open(ndvifilename)
            except:
                popUP('Error', 'Error ViSOARUIWidget 1383 loading: {0}'.format(ndvifilename))

        else:
            try:
                ret1 = self.viewer.open(self.midxfilename)
            except:
                popUP('Error', 'Error ViSOARUIWidget 1389 loading: {0}'.format(self.midxfilename))

            try:
                ret2 = self.viewer2.open(self.midxfilename)
            except:
                popUP('Error', 'Error ViSOARUIWidget 1394 loading: {0}'.format(self.midxfilename))

        self.setUpCams()
        self.resetView()
        return ret1, ret2

    def shutOffSHowGoogleMap(self):
        self.SHOW_GOGGLE_MAP = False
        print('AMy, may have to fix this toggle')
        #self.tabViewer.buttons.toggleGoogleMapBtn.setIcon(QIcon('icons/GoogleMapGray.png'))
        #self.tabViewer.buttons.toggleGoogleMapBtn.setChecked(False)
        self.update()

    def turnOnShowGoogleMap(self):
        self.SHOW_GOGGLE_MAP = True
        print('AMy, may have to fix this toggle')
        #self.tabViewer.buttons.toggleGoogleMapBtn.setChecked(True)
        #self.tabViewer.buttons.toggleGoogleMapBtn.setIcon(QIcon('icons/GoogleMapGreen.png'))
        self.update()

    # def doesProjectHaveLayers(self, projDir):
    #     #ignoring google, does this project have layers
    #     if  not os.path.exists(os.path.join(projDir, 'VisusSlamFiles', 'visus.midx')):
    #         #popUP('File not found', 'Could not find file: \n' + os.path.join(os.path.join(projDir, 'VisusSlamFiles', 'visus.midx')+ '\nThis error is due to errors in the userFileHistory.xml not matching the content on disk.'))
    #         #This error is due to errors in the userhistory not matching the content on disk
    #         return False
    #     tree = ET.parse(os.path.join(projDir, 'VisusSlamFiles', 'visus.midx'))
    #     wrapperdataset = tree.getroot()
    #     count = 0
    #     for visusfile in wrapperdataset.iterfind('dataset'):
    #         if visusfile.attrib['name'] == 'google':
    #             print('found google')
    #         else:
    #             count = count + 1
    #     if count > 1:
    #         return True
    #     else:
    #         return False

   #      self.START_TAB = 0
   #      self.NEW_STITCH_TAB = 1
   #      self.NEW_TIME_SERIES_TAB = 2
   #      self.LOAD_TAB = 3
   #      self.STITCHING_VIEW_TAB = 4
   #      self.ANALYTICS_TAB = 5

    def changeViewHome(self):

        self.tabAskDest.destNametextbox.setText('')
        self.tabAskDest.createErrorLabel.setText('')
        self.tabAskName.projNametextbox.setText('')
        self.tabAskName.createErrorLabel.setText('')
        self.tabAskSource.curDir2.setText('')
        self.tabAskSource.buttonAddImagesSource.setText('Choose Directory')
        self.tabAskSource.buttonAddImagesSource.setStyleSheet(GREEN_PUSH_BUTTON)
        self.tabAskDest.destNewDir.setText('Choose Directory')
        self.tabAskDest.destNewDir.setStyleSheet(GREEN_PUSH_BUTTON)
        self.tabNewStitching.buttonAddImagesTab.setText('Choose Directory')
        self.tabNewStitching.buttonAddImagesTab.setStyleSheet(GREEN_PUSH_BUTTON)

        self.tabs.setCurrentIndex(self.START_TAB)
        self.update()

    def enableViewHome(self,enabledView = True):
        if (self.USER_TAB_UI):
            self.tabs.setTabEnabled(self.START_TAB, enabledView)

    def changeViewNewStitch(self):
        if (self.USER_TAB_UI):
            self.tabs.setCurrentIndex(self.NEW_STITCH_TAB)
        else:
            self.tabs.setCurrentIndex(self.ASKSENSOR_TAB)

    def enableViewNewStitch(self,enabledView = True):
        if (self.USER_TAB_UI):
            self.tabs.setTabEnabled(self.NEW_STITCH_TAB, enabledView)

    def changeViewMoveDataFromCards(self):
        if (self.USER_TAB_UI):
            self.tabs.setCurrentIndex(self.MOVE_DATA_TAB)
        else:
            self.tabs.setCurrentIndex(self.MOVE_DATA_TAB)

    def enableViewMoveDataFromCards(self,enabledView = True):
        if (self.USER_TAB_UI):
            self.tabs.setTabEnabled(self.MOVE_DATA_TAB, enabledView)

    def changeViewBatchProcess(self):
        self.BATCH_MODE = True
        self.tabAskSensor.comboBoxNewTab.setCurrentText('R G B')
        if (self.USER_TAB_UI):
            #self.tabs.setCurrentIndex(self.ASKSENSOR_TAB)
            self.tabs.setCurrentIndex(self.ASKSOURCE_TAB)
        else:
            self.tabs.setCurrentIndex(self.ASKSOURCE_TAB)
            #self.tabs.setCurrentIndex(self.ASKSENSOR_TAB)

    def enableViewBatchProcess(self,enabledView = True):
        self.BATCH_MODE = True
        if (self.USER_TAB_UI):
            self.tabs.setTabEnabled(self.ASKSENSOR_TAB, enabledView)

    def isViewNewStitch(self):
        if (self.tabs.currentIndex() == self.NEW_STITCH_TAB):
            return True
        else:
            return False

    def enableViewNewTimeSeries(self,enabledView = True):
        if (self.USER_TAB_UI):
            self.tabs.setTabEnabled(self.NEW_TIME_SERIES_TAB, enabledView)
    def changeViewNewTimeSeries(self):
        self.tabs.setCurrentIndex(self.NEW_TIME_SERIES_TAB)

    def enableViewLoad(self,enabledView = True):
        if (self.USER_TAB_UI):
            self.tabs.setTabEnabled(self.LOAD_TAB, enabledView)

    def changeViewLoad(self):
        self.tabs.setCurrentIndex(self.LOAD_TAB)

    def enablequickNDVIView(self, enabledView=True):
        if (self.USER_TAB_UI):
            self.tabs.setTabEnabled(self.QUICK_NDVI_TAB, enabledView)

    def changequickNDVIView(self):
        self.tabs.setCurrentIndex(self.QUICK_NDVI_TAB)

    def enableViewStitching(self,enabledView = True):
        if (self.USER_TAB_UI):
            self.tabs.setTabEnabled(self.STITCHING_VIEW_TAB, enabledView)

    def changeViewStitching(self):
        #self.USER_TAB_UI =
        self.openfilenameLabelS.setText(os.path.join(self.projectInfo.projDir, self.projectInfo.projName))
        self.tabStitcher.buttons.goToAnalytics.setStyleSheet(GREEN_PUSH_BUTTON)
        self.tabStitcher.buttons.goToAnalytics.setEnabled(False)
        self.tabs.setCurrentIndex(self.STITCHING_VIEW_TAB)
       # self.startViSUSSLAM()
    def enableViewAnalytics(self,enabledView = True):
        if (self.USER_TAB_UI):
            self.tabs.setTabEnabled(self.ANALYTICS_TAB, enabledView)

    def changeViewAnalytics(self):
        if (self.stitchNumImages > 0):
            self.openfilenameLabel.setText(
                "Viewing: " + self.projectInfo.projDir + "/" + self.projectInfo.projName + " stitched " + str(
                    self.stitchNumImages) + " images in " +  self.stitchTime  + " minutes")
            self.openfilenameLabelS.setText(
                "Viewing: " + self.projectInfo.projDir + "/" + self.projectInfo.projName + " stitched " + str(
                    self.stitchNumImages) + " images in " + self.stitchTime   + " minutes")
        else:
            self.openfilenameLabel.setText(os.path.join(self.projectInfo.projDir, self.projectInfo.projName))
        self.viewerW.setSensor(self.projectInfo.sensor)
        self.viewerW2.setSensor(self.projectInfo.sensor)
        self.tabs.setCurrentIndex(self.ANALYTICS_TAB)

    def goHome(self):
        self.BATCH_MODE = False
        self.slam = Slam2D()
        self.stitchTime = "0"
        self.stitchNumImages =0
        self.tabAskDest.destNametextbox.setText('')
        self.tabAskDest.createErrorLabel.setText('')
        # self.tabAskName.projNametextbox.setText('')
        # self.tabAskName.createErrorLabel.setText('')
        self.tabAskSource.curDir2.setText('')
        self.tabAskSource.buttonAddImagesSource.setText('Choose Directory')
        self.tabAskSource.buttonAddImagesSource.setStyleSheet(GREEN_PUSH_BUTTON)
        self.tabAskDest.destNewDir.setText('Choose Directory')
        self.tabAskDest.destNewDir.setStyleSheet(GREEN_PUSH_BUTTON)
        self.tabAskSource.mapirCalibrationWidget.resetUIFill()

        # self.tabNewStitching.buttonAddImagesTab.setText('Choose Directory')
        # self.tabNewStitching.buttonAddImagesTab.setStyleSheet(GREEN_PUSH_BUTTON)
        self.tabs.setCurrentIndex(self.START_TAB)
        #clear out strings:
        self.projectInfo.reset()
        self.viewer.clearAll()
        self.viewer2.clearAll()
        self.changeViewHome()
        #self.tabs.setCurrentIndex(self.START_TAB)
        # projectDir is where to save the files
        # srcDir is the location of initial images
        self.update()

    def startViSUSSLAM(self):
        if not self.projectInfo.srcDir:
            self.projectInfo.srcDir = self.projectInfo.projDir

        #retSlamSetup, retSlamRan = self.setAndRunSlam(image_dir=self.projectInfo.srcDir, cache_dir=os.path.join(self.projectInfo.projDir, 'VisusSlamFiles'))
        # self.slam.enable_svg = False
        # self.slam.setImageDirectory(image_dir=self.projectInfo.srcDir, cache_dir=os.path.join(self.projectInfo.projDir, 'VisusSlamFiles'))
        # # self.parent.onChange(self.parent.STITCHING_VIEW_TAB)
        # except:
        # self.parent.tabs.setCurrentIndex(self.parent.START_TAB)
        #     self.parent.onChange(self.parent.START_TAB)
        # self.showFullScreen()
        # os.system('cd ~/GIT/ViSUS/SLAM/Giorgio_SLAM_Nov212019/OpenVisus')
        # print('cd ~/GIT/ViSUS/SLAM/Giorgio_SLAM_Nov212019/OpenVisus; python -m Slam '+srcDir)
        # os.system('python -m Slam '+srcDir)
        if self.DEBUG:
            print('startViSUSSLAM finished')

        #import time
        #time.sleep(3)
        print('Amy Check this' )
        self.tabStitcher.run()

    def saveJSONFile(self):
        import json
        #self.cache_dir = os.path.join(self.projectInfo.projDir, 'VisusSlamFiles')
        self.jsonFile = os.path.join( self.projectInfo.cache_dir,'ViSOARIDX',self.projectInfo.projName+'.json')
        visoarLog(self.visoarLogFile, 'Will write to : {0}'.format(self.jsonFile))
        path = os.path.join(self.projectInfo.cache_dir, 'ViSOARIDX')
        if not os.path.exists(path):
            os.makedirs(path)

        data = {
            "owner": "dronepilot@visus.net",
            "share": ["lance@cropsolutionsllc.com","dronepilot@visus.net","amy@visus.net"],
            "projName": self.projectInfo.projName,
            "name": self.projectInfo.projName,
            "projDir":    self.projectInfo.projDir,
            "srcDir": self.projectInfo.srcDir,
            "projDirNDVI":    self.projectInfo.projDirNDVI,
            "cacheDir" : self.projectInfo.cache_dir,
            "createdAt": self.projectInfo.createdAt,
            "updatedAt": self.projectInfo.updatedAt,
            "idxLocalPath": os.path.join(self.projectInfo.cache_dir, "ViSOARIDX" ),
            "idxFile":  self.projectInfo.projName ,
        }


        with open(self.jsonFile, 'w') as outfile:
            json.dump(data, outfile)
        visoarLog(self.visoarLogFile, 'Output json file to: {0}'.format(self.jsonFile))

    def setUpRClone(self):
        self.cache_dir = self.projectInfo.cache_dir #os.path.join(self.projectInfo.projDir, 'VisusSlamFiles')
        idxpath = os.path.join(self.cache_dir, 'ViSOARIDX')
        idxzip = os.path.join(self.cache_dir, 'ViSOARIDX',self.projectInfo.projName+'.zip')
        jsonFile = os.path.join(self.cache_dir, 'ViSOARIDX',self.projectInfo.projName+'.json')
        crontab = os.path.join(self.cache_dir, 'ViSOARIDX','addToRcloneCronTab.sh')
        #self.projectInfo.projDir, self.projectInfo.projName
        # print('Convert to idx: ' + projectDir + '/VisusSlamFiles/visus.midx')

        #create json config file:
        #owner (email address), list of users (email), name of dataset, creation date,
        #later will need lat long (giorgio/Steve)
        self.saveJSONFile()
        idxfilepath = self.convertMIDXtoIDXFile()

        #Set up rclone to copy idx and json file to server
        file_object = open(crontab, 'a')
        file_object.write('rclone copy --update --verbose --transfers 30 --checkers 8 --contimeout 60s --timeout 300s --retries 3 --low-level-retries 10 --stats 1s "'+ idxzip + '" "remote:/hdscratch1/ag-explorer/rsync"')
        file_object.write('\n')
        file_object.write('rclone copy --update --verbose --transfers 30 --checkers 8 --contimeout 60s --timeout 300s --retries 3 --low-level-retries 10 --stats 1s "' + jsonFile + '" "remote:/hdscratch1/ag-explorer/rsync"')
        file_object.write('\n')
        # Next copy over the json file
        # what do you want
        # rename file to visus.idx
        # name.json
        # Python code to John and Steve

        file_object.write('\n')
        file_object.close()
        visoarLog(self.visoarLogFile, 'Wrote crontab to: {0}'.format(crontab))

    def setAnnotations(self, value):
        self.ANNOTATIONS_MODE = value
        db2 = self.viewer2.getDataset()
        db = self.viewer.getDataset()
        try:
            if db.getChild("visus"):
                if self.ANNOTATIONS_MODE and db:
                    db.setEnableAnnotation(True)
                    if (db2):
                        db2.setEnableAnnotation(True)
                elif db:
                    db.setEnableAnnotation(False)
                    if (db2):
                        db2.setEnableAnnotation(False)
        except:
            print("Could not toggle enable Annotations")
        print('Amy fix annotations ...')
        # db = self.viewer.getDataset()
        # db.setEnableAnnotations(value)
        # db = self.viewer2.getDataset()
        # db.setEnableAnnotations(value)

#
# class ViSOARUIWidgetFull(ViSOARUIWidget):
#     def __init__(self, parent):
#         super(ViSOARUIWidget, self).__init__(parent)
#         self.app_dir = os.getcwd()
#
#         self.USER_TAB_UI = False
#
#         self.START_TAB = 0
#         self.NEW_STITCH_TAB = 1
#         self.NEW_TIME_SERIES_TAB = 2
#         self.LOAD_TAB = 3
#         self.STITCHING_VIEW_TAB = 4
#         self.ANALYTICS_TAB = 5
#         self.ASKSENSOR_TAB = 6
#         self.ASKSOURCE_TAB = 7
#         self.ASKNAME_TAB = 8
#         self.ASKDEST_TAB = 9
#         self.ASKSOURCERGBNDVI_TAB = 10
#         self.MOVE_DATA_TAB = 11
#         self.BATCH_PROCESS_TAB = 12
#
#         self.copySourceBool = False
#         self.SHOW_GOGGLE_MAP = False
#         self.ANNOTATIONS_MODE = False
#
#         self.isWINDOWS = (sys.platform.startswith("win") or
#                           (sys.platform == 'cli' and os.name == 'nt'))
#
#         self.inputMode = "R G B"
#         self.projectInfo = VisoarProject()
#
#
#         self.userFileHistory = os.path.join(os.getcwd(), 'userFileHistory.xml')
#
#         self.scriptNames = MASTER_SCRIPT_LIST
#         self.LINK_CAMERAS = True
#
#         self.generate_bbox = False
#         self.color_matching = False
#         self.blending_exp = "output=voronoi()"
#
#         self.loadWidgetDict = {}
#         self.loadLabelsWidgetDict = {}
#
#         if os.path.exists(self.userFileHistory):
#             print('All app settings will be saved to: ' + self.userFileHistory)
#         else:
#             f = open(self.userFileHistory, "wt")
#             today = datetime.now()
#             todayFormated = today.strftime("%Y%m%d_%H%M%S")
#             f.write('<data>\n' +
#                     '\t<project>\n' +
#                     '\t\t<projName>TestData</projName>\n' +
#                     '\t\t<projDir>./data/TestData</projDir>\n' +
#                     '\t\t<srcDir>./data/TestData</srcDir>\n' +
#                     '\t\t<createdAt>' + todayFormated + '</createdAt>\n' +
#                     '\t\t<updatedAt>' + todayFormated + '</updatedAt>\n' +
#                     '\t</project>\n' +
#                     '</data>\n')
#             f.close()
#         self.DEBUG = True
#         self.ADD_VIEWER = True  # Flag for removing viewers for testing
#
#         self.openfilenameLabelS = QLabel()
#         self.openfilenameLabelS.resize(480, 40)
#         self.openfilenameLabelS.setStyleSheet(
#             "min-height:30; min-width:180; padding:0px; background-color: #ffffff; color: rgb(0, 0, 0);  border: 0px")
#
#         self.openfilenameLabel = QLabel()
#         self.openfilenameLabel.resize(480, 40)
#         self.openfilenameLabel.setStyleSheet(
#             "min-height:30; min-width:180; padding:0px; background-color: #ffffff; color: rgb(0, 0, 0);  border: 0px")
#         self.openfilenameLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
#         if self.ADD_VIEWER:
#             self.viewerW = MyViewerWidget(self)
#             self.viewerW2 = MyViewerWidget(self)
#             self.viewer = self.viewerW.viewer  # MyViewer()
#             self.viewer2 = self.viewerW2.viewer  # MyViewer()
#
#             # self.viewer.hide()
#             self.viewer.setMinimal()
#             self.viewer2.setMinimal()
#
#             self.cam1 = self.viewer.getGLCamera()
#             self.cam2 = self.viewer2.getGLCamera()
#
#             # disable smoothing
#             if isinstance(self.cam1, GLOrthoCamera): self.cam1.toggleDefaultSmooth()
#             if isinstance(self.cam2, GLOrthoCamera): self.cam2.toggleDefaultSmooth()
#
#             self.viewer.on_camera_change = lambda: self.onCameraChange12()
#             self.viewer2.on_camera_change = lambda: self.onCameraChange21()
#             # self.viewer_subwin = sip.wrapinstance(FromCppQtWidget(self.viewer.c_ptr()), QtWidgets.QMainWindow)
#             # self.viewer_subwin2 = sip.wrapinstance(FromCppQtWidget(self.viewer2.c_ptr()), QtWidgets.QMainWindow)
#             self.viewer_subwin = self.viewerW.viewer_subwin
#             self.viewer_subwin2 = self.viewerW2.viewer_subwin
#
#         else:
#             self.viewer_subwin = QWidget(self)
#
#         self.pythonScriptingWindow = PythonScriptWindow(self)
#         self.pythonScriptingWindow.resize(600, 640)
#
#         self.logo = QPushButton('', self)
#         self.logo.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
#         ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
#         self.logo.setIcon(QIcon(os.path.join(self.app_dir, 'icons', 'visoar_logo.png')))
#         self.logo.setIconSize(QSize(480, 214))
#
#         self.logo.setText('')
#         if self.ADD_VIEWER:
#             self.slam_widget = Slam2DWidgetForVisoar(self)
#             self.slam_widget.setStyleSheet(LOOK_AND_FEEL)
#             self.slam_widget.progress_bar.bar.setStyleSheet(PROGRESSBAR_LOOK_AND_FEEL)
#             self.slam_widget.progress_bar.bar.setMinimumWidth(300)
#             self.slam = Slam2D()
#             self.slam_widget.slam = self.slam
#
#         self.visoarUserLibraryData = VisoarUserLibraryData(self.userFileHistory)
#
#         self.layout = QVBoxLayout(self)
#
#         self.tabAskSensor = VisoarAskSensor(self)
#         self.tabAskSource = VisoarAskSource(self)
#         self.tabAskSourceRGBNDVI = VisoarAskSourceRGBNDVI(self)
#         self.tabAskName = VisoarAskName(self)
#         self.tabAskDest = VisoarAskDest(self)
#
#         self.tabStart = VisoarStartTabWidget(self)  # QWidget()
#         self.tabNewStitching = VisoarNewTabWidget(self)  # QWidget()
#         self.tabNewTimeSeries = VisoarNewTimeSeriesTabWidget(self)  # QWidget()
#         self.tabLoad = VisoarLoadTabWidget(self)  # QWidget()
#
#         #self.tabBatchProcess = VisoarBatchProcessWidget(self)  # QWidget()
#         self.tabMoveDataFromCards = VisoarMoveDataWidget(self)  # QWidget()
#
#         if self.ADD_VIEWER:
#             self.tabStitcher = VisoarStitchTabWidget(self)  # QWidget()
#             self.tabViewer = VisoarAnalyzeTabWidget(self)  # QWidget()
#
#         if self.USER_TAB_UI:
#             # Initialize tab screen
#             self.tabs = QTabWidget()
#             self.tabs.resize(600, 600)
#
#             self.mySetTabStyle()
#             self.tabs.addTab(self.tabStart, "ViSOAR")
#             # homeicon = QIcon('icons/House.png')#, alignment=Qt.AlignCenter)
#             # homeicon = QIcon('icons/VisoarEye80x80.png')#, alignment=Qt.AlignCenter)
#             # self.tabs.setTabIcon(self.START_TAB, homeicon)
#
#             self.tabs.addTab(self.tabNewStitching, "Stitch A New Mosaic")
#             # homeicon = QIcon('icons/puzzleT.png')#, alignment=Qt.AlignCenter)
#             # self.tabs.setTabIcon(self.NEW_STITCH_TAB, homeicon)
#
#             self.tabs.setIconSize(QSize(100, 100))
#
#             self.tabs.addTab(self.tabNewTimeSeries, "Create Time Series")
#
#             self.tabs.addTab(self.tabLoad, "Load Project")
#             if self.ADD_VIEWER:
#                 self.tabs.addTab(self.tabStitcher, "Stitcher")
#                 self.tabs.addTab(self.tabViewer, "Analytics")
#             self.tabs.currentChanged.connect(self.onTabChange)  # changed!
#
#             # self.tabs.setTabEnabled(2,False)
#             if (self.USER_TAB_UI):
#                 self.tabs.setTabEnabled(self.ANALYTICS_TAB, False)
#
#             self.tabs.setCurrentIndex(self.START_TAB)
#             self.tabs.currentChanged.connect(self.onChange)  # changed!
#         else:
#             self.leftlist = QListWidget()
#             self.leftlist.insertItem(self.START_TAB, 'Start')
#             self.leftlist.insertItem(self.NEW_STITCH_TAB, 'One Screen New')
#             self.leftlist.insertItem(self.NEW_TIME_SERIES_TAB, 'Create Time Series')
#             self.leftlist.insertItem(self.LOAD_TAB, 'Load Dataset')
#             self.leftlist.insertItem(self.STITCHING_VIEW_TAB, 'Stich Moasic')
#             self.leftlist.insertItem(self.ANALYTICS_TAB, 'Viewer')
#             self.leftlist.insertItem(self.ASKSENSOR_TAB, 'Sensor')
#             self.leftlist.insertItem(self.ASKSOURCE_TAB, 'Image Directory')
#             self.leftlist.insertItem(self.ASKNAME_TAB, 'Project Name')
#             self.leftlist.insertItem(self.ASKDEST_TAB, 'Save Directory')
#             self.leftlist.insertItem(self.ASKSOURCERGBNDVI_TAB, 'RGB and NDVI Image Directory')
#             self.leftlist.insertItem(self.MOVE_DATA_TAB, 'Move Data from Drone Cards')
#             self.leftlist.currentRowChanged.connect(self.display)
#
#             # use stack
#             self.tabs = QStackedWidget()
#
#             self.tabs.addWidget(self.tabStart)
#             self.tabs.addWidget(self.tabNewStitching)
#             self.tabs.addWidget(self.tabNewTimeSeries)
#             self.tabs.addWidget(self.tabLoad)
#             self.tabs.addWidget(self.tabStitcher)
#             self.tabs.addWidget(self.tabViewer)
#             self.tabs.addWidget(self.tabAskSensor)
#             self.tabs.addWidget(self.tabAskSource)
#             self.tabs.addWidget(self.tabAskName)
#             self.tabs.addWidget(self.tabAskDest)
#             self.tabs.addWidget(self.tabAskSourceRGBNDVI)
#             self.tabs.addWidget(self.tabMoveDataFromCards)
#
#             self.tabs.setCurrentIndex(0)
#
#             # Add layout of tabs to self
#         self.layout.addWidget(self.tabs)


    def check_splcharacter(self,text):
        import re
        if os.path.isdir(text):
            dir, filestr = os.path.split(text)
        else:
            filestr = text
        string_check = re.compile('[@!#$%^&*()<>?/\|}{~:]')
        newstring = filestr
        from string import ascii_letters, digits
        #if just want to test for ascii and digits, do if set(text).difference(ascii_letters + digits) returns true for anything by ascii and digits

        if  '\''  in filestr or '\"' in filestr  or string_check.search(filestr) != None:
            popUP('Error: Special Character', 'ERROR: your directory or name contains special cha')

            mb = QMessageBox()
            mb.setStyleSheet(LOOK_AND_FEEL)
            #mb.setStyleSheet(POPUP_LOOK_AND_FEEL)
            #mb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            mb.setWindowTitle("Error: Special Character")
            mb.setText(
                  "Your project directory path has special characters.\n\nDo want: us to rename it or cancel and you can rename it yourself?")
            cbtn = mb.addButton('Cancel', QMessageBox.NoRole)

            ybtn = mb.addButton('Automatically Rename', QMessageBox.YesRole)
            # nbtn = mb.addButton('I will rename it', QMessageBox.RejectRole)
            # abtn = mb.addButton('Continue at my Peril', QMessageBox.NoRole)
            #mb.setStyleSheet("QPushButton {padding: 3px;}")
            #width = ybtn.fontMetrics().boundingRect(text).width()
            #btn.setMinimumWidth(width)
            #ybtn.setMinimumWidth(width)
            # nbtn.setMinimumWidth(width)
            # abtn.setMinimumWidth(width)
            #cbtn.setMinimumWidth(width)
            #mb.setFixedWidth(600)

            ret = mb.exec()
            # if mb.clickedButton() == abtn:
            #     print('Continue at my Peril0')
            # el
            if mb.clickedButton() == ybtn:
                print('Automatically Rename')
                from slugify import slugify
                newstring = slugify(newstring,separator = '_' )
                if os.path.isdir(text):
                    popUP('Renaming directory: ', 'Renaming directory: '+text+' to '+ os.path.join(dir,newstring))
                    os.rename(text, os.path.join(dir, newstring))
                else:
                    popUP('Renaming string: ', 'Renaming string: '+text+' to '+  newstring)
            # elif mb.clickedButton() == nbtn:
            #     print('I Will Rename it myself')
            #     self.goHome()
            elif mb.clickedButton() == cbtn:
                print('Continue at my Peril')
            else:
                print('Cancel')
                self.goHome()
        else:
            print("Text hasn't special characters.")

        if os.path.isdir(text):
            newstring = os.path.join(dir, newstring)

        return newstring

