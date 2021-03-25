
import cv2
from glob import glob
import os

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



class MatchRGBNDVIWidget(QWidget):
    def __init__(self, parent,RGB_DIR="",NDVI_DIR="",CHECK_LAST_N_FILES = 5 ):
        super(QWidget, self).__init__(parent)
        self.parent = parent
        # read images

        self.RGB_DIR = RGB_DIR
        self.NDVI_DIR = NDVI_DIR
        #RGB_DIR = '/Volumes/ViSUSAg/RGB_Agrocam/108_10.14.20/'
        #NDVI_DIR = '/Volumes/ViSUSAg/NDVI_Agrocam/108 10.14.20 NDVI/'
        self.CHECK_LAST_N_FILES = CHECK_LAST_N_FILES
        self.BUTTON_SIZE_SM = 200
        self.startFromTop = True
        if (self.RGB_DIR != "" and self.NDVI_DIR!="" ):
            self.init()


    def getLastFileInFolder (self,folder):


        fpath, ffilename = os.path.split(folder)
        accepted_extensions = ["jpg", "png", "JPG", "PNG", "JPEG", 'jpeg','tif','TIF']
        files = [fn for fn in os.listdir(folder) if fn.split(".")[-1] in accepted_extensions]
        files.sort()
        if self.startFromTop:
            files.reverse()

        # files_path = os.path.join(folder, '*')
        # files = sorted(
        #     glob.iglob(files_path), key=os.path.getctime, reverse=self.startFromTop)
        return os.path.join(fpath,files[0])

    def getNFileList(self, folder):

        ffiles = []
        for fext in ("*.jpg", "*.png", "*.JPG", "*.PNG", "*.JPEG", "*.jpeg","*.tif","*.TIF"):
            print('Will glob: {0}'.format(os.path.join(folder, fext)))
            ffiles.extend(glob.glob(os.path.join(folder, fext)))

        # ffiles = glob.glob(os.path.join(folder,'*.gif'))
        # ffiles.extend(glob.glob(os.path.join(folder,'*.png')))
        # ffiles.extend(glob.glob(os.path.join(folder,'*.jpg')))

        if self.startFromTop:
            ffiles.reverse()

        # files_path = os.path.join(folder, '*')
        # files = sorted(
        #     glob.iglob(files_path), key=os.path.getctime, reverse=self.startFromTop)
        filesToCheck = []
        for f in range(self.CHECK_LAST_N_FILES):
            filesToCheck.append(ffiles[f])
        return filesToCheck

    def getFileList(self, folder):

        ffiles = []
        for fext in ("*.jpg", "*.png", "*.JPG", "*.PNG", "*.JPEG", "*.jpeg", "*.tif", "*.TIF"):
            ffiles.extend(glob.glob(os.path.join(folder, fext)))
        if self.startFromTop:
            ffiles.reverse()

        # files_path = os.path.join(folder, '*')
        # files = sorted(
        #     glob.iglob(files_path), key=os.path.getctime, reverse=self.startFromTop)
        return ffiles

    def getGreenImageIcon(self,file):
        img1 = cv2.imread(file)
        rgb_b, rgb_g, rgb_r = cv2.split(img1)
        img1_g = cv2.merge((rgb_g,rgb_g,rgb_g))
        #img1_g = cv2.cvtColor(img1_g, cv2.COLOR_BGR2GRAY)
        # scale_percent = self.BUTTON_SIZE_SM/int(img1.shape[1]) # percent of original size
        # width = int(img1_g.shape[1] * scale_percent / 100)
        # height = int(img1_g.shape[0] * scale_percent / 100)
        # dim = (width, height)
        # # resize image
        # img1 = cv2.resize(img1_g, dim, interpolation=cv2.INTER_AREA)

        qimage =  QImage(img1_g.data,img1_g.shape[1], img1_g.shape[0],
                                   QImage.Format_RGB888).rgbSwapped()
 
        icon = QIcon( QPixmap.fromImage(qimage))
        return icon

    def switchStartFromTop(self):
        self.startFromTop =  self.startSwitch.checkState()
        self.init()

    def init(self):
        ndviImgs = self.getNFileList(self.NDVI_DIR)
        lastFileRGB = self.getLastFileInFolder(self.RGB_DIR)


        #ask user to pick best match between 1 RGB img and N FILES
        question = 'Pick the best image in the row below\n (with the most overlap)\n that matches this image:'

        class Buttons:
            pass

        self.buttons = Buttons

        # self.toolbar
        self.rgblayout = QHBoxLayout()
        self.ndvilayout = QHBoxLayout()
        self.layout = QVBoxLayout()

        self.startSwitch = QCheckBox("Start from Top")
        self.startSwitch.stateChanged.connect(lambda: self.switchStartFromTop)
        self.startSwitch.setChecked(self.startFromTop)
        self.startSwitch.setStyleSheet(QCHECKBOX_LOOK_AND_FEEL)

        # self.copySourceBox_switch = QCheckBox("Copy Source")
        # self.copySourceBox_switch.stateChanged.connect(lambda: self.parent.copySourceBBOXFlip(self.copySourceBox_switch))
        # self.copySourceBox_switch.setChecked(self.parent.copySourceBool)
        # self.copySourceBox_switch.setStyleSheet(QCHECKBOX_LOOK_AND_FEEL)

        self.buttons.myQuestion = QLabel(question)

        self.buttons.RGBImg = QPushButton('Test RGB image', self)
        self.buttons.RGBImg.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.RGBImg.setIcon(self.getGreenImageIcon(lastFileRGB))
        self.buttons.RGBImg.setIconSize(QSize( self.BUTTON_SIZE_SM, self.BUTTON_SIZE_SM))
        self.buttons.RGBImg.resize(self.BUTTON_SIZE_SM, self.BUTTON_SIZE_SM)
        self.buttons.RGBImg.clicked.connect(self.clickRGB)
        self.buttons.RGBImg.setToolTip('Try to find match to this image')
        self.rgblayout.addWidget(self.buttons.myQuestion)
        self.rgblayout.addWidget(self.buttons.RGBImg)
        self.rgblayout.addStretch(True)
        i = 0
        for x in ndviImgs:
            NDVIImg = QPushButton('NDVIImg', self)
            NDVIImg.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
            ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
            NDVIImg.setIcon(self.getGreenImageIcon(x))
            NDVIImg.setIconSize(QSize( self.BUTTON_SIZE_SM, self.BUTTON_SIZE_SM))
            NDVIImg.resize(self.BUTTON_SIZE_SM, self.BUTTON_SIZE_SM)
            NDVIImg.clicked.connect(lambda: self.clickNDVI(i,x))
            NDVIImg.setToolTip('Click if this is the best fit for the image above')
            self.ndvilayout.addWidget(NDVIImg)
            i = i+1

        self.layout.addLayout(self.rgblayout)
        self.layout.addLayout(self.ndvilayout)

        #maxKey, compareList,lastFileRGB,NDVI_bestFit = self.compareLastImagesInDir()
        self.setLayout( self.layout)

    def clickRGB(self):
        print("click")

    def clickNDVI(self,i,ndviFileName):
        print("click on image {0} with filename = {1}".format(i,ndviFileName))
        self.renameFilesBasedUponMatch(i,ndviFileName)
        self.parent.matchSet()

    def setRGB(self, dir):
        self.RGB_DIR = dir

    def setNDVI(self, dir):
        self.NDVI_DIR = dir

    def renameFilesBasedUponMatch(self, i, ndviFileNameStartMatch):
        NDVIfileList = self.getFileList(self.NDVI_DIR)
        RGBfileList = self.getFileList(self.RGB_DIR)

        if i>0:
            #go thru NDVIfileList and remove items until get to ndviFileName
            ndviFile = NDVIfileList[0]
            for ndviFile in NDVIfileList:
                if ndviFile == ndviFileNameStartMatch:
                    print('found '+ ndviFile)
                    break
                else:
                    NDVIfileList.remove(ndviFile)
                    print('remove: ndviFile')

        self.parent.renameFilesRGBNDVI(self.RGB_DIR,self.NDVI_DIR)

    def renameFilesRGBNDVI(self, RGBDIR, NDVDIR):
        NDVIfileList = self.getFileList(NDVDIR)
        RGBfileList = self.getFileList(RGBDIR)

        # rename files
        # this list is from the end.. we need to number them from [max... 1]
        num = 0 #max(len(NDVIfileList), len(RGBfileList))
        for ndviFile, rgbFile in zip(NDVIfileList, RGBfileList):
            RGBPath, rgb_filename = os.path.split(rgbFile)
            NDVIPath, nvdi_filename = os.path.split(ndviFile)
            RGBName, RGBExtension = os.path.splitext(rgb_filename)
            NDVIName, NDVIExtension = os.path.splitext(nvdi_filename)
            if "visussource" not in rgb_filename:
                newName = 'visussource'
                newRGBName = os.path.join(RGBPath, newName + '_' + str(num).zfill(4) + RGBExtension)
                newNDVIName = os.path.join(NDVIPath, newName + '_' + str(num).zfill(4) + NDVIExtension)
                #os.rename(ndviFile, newNDVIName)
                #os.rename(rgbFile, newRGBName)
                print(newNDVIName)
                print(newRGBName)
                num = num + 1
        print('done with rename')