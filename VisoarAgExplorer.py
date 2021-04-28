#import sys, os
#sys.path.append('/Users/amygooch/.pyenv/versions/3.6.8/lib/python3.6/site-packages')

from VisoarSettings import *

#from slam2dWidget import *

from ViSOARUIWidget import *
from slampy.utils import *
# memory card -> local directory
if (sys.platform.startswith('win')):
    LOCAL_DIR="c:/visoar_files"
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)
else:
    if os.path.exists("/Users/amygooch/"):
        LOCAL_DIR="/Users/amygooch/"
        if not os.path.exists(os.path.join(LOCAL_DIR, 'visoar_sync_files')):
            os.makedirs(os.path.join(LOCAL_DIR, 'visoar_sync_files'))
    else:
        LOCAL_DIR =  os.getcwd()
        if not os.path.exists(os.path.join(LOCAL_DIR, 'visoar_sync_files')):
            os.makedirs(os.path.join(LOCAL_DIR, 'visoar_sync_files'))

T1=datetime.datetime.now()

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


class MyPopup(QWidget):
    def __init__(self):
        QWidget.__init__(self)

    def paintEvent(self, e):
        dc = QPainter(self)
        dc.drawLine(0, 0, 100, 100)
        dc.drawLine(100, 0, 0, 100)


class VisoarAgExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ViSOAR Ag Explorer Prototype')
        # print('OpenCV version:  ')
        # print(cv2.__version__)
        self.setMinimumSize(QSize(600, 800))
        self.setStyleSheet(LOOK_AND_FEEL)
        #self.showMaximized()
        #self.setWindowFlags(
        #    self.windowFlags() | Qt.WindowStaysOnTopHint)  # set always on top flag, makes window disappear

        screen = QDesktopWidget().screenGeometry()


        self.central_widget = QFrame()
        self.central_widget.setFrameShape(QFrame.NoFrame)


        self.DEBUG = True

        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)

        self.tab_widget = ViSOARUIWidget(self)
        self.setCentralWidget(self.tab_widget)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # self.showNormal()
        # self.raise_()
        # self.activateWindow()
        if self.DEBUG:
            print('VisoarAgExplorer init finished')

        self.isWINDOWS = (sys.platform.startswith("win") or
                          (sys.platform == 'cli' and os.name == 'nt'))
        #self.center()
        if (self.isWINDOWS):
            #I hate maximized window when developing, but Weston seems to miss buttons if it is not full screen
            self.showMaximized()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tabWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())
        if self.DEBUG:
            print('on_click finished')

    def onChange(self):
        QMessageBox.information(self,
                                "Tab Index Changed!",
                                "Current Tab Index: ")
        if self.DEBUG:
            print('onChange finished')

    def printLog(self, text):
        self.tab_widget.printLog(text)
        if self.DEBUG:
            print('printLog finished')


# //////////////////////////////////////////////////////////////////////////////

# //////////////////////////////////////////////
def Main(argv):
    SetCommandLine("__main__")
    LogFile(Utils.NormalizePath(os.path.join(LOCAL_DIR, T1.strftime("%Y%m%d.%H%M%S") + ".visoar.sync.log")))
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    app.setStyle("Fusion")

    visoarGreen = '#045951'  # 4,89,81
    visoarGreenRGB = QColor(4, 89, 81)
    visoarRed = '#59040c'
    visoarBlue = '#043759'
    visoarLightGreen = '#067f73'
    visoarDarkGreen = '#02332f'  # 2,51,47
    visoarDarkGreenRGB = QColor(2, 51, 47)
    visoarGreenWebSafe = '#006666'
    visoarHighlightYellow = '#d6d2b1'  # 214,210,177
    visoarHighlightYellowRGB = QColor(214, 210, 177)
    if True:
        palette =  QPalette()
        palette.setColor(QPalette.Window, Qt.white)
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base,  visoarGreenRGB)
        palette.setColor(QPalette.AlternateBase, visoarDarkGreenRGB)
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button,visoarGreenRGB)
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, visoarHighlightYellowRGB)
        palette.setColor(QPalette.Highlight, visoarHighlightYellowRGB.lighter())
        palette.setColor(QPalette.HighlightedText, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.Text, Qt.lightGray)
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.lightGray)
        palette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.lightGray)
        palette.setColor(QPalette.Background, Qt.white)
        palette.setColor(QPalette.Foreground, visoarDarkGreenRGB)
        palette.setColor(QPalette.PlaceholderText, Qt.white)
        palette.setColor(QPalette.BrightText, visoarHighlightYellowRGB)
        app.setPalette(palette)

    # GuiModule.createApplication()
    GuiModule.attach()

    if DEBUG:
        print('Main after attach')

    # since I'm writing data serially I can disable locks
    os.environ["VISUS_DISABLE_WRITE_LOCK"] = "1"
    if DEBUG:
        print('Main after VISUS_DISABLE_WRITE_LOCK')

    if True:
        # Create and display the splash screen
        splash_pix = QPixmap('icons/visoar_logo.png')
        # print('Error with Qt.WindowStaysOnTopHint')
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()
        if DEBUG:
            print('Main after splash init')

    if True:
        print('Setting Fonts.... ' + str(QDir("Roboto")))
        dir_ = QDir("Roboto")
        _id = QFontDatabase.addApplicationFont("./Roboto-Regular.ttf")
        print(QFontDatabase.applicationFontFamilies(_id))

        font = QFont("Roboto")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(20)
        print('ERROR: not sure how to set the font in ViSUS')
        if DEBUG:
            print('Main after fonts')

    # app.setFont(font);

    window = VisoarAgExplorer()
    if DEBUG:
        print('Main after visoar window')

    window.show()
    if DEBUG:
        print('Main after window show')

    # window.showMaximized()

    if True:
        splash.finish(window)
    if DEBUG:
        print('Main after splash close')

    app.exec()
    # GuiModule.execApplication()
    if DEBUG:
        print('Main after app exec')

    # sys.stdout = _stdout
    # sys.stderr = _stderr

    # viewer=None
    GuiModule.detach()
    print("Main All done")


# sys.exit(0)

# //////////////////////////////////////////////
if __name__ == '__main__':
    Main(sys.argv)

# 	<<project>
# 	<projName> "Project2" </projName>
# 	<dir> "/Users/amygooch/GIT/SCI/DATA/FromDale/ag1" </dir>
# </project>
# <<project>
# 	<projName> "Project3" </projName>
# 	<dir> "/Users/amygooch/GIT/SCI/DATA/TaylorGrant/rgb/" </dir>
# </project>
