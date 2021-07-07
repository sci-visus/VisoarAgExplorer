

from VisoarSettings import *

from PyQt5.QtWebEngineWidgets         import QWebEngineView

from OpenVisus                        import *
from OpenVisus.gui                    import *

from PyQt5.QtGui 					  import QFont,QPainter,QPen
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFileDialog

from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem

from gradient import *
import pyqtgraph

# sys.path.insert(0, './MAPIR_CameraController')
# from   MAPIR_Processing_dockwidget  import *

sys.path.insert(0, './StandAloneMAPIR_CameraController')
from   MAPIR_Processing  import *

class ViSOARMapIRCalibrationWidget(QWidget):
    def __init__(self, parent  ):
        super(QWidget, self).__init__(parent)
        self.parent = parent

        #self.MODE = MODE
        self.setGeometry(30, 30, 600, 400)

        self.mapIRCalibrationWidget = MAPIR_ProcessingCLI(parent=self,args='wait')
        self.createUI()

    def createUI(self):
        self.layout = QVBoxLayout()
        self.layoutVTopCameraConfig = QVBoxLayout()
        # self.layout1 = QVBoxLayout()
        # self.layout2 = QVBoxLayout()
        # self.layout3 = QVBoxLayout()
        self.layoutAllCameraLayout = QHBoxLayout()
        self.layoutCameraParams = QHBoxLayout()

        # self.labelCameraModel = QLabel("Calibration Camera Model", self)
        # self.comboboxCameraModel = QComboBox(self)
        # self.comboboxCameraModel.addItem("Survey3")
        # self.comboboxCameraModel.setStyleSheet(MY_COMBOX)
        # #self.comboboxCameraModel.currentIndexChanged.connect(self.inputModeChangedNewTab)
        # self.comboboxCameraModel.setFixedSize(100, 40)
        # self.comboboxCameraModel.resize(100, 40)
        # self.comboboxCameraModel.setFixedWidth(100)
        # self.comboboxCameraModel.setFixedHeight(40)
        # self.comboboxCameraModel.setCurrentIndex(0)
        #
        # self.labelCalibrationFilter = QLabel("Calibration Filter", self)
        # self.comboboxCalibrationFilter = QComboBox(self)
        # self.comboboxCalibrationFilter.addItem("OCN")
        # self.comboboxCalibrationFilter.setStyleSheet(MY_COMBOX)
        # #self.comboboxCalibrationFilter.currentIndexChanged.connect(self.inputModeChangedNewTab)
        # self.comboboxCalibrationFilter.setFixedSize(100, 40)
        # self.comboboxCalibrationFilter.resize(100, 40)
        # self.comboboxCalibrationFilter.setFixedWidth(100)
        # self.comboboxCalibrationFilter.setFixedHeight(40)
        # self.comboboxCalibrationFilter.setCurrentIndex(0)
        #
        # self.labelCalibrationLens = QLabel("Calibration Lens", self)
        # self.comboboxCalibrationLens = QComboBox(self)
        # self.comboboxCalibrationLens.addItem("3.37mm (Survey3W)")
        # self.comboboxCalibrationLens.setStyleSheet(MY_COMBOX)
        # #self.comboboxCalibrationLens.currentIndexChanged.connect(self.inputModeChangedNewTab)
        # self.comboboxCalibrationLens.setFixedSize(100, 40)
        # self.comboboxCalibrationLens.resize(100, 40)
        # self.comboboxCalibrationLens.setFixedWidth(100)
        # self.comboboxCalibrationLens.setFixedHeight(40)
        # self.comboboxCalibrationLens.setCurrentIndex(0)


        # self.layout1.addWidget(self.labelCameraModel, Qt.AlignLeft)
        # self.layout1.addWidget(self.comboboxCameraModel, Qt.AlignLeft)
        # self.layout2.addWidget(self.labelCalibrationFilter, Qt.AlignLeft)
        # self.layout2.addWidget(self.comboboxCalibrationFilter, Qt.AlignLeft)
        # self.layout3.addWidget(self.labelCalibrationLens, Qt.AlignLeft)
        # self.layout3.addWidget(self.comboboxCalibrationLens, Qt.AlignLeft)
        # self.layoutCameraParams.addLayout(self.layout1)
        # self.layoutCameraParams.addLayout(self.layout2)
        # self.layoutCameraParams.addLayout(self.layout3)

        targetlayout =  QHBoxLayout()
        self.targetLabel = QLabel("Target Source Image", self)
        self.targetLineEdit = QLineEdit(self)
        self.targetBrowseBtn = QPushButton(". . .")
        self.targetBrowseBtn.clicked.connect(self.setTargetSource)
        self.targetBrowseBtn.setStyleSheet(GREEN_PUSH_BUTTON)
        targetlayout.addWidget(self.targetLineEdit)
        targetlayout.addWidget(self.targetBrowseBtn)

        imageLocationLayout =  QHBoxLayout()
        self.imageLabel = QLabel("MapIR Images", self)
        self.imageLineEdit = QLineEdit(self)
        self.imageBrowseBtn = QPushButton(". . .")
        self.imageBrowseBtn.clicked.connect(self.setImageSource)
        self.imageBrowseBtn.setStyleSheet(GREEN_PUSH_BUTTON)
        imageLocationLayout.addWidget(self.imageLineEdit)
        imageLocationLayout.addWidget(self.imageBrowseBtn)

        self.targetLineEdit.resize(180, 40)
        self.targetLineEdit.setStyleSheet(
            "padding:10px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
        self.btnGenerate = QPushButton("Calibrate Images")
        self.btnGenerate.clicked.connect(self.genCalibration)
        self.btnGenerate.setStyleSheet(GREEN_PUSH_BUTTON)

        self.textEditLog = QTextEdit()
        self.mapIRCalibrationWidget.CalibrationLog = self.textEditLog
        self.textEditLog.ensureCursorVisible()
        self.textEditLog.setLineWrapColumnOrWidth(900)
        self.textEditLog.setLineWrapMode(QTextEdit.FixedPixelWidth)
        self.textEditLog.setFixedWidth(800)

        # self.layoutVTopCameraConfig.addLayout(self.layoutCameraParams)
        self.layoutVTopCameraConfig.addWidget(self.targetLabel, Qt.AlignLeft)
        self.layoutVTopCameraConfig.addLayout(targetlayout)
        self.layoutVTopCameraConfig.addWidget(self.imageLabel, Qt.AlignLeft)
        self.layoutVTopCameraConfig.addLayout(imageLocationLayout)
        self.layoutAllCameraLayout.addLayout(self.layoutVTopCameraConfig)
        self.layoutAllCameraLayout.addWidget(self.textEditLog, Qt.AlignRight)

        self.layout.addLayout(self.layoutAllCameraLayout)
        self.layout.addWidget(self.btnGenerate, Qt.AlignLeft)
        #self.layout.addWidget(self.textEditLog, Qt.AlignLeft)

        self.setLayout(self.layout)

    def resetUIFill(self):
        self.targetLineEdit.setText('')
        self.targetLineEdit.setText('')
        self.textEditLog.setText('')
        self.on_hide()

    def on_show(self):
        print('show')
        self.show()
        self.update()

    def on_hide(self):
        print('hide')
        self.hide()
        self.update()

    def preProcessMapIRImagesWithTarget(self):
        # PreProcessing
        if (self.parent.parent.tabAskSensor.comboBoxNewTab.currentText() == 'MAPIR and RGB') or (
                self.parent.parent.tabAskSensor.comboBoxNewTab.currentText() == 'MapIR only (OCNIR)'):
            print(
                self.parent.mapirCalibrationWidget.mapIRCalibrationWidget.CalibrationInFolder)  # =  self.tabAskSource.curDir2
            outdir = self.parent.mapirCalibrationWidget.calibrateMapIRImages()
            if (outdir is None):
                import glob
                listing = glob.glob(os.path.join(self.parent.parent.projectInfo.srcDir, 'Calibrated_*'))
                self.parent.parent.projectInfo.srcDir = os.path.join(self.parent.parent.projectInfo.srcDir, listing[-1])
                print('New Directory for Src Images: {0} '.format(self.parent.parent.projectInfo.srcDir))
                self.parent.parent.projectInfo.cache_dir = os.path.join(self.parent.parent.projectInfo.srcDir, 'VisusSlamFiles')
            else:
                self.parent.parent.projectInfo.srcDir = outdir

    def setImageSource(self):
        dir= str(QFileDialog.getExistingDirectory(self, "Select MapIR Image Directory" ))
        self.imageLineEdit.setText(dir)
        return dir

    def setTargetSource(self):
        filename, filter = QFileDialog.getOpenFileName(self, "Select MapIR Target Image", "","Images (*.png *.tif *.jpg *.jpeg)")
        self.targetLineEdit.setText(filename)
        return filename

    def calibrateMapIRImages(self):
        outdir = self.mapIRCalibrationWidget.on_CalibrateButton_released()
        return outdir

    def genCalibration(self):
        # print('calibration_camera_model')
        # print(calibration_camera_model)  # combobox  'Survey3'
        #
        # print('calibration_QR_file')
        # print(calibration_QR_file)  # qlineedit  path to file
        #
        # print('calibration_filter')
        # print(calibration_filter)  # combobox  'OCN'
        #
        # print('calibration_lens')
        # print(calibration_lens)  # Combbox   '3.37mm (Survey3W)'
        #
        # print('qrcoeffs')
        # print(qrcoeffs)  # []
        #
        # print('qr_coeffs_index')
        # print(qr_coeffs_index)  # 1

        self.CalibrationCameraModel = 'Survey3' #self.comboboxCameraModel
        self.CalibrationQRFile = self.targetLineEdit.text()
        self.CalibrationFilter = 'OCN' #self.comboboxCalibrationFilter
        self.CalibrationLens = '3.37mm (Survey3W)' #self.comboboxCalibrationLens
        self.qrcoeffs = []
        self.qr_coeffs_index = 1
        args = {}
        args['target'] = self.CalibrationQRFile
        args['path'] =  self.imageLineEdit.text()
        args['calibration_camera_model']='Survey3'
        args['calibration_QR_file']='Survey3'
        args['calibration_filter']='OCN'
        args['calibration_lens']='3.37mm (Survey3W)'
        self.mapIRCalibrationWidget.processArgs(args)

        # self.mapIRCalibrationWidget.generate_calibration(self.CalibrationCameraModel, self.CalibrationQRFile, self.CalibrationFilter,
        #                           self.CalibrationLens, self.qrcoeffs, qr_coeffs_index=1)
        self.qr_coeffs_index, self.qrcoeffs = self.mapIRCalibrationWidget.generate_calibration(  )

        print('Generate returns')
        # print(self.qrcoeffs)
        # self.mapIRCalibrationWidget.CalibrationCameraModel = self.CalibrationCameraModel
        # self.mapIRCalibrationWidget.CalibrationQRFile = self.CalibrationQRFile
        # self.mapIRCalibrationWidget.CalibrationFilter = self.CalibrationFilter
        # self.mapIRCalibrationWidget.CalibrationLens = self.CalibrationLens
        # self.mapIRCalibrationWidget.qrcoeffs = self.qrcoeffs
        # self.mapIRCalibrationWidget.qr_coeffs_index = self.qr_coeffs_index
        # self.mapIRCalibrationWidget.CalibrationInFolder = self.imageLineEdit.text()

        self.preProcessMapIRImagesWithTarget()
        self.parent.curDir2.setText(self.mapIRCalibrationWidget.CalibrationInFolder)
        #self.close()
        self.parent.curDir.setHidden(False)
        self.parent.curDir2.setHidden(False)
        self.parent.buttonAddImagesSource.setHidden(False)

