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

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2, numpy
from gmail_visoar				import *
from datetime import datetime

class ViSOARNDVIImageWidget(QWidget):
    def __init__(self, parent=None, image=None):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        self.originalImagePath = image
        self.saveImagePath = ''
        self.main_layout = QVBoxLayout()
        self.MODE = ''

        self.imageLabel      =  QLabel()
        self.outimageLabel      =  QLabel()
        self.setLayout(self.main_layout)
        self.refreshGui()

    def refreshGui(self):
        self.clearLayout(self.main_layout)


        self.main_layout.addLayout(self.hlayout([
            self.createButton('NDVI (for NIR ONLY)', callback=self.computeNDVIAgrocam),
            self.createButton('TGI (for RGB )', callback=self.computeTGI),
            self.createButton('Email Images', callback=self.mailScreenshot),
        ]))

        self.main_layout.addWidget(self.imageLabel)
        self.main_layout.addWidget(self.outimageLabel)

    def setImage(self, imagePath):
        self.originalImagePath = imagePath
        if imagePath:
            pix = QPixmap(imagePath)
            pix = pix.scaled(500, 500, Qt.KeepAspectRatio)
            self.imageLabel.setPixmap(pix)
        else:
            print("Error: img path is none")

    def cv2_to_qimage(self,cv_img):
        # Notice the dimensions.
        height, width, bytesPerComponent = cv_img.shape

        cv_img = cv_img.astype(numpy.float32)
        cv_img *= 255  # or any coefficient
        cv_img = cv_img.astype(numpy.uint8)

        bytesPerLine = bytesPerComponent * width
        self.saveOutImage(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        if (bytesPerComponent == 4): #number of channels
            image = QImage(cv_img.data, width , height, bytesPerLine, QImage.Format_RGBA8888)
        else:
            image = QImage(cv_img.data, width, height, bytesPerLine, QImage.Format_RGB888)

        return image

    def mailScreenshot(self, withDate=True):

        self.myVisoarImageMailer = VisoarImageMailer([self.originalImagePath,self.saveImagePath] ,
                                                     self.originalImagePath, self)
        self.myVisoarImageMailer.launch()

    def readImgFromDir(self):
        if self.originalImagePath:
            img = cv2.imread(self.originalImagePath)
            # height, width, channel = img.shape
            # img = input.astype(numpy.float32)
            img = img.astype(numpy.float32) / 255.0
            return img
        else:
            QMessageBox.information(self,
                                    "Error: Load image",
                                    "Please Load an image before applying filter ")
            return None
    def saveOutImage(self,out,withDate=True):
        if withDate:
            now = datetime.now()
            date_time = now.strftime("_%Y%m%d_%H%M%S")
        else:
            date_time = ''

        dir, filestr = os.path.split(self.originalImagePath)
        filesplit = os.path.splitext(filestr)
        namestr = filesplit[0]
        ext = filesplit[1]
        self.saveImagePath = os.path.join(dir,namestr+self.MODE+date_time+ext)
        #cv2.imshow('out before saving', out)
        cv2.imwrite(self.saveImagePath, out)

    def setOutImage(self, out):

        self.outQImg = self.cv2_to_qimage(out)
        pix = QPixmap.fromImage(self.outQImg)
        pix = pix.scaled(500, 500, Qt.KeepAspectRatio)
        self.outimageLabel.setPixmap(pix)

    def applyMapping(self, gray):
        # Note: both these mappings discard the negative values of the mapping
        cdict = [(0.56, 0.02, 0.02), (0.74, 0.34, 0.04), (0.94, 0.65, 0.27), (0.2, 0.4, 0.0), (0.2, 0.4, 0.0), ]
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)
        cmap1 = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", cdict)

        colors = ["red", "darkorange", "gold", "lawngreen", "green", "green"]
        nodes = [0.0, 0.3, 0.5, 0.8, 0.9, 1.0]
        cmap2 = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, colors)))

        # https://up42.com/blog/tech/5-things-to-know-about-ndvi

        colors = ["red", "gold", "lawngreen", "green", "green"]
        nodes = [0.0, 0.1, 0.333, 0.666, 1.0]
        cmap3 = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, colors)))

        colors = ["red", "red", "gold", "lawngreen", "green", "green"]
        nodes = [0.0, 0.5, .55, 0.65, 0.8, 1.0]
        cmap4 = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, colors)))

        out = cmap4(gray)
        return out

    def applyMappingTGI(self, gray):

        colors = ["red", "red", "gold", "lawngreen", "green", "green"]
        nodes = [0.0, 0.25, .43, 0.63, 0.83, 1.0]
        cmap4 = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, colors)))

        out = cmap4(gray)
        return out


    def computeNDVIAgrocam(self):
        self.MODE = 'NDVI'

        img = self.readImgFromDir( )


        if img is not None:
            NIR = img[:, :, 2]
            green = img[:, :, 1]
            blue = img[:, :, 0]

            NDVI_u = (NIR - blue)
            NDVI_d = (NIR + blue)
            NDVI_d[NDVI_d == 0] = 0.01
            NDVI = NDVI_u / NDVI_d
            NDVI = (1+NDVI)/2

            #NDVI = cv2.normalize(NDVI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]
            #gray = numpy.float32(NDVI)
            gray = NDVI

            out = self.applyMapping(gray)
            self.setOutImage(out)
            self.update()

    def computeTGIOld(self):
        self.MODE = 'TGI'

            #Triangular greenness index
        img = self.readImgFromDir( )

        if img is not None:
            red = img[:, :, 2]
            green = img[:, :, 1]
            blue = img[:, :, 0]

            #cv2.imshow('red', red)
            #cv2.imshow('green', green)
            #cv2.imshow('blue', blue)
            scaleRed = (0.39 * red)
            scaleBlue = (.61 * blue)
            TGI = green - scaleRed - scaleBlue
            TGI = (TGI + 1.0) / 2.0
            #TGI = (TGI *.5)
            #0.5 * (((λR - λB) * (R - G)) - ((λR - λG) * (R - B)))
            TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]
            # gray = numpy.float32(NDVI)
            gray = TGI
            #cv2.imshow('Gray TGI', gray)
            print(numpy.amax(gray))
            print(numpy.amin(gray))
            out = self.applyMapping(gray)
            self.setOutImage(out)
            self.update()

    def computeTGI(self):
        self.MODE = 'TGI'
        #https://github.com/bethanysprag/TriangularGreenness/blob/master/tgi.py
        # Triangular greenness index
        img = self.readImgFromDir()
        if img is not None:
            red = img[:, :, 2]
            green = img[:, :, 1]
            blue = img[:, :, 0]

            TGI = (-1) * 0.5 * ((200 * (red - green)) - (100 * (red - blue)))
            gray =  cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
            # cv2.imshow('Gray TGI', gray)
            print(numpy.amax(gray))
            print(numpy.amin(gray))
            out = self.applyMappingTGI(gray)
            self.setOutImage(out)
            self.update()

    def compute(self, imgPath):
        self.setImage(imgPath)

    # createButton
    def createButton(self, text, callback=None):
        ret = QPushButton(text)
        if callback is not None:
            ret.clicked.connect(callback)
        return ret
    # hlayout
    def hlayout(self, items):
        ret = QHBoxLayout()
        for item in items:
            try:
                ret.addWidget(item)
            except:
                ret.addLayout(item)
        return ret

    # vlayout
    def vlayout(self, items):
        ret = QVBoxLayout()
        for item in items:
            if item.widget() is not None:
                ret.addWidget(item)
            else:
                ret.addLayout(item)
        return ret

    # clearLayout
    def clearLayout(self, layout):
        if layout is None: return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clearLayout(item.layout())


class QCustomQWidget ( QWidget):
    def __init__ (self, parent = None):
        super(QCustomQWidget, self).__init__(parent)
        self.name = None
        self.textQVBoxLayout = QVBoxLayout()
        self.textUpQLabel    =  QLabel()
        #self.textDownQLabel  =  QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        #self.textQVBoxLayout.addWidget(self.textDownQLabel)
        self.allQHBoxLayout  =  QHBoxLayout()
        #self.iconQLabel= QPushButton('', self)
        #self.iconQLabel.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        self.iconQLabel      =  QLabel()
        self.iconQLabel.setVisible(False)
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)
        # setStyleSheet
        self.textUpQLabel.setStyleSheet('''
           background-color: white;
    	   color: #045951;
    	   padding: 10px 10px 10px 10px;
    	   margin: 5px 5px 5px 5px;
        ''')
        # self.textDownQLabel.setStyleSheet('''
        #     color: rgb(255, 0, 0);
        # ''')
        self.iconQLabel.setStyleSheet("margin:10px; padding:10px;""")
        self.iconQLabel.setFixedSize(NAME_BUTTON_WIDTH, NAME_BUTTON_WIDTH)

    def setTextUp (self, text):
        self.name = text
        self.textUpQLabel.setText(text)

    #def setTextDown (self, text):
    #    self.textDownQLabel.setText(text)

    def setIcon (self, imagePath):
        if imagePath:
            pix = QPixmap(imagePath)
            pix = pix.scaled(NAME_BUTTON_WIDTH, NAME_BUTTON_WIDTH, Qt.KeepAspectRatio)
            self.iconQLabel.setPixmap(pix)
        else:
            print("Error: img path is none")

    def getName(self):
        return self.name


class VisoarQuickNDVIWidget(QWidget):

    # constructor
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        self.tmpImageSavePath = ''
        self.skip = 0
        # global log
        # if log is None:
        #     log = LogFile()
        #     log.print("Got arguments", sys.argv)

        self.setWindowTitle("Sync files")
        self.resize(600, 200)
        self.sensors = {}
        self.main_layout = QHBoxLayout()
        self.list_layout = QVBoxLayout()
        self.ndviViewWidget = ViSOARNDVIImageWidget()
        self.main_layout.addLayout(self.list_layout)
        self.main_layout.addWidget(self.ndviViewWidget)
        self.setLayout(self.main_layout)
        self.refreshGui()

    def refreshGui(self):
        self.buttons = []

        self.clearLayout(self.list_layout)
        self.listWidget = QListWidget()
        self.listWidget.itemClicked.connect(self.onClicked)
        self.listWidget.currentItemChanged.connect(self.onClicked)
        self.listWidget.setStyleSheet('''
                             background-color: white;
                      	   color: white;
                      	   margin:10px; padding:10px;
                          ''')

        self.curDir = QLineEdit()
        self.curDir.setText('')
        #self.curDir.setEnabled(False)

        self.sl = QSlider(Qt.Horizontal)
        self.sl.setMinimum(0)
        self.sl.setMaximum(10)
        self.sl.setValue(5)
        self.sl.setTickPosition(QSlider.TicksBelow)
        self.sl.setTickInterval(1)
        self.sl.valueChanged.connect(lambda: self.setImgListDir(changeDir = False))
        # self.skipLine = QLineEdit()
        # self.skipLine.setText('5')
        # self.skipLine.setEnabled(False)

        self.buttonAddImagesSource = QPushButton('setDirectory', self)
        self.buttonAddImagesSource.resize(180, 40)
        self.buttonAddImagesSource.clicked.connect(lambda: self.setImgListDir(changeDir=True))
        self.buttonAddImagesSource.setStyleSheet(GREEN_PUSH_BUTTON)
        self.buttonAddImagesSource.setToolTip('Specify directory of image for stitching')
        self.list_layout.addLayout(self.hlayout([
            QLabel('Directory'),
            self.curDir,
            self.buttonAddImagesSource
        ]))
        self.list_layout.addLayout(self.hlayout([
            QLabel('Skip Images'),
            self.sl,
        ]))

        self.list_layout.addWidget(self.listWidget)

        #self.setImgListDir()

    def onClicked(self, item):
        #QMessageBox.information(self, "Info", item.text())
        if item:
            self.ndviViewWidget.compute(item.text())

    def setImgListDir(self, changeDir = True):
        self.listWidget.clear()
        if  changeDir:  #Allow user to change directory
            dir =  str(QFileDialog.getExistingDirectory(self, "Select Directory containing Images"))
            self.curDir.setText(dir)
        else:  #Not make Amy enter directory.... for testing
            dir = self.curDir.text()
        import os
        files = []
        extensions = ('.jpeg', '.tif', '.JPG','.TIF', '.PNG','.png')
        imgNum = 0
        skipN  = int(self.sl.value())
        dirList = os.listdir(dir)
        if (skipN>0):  #skip every skipN items in array
            dirList = dirList[0::skipN]
        for file in dirList:
            if file.endswith(extensions ):
                    files.append(os.path.join(dir, file))

        for x in files:
            # Create QCustomQWidget
            myQCustomQWidget = QCustomQWidget()
            myQCustomQWidget.setTextUp(x)
            #myQCustomQWidget.setTextDown(x)
            if False:
                myQCustomQWidget.setIcon(x)
            # Create QListWidgetItem
            myQListWidgetItem =  QListWidgetItem(self.listWidget)
            myQListWidgetItem.setText(x)

            # Set size hint
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            # Add QListWidgetItem into QListWidget
            self.listWidget.addItem(myQListWidgetItem)
            self.listWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)

            #
            # item =  QListWidgetItem()
            # icon =  QIcon()
            # icon.addPixmap( QPixmap( x),  QIcon.Normal,  QIcon.Off)
            # item.setIcon(icon)
            # self.listWidget.addItem(item)
        self.update()


    # separator
    def separator(self):
        line = QLabel(" ")
        # line.setFrameShape(QFrame.HLine)
        # line.setFrameShadow(QFrame.Sunken)
        return line

    # hlayout
    def hlayout(self, items):
        ret = QHBoxLayout()
        for item in items:
            try:
                ret.addWidget(item)
            except:
                ret.addLayout(item)
        return ret

    # vlayout
    def vlayout(self, items):
        ret = QVBoxLayout()
        for item in items:
            if item.widget() is not None:
                ret.addWidget(item)
            else:
                ret.addLayout(item)
        return ret

    # clearLayout
    def clearLayout(self, layout):
        if layout is None: return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clearLayout(item.layout())
