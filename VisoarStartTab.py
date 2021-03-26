
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


class VisoarStartTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.DEBUG = True
        self.setStyleSheet(LOOK_AND_FEEL)

        class Buttons:
            pass

        self.layout = QVBoxLayout()
        self.choicelayoutTop = QHBoxLayout()
        self.choicelayout = QHBoxLayout()

        self.layout.setSpacing(GRID_SPACING)

        self.buttons = Buttons

        self.buttonMoveCardData = QPushButton('Process Drone Memory Card', self)
        self.buttonMoveCardData.resize(180, 40)
        self.buttonMoveCardData.clicked.connect(self.moveDataFromCard)
        self.buttonMoveCardData.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttonMoveCardData.resize(self.buttonMoveCardData.sizeHint().width(), self.buttonMoveCardData.sizeHint().height())
        self.choicelayoutTop.addStretch(True)
        self.choicelayoutTop.addWidget(self.buttonMoveCardData, alignment=Qt.AlignLeft)
        self.choicelayoutTop.addStretch(True)


        self.buttonBatchProcess = QPushButton('Batch Process Stitching of Directories', self)
        self.buttonBatchProcess.resize(180, 40)
        self.buttonBatchProcess.clicked.connect(self.startBatchProcess)
        self.buttonBatchProcess.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttonBatchProcess.resize(self.buttonBatchProcess.sizeHint().width(), self.buttonBatchProcess.sizeHint().height())
        self.choicelayoutTop.addStretch(True)
        self.choicelayoutTop.addWidget(self.buttonBatchProcess, alignment=Qt.AlignLeft)
        self.choicelayoutTop.addStretch(True)


        self.buttonStitching = QPushButton('Start Stitching', self)
        self.buttonStitching.resize(180, 40)
        self.buttonStitching.clicked.connect(self.startStitching)
        self.buttonStitching.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttonStitching.resize(self.buttonStitching.sizeHint().width(), self.buttonStitching.sizeHint().height())
        self.choicelayout.addStretch(True)
        self.choicelayout.addWidget(self.buttonStitching, alignment=Qt.AlignLeft)
        self.choicelayout.addStretch(True)


        self.buttonTimeSeries = QPushButton('Start Time Series', self)
        self.buttonTimeSeries.resize(180, 40)
        self.buttonTimeSeries.clicked.connect(self.startTimeSeries)
        self.buttonTimeSeries.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttonTimeSeries.resize(self.buttonTimeSeries.sizeHint().width(), self.buttonTimeSeries.sizeHint().height())
        self.choicelayout.addWidget(self.buttonTimeSeries, alignment=Qt.AlignCenter)
        self.choicelayout.addStretch(True)


        self.layout.addStretch(True)
        self.layout.addLayout(self.choicelayoutTop)
        self.layout.addStretch(True)
        self.layout.addLayout(self.choicelayout)
        self.layout.addStretch(True)

        self.buttonLoad = QPushButton('Load From Library', self)
        self.buttonLoad.resize(180, 40)
        self.buttonLoad.clicked.connect(self.loadFromUserLibrary)
        self.buttonLoad.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttonLoad.resize(self.buttonLoad.sizeHint().width(),self.buttonLoad.sizeHint().height())
        self.layout.addWidget(self.buttonLoad, alignment=Qt.AlignCenter)
        # self.layout.addStretch(True)

        self.logo = QPushButton('', self)
        self.logo.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        self.logo.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'visoar_logo.png')))
        self.logo.setIconSize(QSize(480, 214))

        self.logo.setText('')

        self.layout.addWidget(self.logo)

        self.setLayout(self.layout)

    def moveDataFromCard(self):
        self.parent.enableViewMoveDataFromCards()
        self.parent.changeViewMoveDataFromCards()

    def startBatchProcess(self):
        self.parent.enableViewBatchProcess()
        self.parent.changeViewBatchProcess()

    def startStitching(self):
        self.parent.enableViewNewStitch()
        self.parent.changeViewNewStitch()


    def startTimeSeries(self):
        self.parent.enableViewNewTimeSeries()
        self.parent.changeViewNewTimeSeries()


    def loadFromUserLibrary(self):
        self.parent.enableViewLoad()
        self.parent.changeViewLoad()
