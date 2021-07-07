from VisoarSettings import *

from PyQt5.QtWebEngineWidgets         import QWebEngineView

from OpenVisus                        import *
from OpenVisus.gui                    import *

from PyQt5.QtGui 					  import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton,QToolButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFileDialog

from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem

from pythonScriptingWindow import *

from VisoarMapPieces import *


class VisoarAnalyzeTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.sublayoutTabViewer = QVBoxLayout()
        self.DEBUG = True
        self.setStyleSheet(LOOK_AND_FEEL)
        self.TOPBOTTOM_VIEWER = False
        self.SVG_ON = True

        self.parent.visoarLayerList = []

        class Buttons:
            pass

        self.buttons = Buttons

        # self.toolbar
        self.toolbar = QHBoxLayout()

        self.buttons.home = QPushButton('', self)
        self.buttons.home.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.home.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'home.png')))
        self.buttons.home.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.home.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.home.clicked.connect(self.parent.goHome)
        self.buttons.home.setToolTip('Go to home screen')


        # self.buttons.stitch = QPushButton('', self)
        # self.buttons.stitch.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        # ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        # self.buttons.stitch.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'puzzle.png')))
        # self.buttons.stitch.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        # self.buttons.stitch.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        # self.buttons.stitch.clicked.connect(self.parent.changeViewStitching)
        # self.buttons.stitch.setToolTip('Go to stitching screen')
        # self.buttons.stitch.setHidden(True)

        #self.buttons.inputModeATabLabel = QLabel("Sensor:", self)

        self.buttons.comboBoxATab = QComboBox(self)
        self.buttons.comboBoxATab.addItem("R G B")
        self.buttons.comboBoxATab.addItem("MapIR only (OCNIR)")
        self.buttons.comboBoxATab.addItem("R G NIR")
        self.buttons.comboBoxATab.addItem("R NIR (Sentera NDVI)")
        self.buttons.comboBoxATab.addItem("RedEdge NIR (Sentera NDRE)")
        self.buttons.comboBoxATab.addItem("Unknown")

        self.buttons.comboBoxATab.setStyleSheet(MY_COMBOX)
        self.buttons.comboBoxATab.currentIndexChanged.connect(self.inputModeChangedATab)


        #print('combobox new tab: ' + str(self.parent.tabNewStitching.comboBoxNewTab.currentIndex()))
        self.buttons.comboBoxATab.setToolTip('Sensor/Image mode for input images')
        self.toolbar.addWidget(self.buttons.home)
        #self.toolbar.addWidget(self.buttons.inputModeATabLabel)
        self.toolbar.addWidget(self.buttons.comboBoxATab)
        self.buttons.comboBoxATab.setHidden(True)

        self.buttons.comboBoxATabScripts = QComboBox(self)
        #self.buttons.comboBoxATabScripts.setToolTip('Sensor/Image mode for input images')


        self.toolbar.addWidget(self.buttons.comboBoxATabScripts)
        self.buttons.comboBoxATabScripts.setHidden(True)

        self.buttons.annotation_switch = QCheckBox("Annotation")
        self.buttons.annotation_switch.stateChanged.connect(lambda: self.flipAnnotation(self.buttons.annotation_switch))
        self.buttons.annotation_switch.setChecked(self.parent.ANNOTATIONS_MODE)
        self.buttons.annotation_switch.setStyleSheet(QCHECKBOX_LOOK_AND_FEEL)

        self.buttons.convert_midx_to_idx = createPushButton("Save IDX",
                                                            lambda: parent.convertMIDXtoIDXFile())
        self.buttons.convert_midx_to_idx.setToolTip('Save out IDX file for copying to server')
        self.buttons.save_screenshot = createPushButton("",
                                                        lambda: parent.saveScreenshot())
        self.buttons.save_screenshot.setToolTip('Save screenshot')
        # self.buttons.resetView = createPushButton("",
        #                                           lambda: parent.resetView())
        # self.buttons.resetView.setToolTip('Reset Viewpoint to see full mosaic')
        # self.buttons.resetView.setIcon(QIcon('icons/resetView.png'))
        # fixButtonsLookFeel(self.buttons.resetView)

        # self.buttons.toggleGoogleMapBtn = QPushButton('', self)
        # icon = QIcon()
        # icon.addPixmap(QPixmap('icons/googleMapGray.png'),QIcon.Normal, QIcon.Off)
        # icon.addPixmap(QPixmap('icons/googleMapGreen.png'), QIcon.Normal, QIcon.On)
        # self.buttons.toggleGoogleMapBtn.setToolTip('Toggle on/off Google Map background')
        #
        # self.buttons.toggleGoogleMapBtn.setIcon(icon)
        # self.buttons.toggleGoogleMapBtn.clicked.connect(self.toggleGoogleMap)
        # self.buttons.toggleGoogleMapBtn.setCheckable(True)
        # self.buttons.toggleGoogleMapBtn.setChecked(False)
        # fixButtonsLookFeel(self.buttons.toggleGoogleMapBtn)


        self.buttons.oneViewButton = QPushButton('', self)  #createPushButton("", lambda: self.oneView())
        self.buttons.oneViewButton.setToolTip('Change to a single panel view')
        #self.buttons.oneViewButton.setIcon(QIcon('icons/oneViewer_gray.png'))
        icon = QIcon()
        icon.addPixmap(QPixmap('icons/oneViewer_gray.png'),QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap('icons/oneViewer.png'), QIcon.Normal, QIcon.On)
        self.buttons.oneViewButton.setIcon(icon)
        self.buttons.oneViewButton.clicked.connect(self.oneView)
        self.buttons.oneViewButton.setCheckable(True)
        self.buttons.oneViewButton.setChecked(True)

        self.buttons.sideBySideViewButton = QPushButton('', self)  #createPushButton("",  lambda: self.sidebySideView())
        #self.buttons.sideBySideViewButton.setIcon(QIcon('icons/sideBySide.png'))
        icon = QIcon()
        icon.addPixmap(QPixmap('icons/sideBySide_gray.png'),QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap('icons/sideBySide.png'), QIcon.Normal, QIcon.On)
        self.buttons.sideBySideViewButton.setIcon(icon)
        self.buttons.sideBySideViewButton.clicked.connect(self.sidebySideView)
        self.buttons.sideBySideViewButton.setCheckable(True)
        self.buttons.sideBySideViewButton.setChecked(False)
        self.buttons.sideBySideViewButton.setToolTip('Change to a side by side view, each with their own camera')

        self.buttons.sideBySideViewLinkButton = QPushButton('', self) #createPushButton("",lambda: self.sidebySideViewLink())
        self.buttons.sideBySideViewLinkButton.setIcon(QIcon('icons/sideBySideLink_gray.png'))
        icon = QIcon()
        icon.addPixmap(QPixmap('icons/sideBySideLink_gray.png'),QIcon.Normal, QIcon.Off)
        icon.addPixmap(QPixmap('icons/sideBySideLink.png'), QIcon.Normal, QIcon.On)
        self.buttons.sideBySideViewLinkButton.setIcon(icon)
        self.buttons.sideBySideViewLinkButton.clicked.connect(self.sidebySideViewLink)
        self.buttons.sideBySideViewLinkButton.setCheckable(True)
        self.buttons.sideBySideViewLinkButton.setChecked(False)
        self.buttons.sideBySideViewLinkButton.setToolTip('Change to a side by side view with linked cameras')

        self.button_views =  QToolButton(self )
        self.button_views.setIconSize(QSize(V_LIST_DATES, V_BUTTON_SIZE_SM))
        self.button_views.resize(V_LIST_DATES, V_BUTTON_SIZE_SM)
        self.button_views.setFixedSize(V_LIST_DATES, V_BUTTON_SIZE_SM)
        self.button_views.setToolTip('Menu for changing views for the app')
        self.button_views.clicked.connect(lambda: self.showViewMenuOptions())


        self.button_views.setText('View')

        self.button_views.setPopupMode( QToolButton.MenuButtonPopup)
        self.button_views.setMenu( QMenu(self.button_views))
        #self.textBox =  QTextBrowser(self)

        # self.buttons.openMyMapWidget = createPushButton("",
        #                                             lambda: self.addMyMapWidgetWindow())
        #
        # self.buttons.openMyMapWidget.setIcon(QIcon('icons/palette.png'))
        # fixButtonsLookFeel(self.buttons.openMyMapWidget)
        # self.buttons.openMyMapWidget.setToolTip('Allows changing of color map used for NDVI/TGI scripts')

        self.buttons.mail_screenshot = createPushButton("",
                                                        lambda: self.parent.mailScreenshot())

        self.buttons.mail_screenshot.setIcon(QIcon('icons/MailImage.png'))
        fixButtonsLookFeel(self.buttons.mail_screenshot)
        self.buttons.mail_screenshot.setToolTip('Mail screen shot pop-up')

        self.buttons.openPythonWindow = createPushButton("",
                                                         lambda: self.addScriptingWindow())

        self.buttons.openPythonWindow.setIcon(QIcon('icons/ConsoleGreen.png'))
        fixButtonsLookFeel(self.buttons.openPythonWindow)
        self.buttons.openPythonWindow.setToolTip('Python scripting pop-up')

        # self.buttons.openLayersWindowBtn = createPushButton("",
        #                                                  lambda: self.openLayersWindow())
        #
        # self.buttons.openLayersWindowBtn.setIcon(QIcon('icons/LayersGreen.png'))
        # fixButtonsLookFeel(self.buttons.openLayersWindowBtn)
        # self.buttons.openLayersWindowBtn.setToolTip('View Layers controls')

        self.buttons.mail_bug = createPushButton("",
                                                        lambda: self.parent.mailBug())
        self.buttons.mail_bug.setIcon(QIcon('icons/Bug.png'))
        fixButtonsLookFeel(self.buttons.mail_bug)
        #self.buttons.mail_bug.setIcon(QIcon('icons/cloud.png'))
        self.buttons.mail_bug.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.mail_bug.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.mail_bug.setFixedSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.mail_bug.setToolTip('Mail a bug to support')

        self.buttons.cloud = createPushButton("",
                                                        lambda: self.parent.saveToCloud())
        self.buttons.cloud.setIcon(QIcon('icons/cloud.png'))
        fixButtonsLookFeel(self.buttons.cloud)

        self.buttons.cloud.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.cloud.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.cloud.setFixedSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.cloud.setToolTip('Convert to IDX, and create script for background upload to ViSUS dataportal')

        #action0 =  QWidgetAction(self.button_views)
        action1 =  QWidgetAction(self.button_views)
        action2 =  QWidgetAction(self.button_views)
        action3 =  QWidgetAction(self.button_views)
        #action4 =  QWidgetAction(self.button_views)
        #action5 =  QWidgetAction(self.button_views)
        #action0.setDefaultWidget(self.buttons.resetView)
        action1.setDefaultWidget(self.buttons.oneViewButton)
        action2.setDefaultWidget(self.buttons.sideBySideViewButton)
        action3.setDefaultWidget(self.buttons.sideBySideViewLinkButton)
        #action4.setDefaultWidget(self.buttons.openLayersWindowBtn)
        #action5.setDefaultWidget(self.buttons.toggleGoogleMapBtn)
        #self.button_views.menu().addAction(action0)
        self.button_views.menu().addAction(action1)
        self.button_views.menu().addAction(action2)
        self.button_views.menu().addAction(action3)
        #self.button_views.menu().addAction(action4)
        #self.button_views.menu().addAction(action5)
        self.button_views.setStyleSheet(MY_COMBOX)
        self.button_views.setStyleSheet(MY_QTOOLBOX)
        self.button_views.setStyleSheet(WHITE_TOOL_BUTTON)
        self.button_views.setStyleSheet('border: 2px solid #045951;padding:0px')


        if ENABLE_SAVE_IDX:
            self.toolbar.addWidget(self.buttons.convert_midx_to_idx, alignment=Qt.AlignLeft)
        # self.toolbar.addWidget(self.buttons.annotation_switch)
        # self.toolbar.addSpacing(10)
        #self.toolbar.addWidget(self.buttons.resetView)
       # self.toolbar.addSpacing(10)
       #  self.toolbar.addWidget(self.buttons.toggleGoogleMapBtn)
       #  self.toolbar.addSpacing(10)

        self.toolbar.addWidget(self.button_views, alignment=Qt.AlignLeft)
        self.toolbar.addSpacing(10)

        # self.toolbar.addWidget(self.buttons.oneViewButton)
        # self.toolbar.addSpacing(10)
        # self.toolbar.addWidget(self.buttons.sideBySideViewButton)
        # self.toolbar.addSpacing(10)
        # self.toolbar.addWidget(self.buttons.sideBySideViewLinkButton)
        # self.toolbar.addSpacing(10)
        self.toolbar.addWidget(self.buttons.save_screenshot, alignment=Qt.AlignLeft)
        self.toolbar.addSpacing(10)
        self.toolbar.addWidget(self.buttons.mail_screenshot, alignment=Qt.AlignLeft)
        #self.toolbar.addSpacing(True)
        self.toolbar.addWidget(self.buttons.openPythonWindow, alignment=Qt.AlignRight)
        self.toolbar.addSpacing(10)
        # self.toolbar.addWidget(self.buttons.openLayersWindowBtn)
        # self.toolbar.addSpacing(100)
        #self.toolbar.addWidget(self.buttons.openMyMapWidget, alignment=Qt.AlignRight)
        #self.toolbar.addStretch(10)

        self.toolbar.addWidget(self.buttons.mail_bug, alignment=Qt.AlignRight)
        self.toolbar.addStretch(10)
        self.toolbar.addWidget(self.buttons.cloud, alignment=Qt.AlignRight)


        self.buttons.convert_midx_to_idx.setStyleSheet(WHITE_PUSH_BUTTON)
        # self.buttons.save_screenshot.setStyleSheet(WHITE_PUSH_BUTTON)
        #self.buttons.resetView.setStyleSheet(WHITE_PUSH_BUTTON)
        # self.buttons.openPythonWindow.setStyleSheet(WHITE_PUSH_BUTTON)

        ic = QIcon('icons/CameraGreen.png')
        self.buttons.save_screenshot.setIcon(ic)
        fixButtonsLookFeel(self.buttons.save_screenshot)
        fixButtonsLookFeel(self.buttons.sideBySideViewButton)
        fixButtonsLookFeel(self.buttons.oneViewButton)
        #fixButtonsLookFeel(self.buttons.resetView)
        fixButtonsLookFeel(self.buttons.sideBySideViewLinkButton)


        self.sublayoutTabViewer.addLayout(self.toolbar)
        self.sublayoutTabViewer.addWidget(self.parent.openfilenameLabel)

        if self.TOPBOTTOM_VIEWER:
            # Viewer
            #self.sublayoutTabViewer.addWidget(self.parent.viewer_subwin)
            self.sublayoutTabViewer.addWidget(self.parent.viewerW)
            # Viewer
            #self.sublayoutTabViewer.addWidget(self.parent.viewer_subwin2)
            self.sublayoutTabViewer.addWidget(self.parent.viewerW2)
        else:
            self.sublayoutViewer = QHBoxLayout()
            # Viewer
            #self.sublayoutViewer.addWidget(self.parent.viewer_subwin)
            self.sublayoutViewer.addWidget(self.parent.viewerW)
            # Viewer
            #elf.sublayoutViewer.addWidget(self.parent.viewer_subwin2)
            self.sublayoutViewer.addWidget(self.parent.viewerW2)
            self.sublayoutTabViewer.addLayout(self.sublayoutViewer )

        self.parent.setUpCams()

        self.setLayout(self.sublayoutTabViewer)
        if self.DEBUG:
            print('tabViewerUI finished')

        self.parent.inputModeChanged()

    def showViewMenuOptions(self):

        point = self.button_views.rect().bottomRight()
        global_point = self.button_views.mapToGlobal(point)
        self.button_views.menu().move(global_point - QtCore.QPoint(self.button_views.menu().width(), 0))
        self.button_views.menu().show()

    def flipAnnotation(self, btn):
        self.SVG_ON = not self.SVG_ON

        self.parent.setAnnotations(self.SVG_ON)
        self.buttons.annotation_switch.setChecked(self.SVG_ON)
        print('Flipped color_matching: {0}'.format(self.SVG_ON))
        self.setSVGNodeVisibility(self.parent.projectInfo.projDir, self.SVG_ON)

    def toggleGoogleMap(self):
        print('-----------------> toggleGoogleMap')
        print(self.buttons.toggleGoogleMapBtn.isChecked())
        if self.buttons.toggleGoogleMapBtn.isChecked():
            #if (self.parent.SHOW_GOGGLE_MAP):
            self.parent.SHOW_GOGGLE_MAP = True
            print('SHOW_GOGGLE_MAP True')
            #self.buttons.toggleGoogleMapBtn.setIcon(QIcon('icons/googleMapGray.png'))
        else:
            self.parent.SHOW_GOGGLE_MAP = False
            print('SHOW_GOGGLE_MAP False')
            #self.buttons.toggleGoogleMapBtn.setIcon(QIcon('icons/googleMapGreen.png'))
        self.update()
        self.parent.openMIDX( )



    def oneView(self):
        self.buttons.sideBySideViewLinkButton.setChecked(False)
        self.buttons.sideBySideViewButton.setChecked(False)
        self.buttons.oneViewButton.setChecked(True)

        #self.buttons.sideBySideViewButton.setIcon(QIcon('icons/sideBySide_gray.png'))
        #self.buttons.sideBySideViewLinkButton.setIcon(QIcon('icons/sideBySideLink_gray.png'))
        #self.buttons.oneViewButton.setIcon(QIcon('icons/oneViewer.png'))
        self.update()
        self.parent.oneView()

    def sidebySideViewLink(self):
        self.parent.LINK_CAMERAS = True
        self.buttons.sideBySideViewLinkButton.setChecked(True)
        self.buttons.sideBySideViewButton.setChecked(False)
        self.buttons.oneViewButton.setChecked(False)

        #self.buttons.sideBySideViewLinkButton.setIcon(QIcon('icons/sideBySideLink.png'))
        #self.buttons.sideBySideViewButton.setIcon(QIcon('icons/sideBySide_gray.png'))
        #self.buttons.oneViewButton.setIcon(QIcon('icons/oneViewer_gray.png'))
        self.update()
        self.parent.sidebySideView()

    def sidebySideView(self):
        self.parent.LINK_CAMERAS = False
        self.buttons.sideBySideViewLinkButton.setChecked(False)
        self.buttons.sideBySideViewButton.setChecked(True)
        self.buttons.oneViewButton.setChecked(False)

        #self.buttons.sideBySideViewLinkButton.setIcon(QIcon('icons/sideBySideLink_gray.png'))
        #self.buttons.sideBySideViewButton.setIcon(QIcon('icons/sideBySide.png'))
        #self.buttons.oneViewButton.setIcon(QIcon('icons/oneViewer_gray.png'))
        self.update()
        self.parent.sidebySideView()

    def inputModeChangedATab(self):
        self.parent.inputMode = self.buttons.comboBoxATab.currentText()

        if (self.parent.inputMode == "R G B"):
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR_normalized', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_Threshold', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI_Threshold', True)
        elif (self.parent.inputMode == "R NIR (Sentera NDVI)"):
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR_normalized', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI_Threshold', False)
        elif (self.parent.inputMode == "MapIR only (OCNIR)"):
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR_normalized', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI_Threshold', False)
        elif (self.parent.inputMode == "RedEdge NIR (Sentera NDRE)"):
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR_normalized', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI_Threshold', False)
        elif (self.parent.inputMode == "R G NIR"):
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR_normalized', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI', False)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI_Threshold', False)
        elif (self.parent.inputMode == "Unknown"):
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_MAPIR_normalized', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'NDVI_Threshold', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI', True)
            self.parent.setEnabledCombobxItem(self.buttons.comboBoxATabScripts, 'TGI_Threshold', True)

        self.parent.inputModeChanged()

    def addScriptingWindow(self):
        self.parent.pythonScriptingWindow.on_show()

    def runScript(self, name):
        fieldname = "output=ArrayUtils.interleave(ArrayUtils.split(voronoi())[0:3])"
        print("Showing NDVI for Red and IR channels")

        self.parent.openMIDX()
        # if self.parent.SHOW_GOGGLE_MAP:
        #     url = os.path.join(self.parent.projectInfo.cache_dir, "visus.midx")
        # else:
        #     url = os.path.join(self.parent.projectInfo.cache_dir, "google.midx")
        #
        # self.parent.viewer.open(url)
        # self.parent.viewer2.open(url)

        # make sure the RenderNode get almost RGB components
        #self.parent.viewer.setFieldName(fieldname)
        self.parent.viewer2.setFieldName(fieldname)

        # for Amy: example about processing
        # if False:
        print('FUNCTION: RunScript : ' + name)
        #self.parent.app_dir = os.getcwd()
        script = getTextFromScript(os.path.join(self.parent.app_dir, 'scripts', name + '.py'))

        #self.parent.viewer.setScriptingCode(script)
        self.parent.viewer2.setScriptingCode(script)

    def runThisScript(self, script,viewer):
        fieldname = "output=ArrayUtils.interleave(ArrayUtils.split(voronoi())[0:3])"
        print("Showing NDVI for Red and IR channels")
        #self.parent.openMIDX()
        # if self.parent.SHOW_GOGGLE_MAP:
        #     url = os.path.join(self.parent.projectInfo.cache_dir, "visus.midx")
        # else:
        #     url = os.path.join(self.parent.projectInfo.cache_dir, "google.midx")
        #
        # self.parent.viewer.open(url)
        # self.parent.viewer2.open(url)

        # make sure the RenderNode get almost RGB components
        # self.parent.viewer.setFieldName(fieldname)
        viewer.setFieldName(fieldname)

        # self.parent.viewer.setScriptingCode(script)
        viewer.setScriptingCode(script)

        # showThreshold
    #
    # def show_threshold_NDVI(self):
    #     self.runScript('NDVI_Threshold')
    #     if self.DEBUG:
    #         print('showThreshold finished')
    #
    #     # showThreshold
    #
    # def showThreshold_TGI(self):
    #     self.runScript('TGI_Threshold')
    #     if self.DEBUG:
    #         print('showThreshold finished')
    #
    #     # showThreshold
    #
    # def showCount(self):
    #     self.runScript('Count')
    #     if self.DEBUG:
    #         print('showThreshold finished')
    #
    #     # showNDVI
    #
    # def showNDVI(self):
    #     self.runScript('NDVI')
    #     if self.DEBUG:
    #         print('showNDVI finished')
    #
    #     # showTGI (for RGB datasets)
    #
    # def showTGI(self):
    #     self.runScript('TGI')
    #     if self.DEBUG:
    #         print('showTGI finished')

    def showRGB(self):
        fieldname = "output=ArrayUtils.interleave(ArrayUtils.split(voronoi())[0:3])"
        print("Showing NDVI for Red and IR channels")
        self.parent.openMIDX()
        # if self.parent.SHOW_GOGGLE_MAP:
        #     url = os.path.join(self.parent.projectInfo.cache_dir, "visus.midx")
        # else:
        #     url = os.path.join(self.parent.projectInfo.cache_dir, "google.midx")
        # self.parent.viewer.open(url)
        # self.parent.viewer2.open(url)

        fieldname = "output=ArrayUtils.interleave(ArrayUtils.split(voronoi())[0:3])"
        print("Showing img src")
        # self.viewer.open(self.projDir + '/VisusSlamFiles/visus.midx' )
        # make sure the RenderNode get almost RGB components
        self.parent.viewer.setFieldName(fieldname)
        self.parent.viewer.setScriptingCode(
"""
output=input
""".strip())
        self.parent.viewer2.setFieldName(fieldname)
        self.parent.viewer2.setScriptingCode(
            """
            output=input
            """.strip())
        #self.saveThumbNailImg()
        if self.DEBUG:
            print('showRGB finished')

    #def saveThumbNailImg(self):
        # self.parent.saveScreenshot(False)
        # return
        # self.parent.projectInfo.cache_dir = os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles')
        # cur_path =  os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX')
        # # path = Path(self.cache_dir + '/' + self.projName + 'IDX')
        # if not os.path.exists(cur_path):
        #     os.makedirs(cur_path)
        # # os.makedirs(cur_path, exist_ok=True)
        # # nPath = Path(cur_path)
        # # nPath.parent.mkdir(parents=True, exist_ok=True)
        # # self.parent.viewer.takeSnapshot(True,  self.cache_dir+ '/'+self.projName+'IDX/'+'Thumbnail.png')
        # fileName = os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX',  'Thumbnail.png')
        #
        # print('saving Thumbnail {0}'.format(fileName ))
        # self.parent.viewer2.takeSnapshot(True,  fileName)



    def setSVGNodeVisibility(self, projDir, visibility):
        #
        tree = ET.parse(os.path.join(projDir, 'VisusSlamFiles', 'visus.midx'))
        wrapperdataset = tree.getroot()

        for svgnode in wrapperdataset.iterfind('svg'):
            if visibility:
                svgnode.set('visibility','visible')
                print('set svg visibile')
            else:
                svgnode.set('visibility', 'hidden')
                print('set svg hidden')
        tree.write(os.path.join(projDir, 'VisusSlamFiles', 'visus.midx'))

        self.parent.openMIDX()

    def annotationsEnabled(self):
        return self.buttons.annotation_switch.isChecked()