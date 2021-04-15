from VisoarSettings             import *

from PyQt5.QtWebEngineWidgets         import QWebEngineView

from OpenVisus                        import *
from OpenVisus.gui                    import *

from PyQt5.QtGui 					  import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFileDialog

from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem


class VisoarStitchTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.DEBUG = True
        self.color_matching = False
        self.setStyleSheet(LOOK_AND_FEEL)
        #def tabStitcherUI(self):
        if self.DEBUG:
            print('tabStitcherUI started')
        self.sublayoutTabStitcher = QVBoxLayout()
        # AAG: 05152020 was:
        # self.sublayoutTabStitcher= QVBoxLayout(self)

        class Buttons:
            pass

        self.buttons = Buttons

        # toolbar
        toolbar = QHBoxLayout()
        # self.buttons.load_midx=createPushButton("Load Prev Solution",
        # 	lambda: self.loadPrevSolution())

        #self.cmatch_group = QHBoxLayout()
        # self.cmatchLabel = QLabel('Preprocess: ')
        # self.cmatchLabel.setStyleSheet(
        #     "min-height:20; min-width:100;margin:0px; padding:0px; background-color: #ffffff;  ")

        self.cmatch_switch = QCheckBox("Color Preprocess")
        self.cmatch_switch.stateChanged.connect(lambda: self.flipColorMatch(self.cmatch_switch))
        #self.cmatch_switch = MySwitch()
        self.cmatch_switch .setChecked(False)
        # self.cmatch_switch.setStyleSheet("""QCheckBox::indicator:unchecked {image: url(:""" +
        #                                  os.path.join(self.parent.app_dir, 'icons', 'unchecked.png') + """);}""")
        # self.cmatch_switch.setStyleSheet("""QCheckBox::indicator:checked {image: url(:""" +
        #                                  os.path.join(self.parent.app_dir, 'icons', 'checked.png') + """);}""")

        #self.cmatch_switch.clicked.connect(self.flipColorMatch)
        self.cmatch_switch.setStyleSheet(QCHECKBOX_LOOK_AND_FEEL)
        #self.cmatch_group.addWidget(self.cmatchLabel)
        #self.cmatch_group.addWidget(self.cmatch_switch)


        self.buttons.run_slam = createPushButton("Stitch it!",
                                                 lambda: self.run())
        self.buttons.goToAnalytics = createPushButton("Analytics",
                                                      lambda: self.parent.goToAnalyticsTab())

        self.buttons.run_slam.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttons.goToAnalytics.setStyleSheet(DISABLED_PUSH_BUTTON)
        self.buttons.goToAnalytics.setEnabled(False)

        self.buttons.home = QPushButton('', self)
        self.buttons.home.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.home.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'home.png')))
        self.buttons.home.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.home.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.home.clicked.connect(self.parent.goHome)

        # self.buttons.show_ndvi=createPushButton("NDVI",
        # 	lambda: self.showNDVI())

        # self.buttons.show_tgi=createPushButton("TGI",
        # 	lambda: self.showTGI())

        # self.buttons.show_rgb=createPushButton("RGB",
        # 	lambda: self.showRGB())

        #		toolbar.addWidget(self.buttons.load_midx)
        toolbar.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        toolbar.addWidget(self.cmatch_switch)
        toolbar.addWidget(self.buttons.run_slam)
        toolbar.addWidget(self.buttons.goToAnalytics)
        # toolbar.addWidget(self.buttons.show_ndvi)
        # toolbar.addWidget(self.buttons.show_tgi)
        # toolbar.addWidget(self.buttons.show_rgb)

        self.buttons.resetViewBtn = createPushButton("",
                                                  lambda: parent.resetView())
        self.buttons.resetViewBtn.setIcon(QIcon('icons/resetView.png'))
        fixButtonsLookFeel(self.buttons.resetViewBtn)
        toolbar.addWidget(self.buttons.resetViewBtn)

        self.buttons.save_screenshot = createPushButton("",
                                                        lambda: self.parent.saveScreenshot())
        toolbar.addWidget(self.buttons.save_screenshot)
        toolbar.addSpacing(10)

        ic = QIcon('icons/CameraGreen.png')
        self.buttons.save_screenshot.setIcon(ic)
        fixButtonsLookFeel(self.buttons.save_screenshot)


        self.buttons.mail_screenshot = createPushButton("",
                                                        lambda: self.parent.mailScreenshot())
        toolbar.addWidget(self.buttons.mail_screenshot)
        toolbar.addSpacing(10)

        self.buttons.mail_screenshot.setIcon(QIcon('icons/MailImage.png'))
        fixButtonsLookFeel(self.buttons.mail_screenshot)

        # empty = QWidget()
        # empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # toolbar.addWidget(empty)
        toolbar.addSpacing(100)

        self.buttons.mail_bug = createPushButton("",
                                                        lambda: self.parent.mailBug())
        toolbar.addWidget(self.buttons.mail_bug, alignment=Qt.AlignRight )
        fixButtonsLookFeel(self.buttons.mail_bug)
        self.buttons.mail_bug.setIcon(QIcon('icons/Bug.png'))
        self.buttons.mail_bug.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.mail_bug.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.mail_bug.setFixedSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)

        # self.quitButton  = self.addQuitButton()
        # toolbar.addWidget(self.quitButton)

        toolbar.addStretch(1)
        if self.parent.USER_TAB_UI:
            self.sublayoutTabStitcher.addLayout(toolbar)
        else:
            self.sublayoutTabStitcher.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        self.sublayoutTabStitcher.addWidget(self.parent.openfilenameLabelS)
        self.sublayoutTabStitcher.addWidget(self.parent.slam_widget)
        self.setLayout(self.sublayoutTabStitcher)

        if self.DEBUG:
            print('tabStitcherUI finished')

    # User has specified location for data and the project name, launch ViSUS SLAM

    def flipColorMatch(self, btn):
        self.color_matching = not self.color_matching
        self.cmatch_switch.setChecked(self.color_matching)
        print('Flipped color_matching: {0}'.format(self.color_matching))

    def getPhysicsBoxFromMIDX(self, midx_in):
        print(midx_in)
        value = ''
        tree = ET.parse(midx_in)
        dataset = tree.getroot()
        print('-0-0-0-0-0-0-0-0-0-0-')
        print(dataset.attrib['physic_box'])
        print('-0-0-0-0-0-0-0-0-0-0-')
        return str(dataset.attrib['physic_box'])

    def run(self):
        #try:
        self.parent.openfilenameLabelS.setText("Starting to Stitch: "+ self.parent.projectInfo.srcDir )
        if self.parent.tabAskSensor.comboBoxNewTab.currentText() == 'Agrocam':
            print("Note to self, taking out slam default changes")
            #            self.parent.slam_widget.setDefaults(color_matching=self.color_matching)
            if not (os.path.exists(os.path.join(self.parent.projectInfo.srcDir, 'VisusSlamFiles'))):
                os.makedirs(os.path.join(self.parent.projectInfo.srcDir, 'VisusSlamFiles'))

            if not self.parent.slam:
                self.parent.slam = Slam2d()

            self.parent.slam.setImageDirectory(image_dir=self.parent.projectInfo.srcDir,
                                                      cache_dir=os.path.join(self.parent.projectInfo.srcDir, 'VisusSlamFiles'))
            ret = self.parent.slam_widget.run(self.parent.slam)
            ret2 = self.parent.slam_widget.slam.run()

            #Now, we have to parse the midx from the RGB data set and send it into the NDVI one:
            # <dataset typename='IdxMultipleDataset' logic_box='0 33219 0 9355' physic_box='0.18167907760636232 0.18178016271080077 0.63092731395604973 0.63093683616193741'>
            physbox = self.getPhysicsBoxFromMIDX(os.path.join(self.parent.projectInfo.srcDir, 'VisusSlamFiles', 'visus.midx'))

            from shutil import copyfile
            if (os.path.exists(self.parent.projectInfo.srcDirNDVI)):
                if not (os.path.exists(os.path.join(self.parent.projectInfo.srcDirNDVI,'VisusSlamFiles'))):
                    os.makedirs(os.path.join(self.parent.projectInfo.srcDirNDVI,'VisusSlamFiles'))
                copyfile(os.path.join( self.parent.projectInfo.srcDir, 'VisusSlamFiles','metadata.json'),
                        os.path.join(self.parent.projectInfo.srcDirNDVI, 'VisusSlamFiles','metadata.json'))

            self.parent.openfilenameLabelS.setText(
                "Starting to Stitch: " +  self.parent.projectInfo.srcDirNDVI)
            if not self.parent.slam:
                self.parent.slam = Slam2d()
            self.parent.slam.setImageDirectory(image_dir= self.parent.projectInfo.srcDirNDVI,
                                                      cache_dir= os.path.join(self.parent.projectInfo.srcDirNDVI, 'VisusSlamFiles'),
                                                      telemetry=os.path.join(self.parent.projectInfo.srcDirNDVI, 'VisusSlamFiles/metadata.json'),
                                                      physic_box=physbox)

            ret2 = self.parent.slam_widget.run(self.parent.slam)
            ret2 = self.parent.slam_widget.slam.run()
            self.parent.createRGBNDVI_MIDX()
        else:
            print("Note to self, taking out slam default changes")
            #self.parent.slam_widget.setDefaults(color_matching=self.color_matching)
            if not self.parent.slam:
                self.parent.slam = Slam2d()
            self.parent.slam.setImageDirectory(image_dir=self.parent.projectInfo.srcDir,
                                                      cache_dir=os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles'))

            ret = self.parent.slam_widget.run(self.parent.slam)
            ret2 = self.parent.slam_widget.slam.run()

            self.parent.projectInfo.cache_dir = os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles')
            if (ret):
                self.buttons.goToAnalytics.setEnabled(True)
                self.buttons.goToAnalytics.setStyleSheet(GREEN_PUSH_BUTTON)
                self.buttons.run_slam.setStyleSheet(GRAY_PUSH_BUTTON)
                if self.DEBUG:
                    print('run finished')
                # msg = QMessageBox()
                # msg.setWindowTitle('Images Stitched')
                # msg.setText('Images Stitched\n \tYou can now press Analytics Button.')
                # msg.setStyleSheet(POPUP_LOOK_AND_FEEL)
                # x = msg.exec_()
                #self.parent.setUpRClone()
                if not self.parent.USER_TAB_UI:
                    self.parent.goToAnalyticsTab()
            else:
                popUP('Slam failed','ERROR 101: Visus Slam failed')
                self.parent.enableViewNewStitch()
        # except:
        #    popUP('Slam failed', 'ERROR 102: Visus Slam failed')
        #    self.parent.changeViewNewStitch()
        #    return False