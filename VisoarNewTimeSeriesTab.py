
from VisoarSettings             import *

#from PyQt5.QtWebEngineWidgets         import QWebEngineView

# from OpenVisus                        import *
# from OpenVisus.gui                    import *

from PyQt5.QtGui 					  import QFont
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFileDialog

from PyQt5.QtWidgets                  import QTableWidget,QTableWidgetItem



class VisoarNewTimeSeriesTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.GRID_SPACING = 5
        self.parent = parent
        self.DEBUG = True
        self.setStyleSheet(LOOK_AND_FEEL)

        self.listOfMidxFiles = []
        self.saveDir = ''

        class Buttons:
            pass

        self.layout = QVBoxLayout()
        self.layout.setSpacing(self.GRID_SPACING)

        self.buttons = Buttons
        self.nameLayout = QHBoxLayout()
        self.buttons.projNameLabel = QLabel('New Project Name:')
        self.buttons.projNametextbox = QLineEdit(self)
        self.buttons.projNametextbox.setStyleSheet(
            "min-height:30; min-width:180; padding:0px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
        self.nameLayout.addWidget(self.buttons.projNameLabel, alignment=Qt.AlignLeft)
        self.nameLayout.addWidget(self.buttons.projNametextbox, alignment=Qt.AlignLeft)
        self.nameLayout.addStretch(True)
        self.layout.addLayout(self.nameLayout )

        self.saveLayout = QHBoxLayout()
        self.buttons.saveDirLabel = QLabel('Save Time Series Directory: ')
        self.buttons.saveDirNameLabel = QLabel('')

        self.buttons.btnSetSaveDir = QPushButton(". . .")
        self.buttons.btnSetSaveDir.clicked.connect(self.setSaveDirectory)
        self.buttons.btnSetSaveDir.setStyleSheet(GREEN_PUSH_BUTTON)
        self.saveLayout.addWidget(self.buttons.saveDirLabel, alignment=Qt.AlignLeft)
        self.saveLayout.addWidget(self.buttons.saveDirNameLabel, alignment=Qt.AlignLeft)
        self.saveLayout.addWidget(self.buttons.btnSetSaveDir, alignment=Qt.AlignLeft)
        self.saveLayout.addStretch(True)
        self.layout.addLayout(self.saveLayout)

        self.buttons.buttonStitching = QPushButton('Add MIDX file', self)
        self.buttons.buttonStitching.resize(180, 40)
        self.buttons.buttonStitching.clicked.connect(self.addMIDXFiles)
        self.buttons.buttonStitching.setStyleSheet(GREEN_PUSH_BUTTON)
        self.layout.addWidget(self.buttons.buttonStitching, alignment=Qt.AlignLeft)

        self.buttons.listLabel = QLabel('List of MIDX files:')
        self.layout.addWidget(self.buttons.listLabel, alignment=Qt.AlignLeft)

        #List View of Files
        self.containerScroll = QScrollArea(self)
        self.containerScroll.setWidgetResizable(True)
        self.containerScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.containerScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.container = QWidget(self)
        self.sublayoutGrid = QGridLayout(self.container)
        self.sublayoutGrid.setSpacing(GRID_SPACING)
        self.sublayoutGrid.setHorizontalSpacing(0)

        self.layout.addWidget(self.containerScroll)
        #self.layout.addWidget(self.parent.logo)  # ,row,0)

        self.buttons.home = QPushButton('', self)
        self.buttons.home.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.home.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'home.png')))
        self.buttons.home.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.home.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        #self.layout.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        self.buttons.home.clicked.connect(self.parent.goHome)

        self.buttons.btnCreateTimeSeries = QPushButton("Create Time Series")
        self.buttons.btnCreateTimeSeries.clicked.connect(self.createTimeSeries)
        self.buttons.btnCreateTimeSeries.setStyleSheet(GREEN_PUSH_BUTTON)
        #self.layout.addWidget(self.buttons.btnCreateTimeSeries, alignment=Qt.AlignRight)

        self.sublayoutLastRow = QHBoxLayout()
        self.sublayoutLastRow.addWidget(self.buttons.home, alignment=Qt.AlignRight)
        self.sublayoutLastRow.addStretch(True)
        self.sublayoutLastRow.addWidget(self.buttons.btnCreateTimeSeries, alignment=Qt.AlignLeft)
        self.layout.addLayout(self.sublayoutLastRow)


        self.containerScroll.setWidget(self.container)
        self.setLayout(self.layout)


    def setSaveDirectory(self):
        self.saveDir = str(
            QFileDialog.getExistingDirectory(self, "Select Directory to save New files to"))
        self.buttons.saveDirNameLabel.setText(self.saveDir)

    def addMIDXFiles(self):
        filename, filter = QFileDialog.getOpenFileName(self, "Select MIDX File", "", "MIDX (*.midx)")
        #vll = VisoarLayer(filename)
        #self.visoarLayerList.append(vll)
        self.listOfMidxFiles.append(filename)
        print(self.listOfMidxFiles)
        self.updateListMidxFiles()

    def updateListMidxFiles(self):
        clearLayout(self.sublayoutGrid)
        COL_NAME = 0
        COL_MODIFY = 1
        editIconPath = os.path.join(self.parent.app_dir, 'icons', 'Edit_green.png')
        delIconPath = os.path.join(self.parent.app_dir, 'icons', 'garbage_green.png')

        ROW = 0
        headerLabelName = QLabel('Project Name')
        headerLabelName.setStyleSheet(
            """padding:0px; margin:0px; background-color: #045951;  color:#ffffff""")
        headerLabelModify = QLabel('Modify')
        headerLabelModify.setStyleSheet(
            """padding:0px; margin:0px;background-color: #045951;  color:#ffffff""")
        h = V_BUTTON_SIZE_SM
        headerLabelName.setFixedHeight(h)
        headerLabelModify.setFixedHeight(h)
        headerLabelName.setMinimumSize(V_LIST_LABLES, h)
        headerLabelModify.setMinimumSize(V_LIST_LABLES, h)
        self.sublayoutGrid.addWidget(headerLabelName, ROW, COL_NAME)
        self.sublayoutGrid.addWidget(headerLabelModify, ROW, COL_MODIFY)

        for name in self.listOfMidxFiles:
            ROW =  ROW+1
            print(name)

            widgetName  = QWidget()
            nameLabel = QToolButton(widgetName)
            nameLabel.setText(name)
            widgetEdit = QWidget()
            widgetDelete = QWidget()
            widgetName.setStyleSheet(
                """border-radius:10px; padding:10px; margin: 0px; background-color: #eeeeee; QToolButton {background-color: #eeeeee; border-style: outset; border-width: 0px;color:#045951}""");
            widgetEdit.setStyleSheet(
                """background-color:none; QPushButton {background-color: none; border-style: outset; border-width: 0px;color:#045951}""");
            widgetDelete.setStyleSheet(
                """background-color: none; QPushButton {background-color: none; border-style: outset; border-width: 0px;color:#045951}""");

            widgetEdit.setMinimumSize(h, h)
            widgetDelete.setMinimumSize(h,h)
            widgetEdit.setStyleSheet(
                """background-color: none;  color:#ffffff""")
            widgetDelete.setStyleSheet(            """background-color: none;  color:#ffffff""")
            editXMLButton = QPushButton(widgetEdit)
            editXMLButton.setIcon(QIcon(editIconPath))
            btnCallback = partial(self.editName, name)
            editXMLButton.clicked.connect(btnCallback)

            deleteXMLButton = QPushButton(widgetDelete)
            deleteXMLButton.setIcon(QIcon(delIconPath))
            btnCallback = partial(self.deleteName, name)
            deleteXMLButton.clicked.connect(btnCallback)

            editXMLButton.setStyleSheet(CLEARBACKGROUND_PUSH_BUTTON)
            editXMLButton.resize(h, h)
            editXMLButton.setFixedSize(h, h )
            editXMLButton.setIconSize(QSize(h, h))

            deleteXMLButton.setStyleSheet(CLEARBACKGROUND_PUSH_BUTTON)
            deleteXMLButton.resize(h, h)
            deleteXMLButton.setFixedSize(h, h  )
            deleteXMLButton.setIconSize(QSize(h, h))

            widgetDelete.setFixedSize(h, h  )
            widgetEdit.setFixedSize(h, h )
            widgetName.setFixedHeight(h)
            modifyLayout = QHBoxLayout()
            modifyLayout.addWidget(widgetDelete )
            modifyLayout.addWidget(widgetEdit )

            self.sublayoutGrid.addWidget(widgetName, ROW, COL_NAME  )
            self.sublayoutGrid.addLayout(modifyLayout, ROW, COL_MODIFY )

    def editName(self, Name):
        self.listOfMidxFiles.remove(Name)
        self.addMIDXFiles()


    def deleteName(self, Name):
        self.listOfMidxFiles.remove(Name)
        self.updateListMidxFiles()




    def createTimeSeries(self):
        if len(self.listOfMidxFiles)> 1 and self.saveDir :

            #create file
            #visus.midx
            dataset = ET.Element('dataset',
                          {'name': 'visus',
                           'typename': 'IdxMultipleDataset'
                           })


            field = ET.SubElement(dataset, 'field',
                                  {'name': 'voronoi',
                                   })
            code = ET.SubElement(field, 'code' ).text = 'output=voronoi()'

            googlemidx = ET.SubElement(dataset, 'dataset',
                                  {'name': 'google',
                                   'typename': 'GoogleMapsDataset',
                                   'tiles': 'http://mt1.google.com/vt/lyrs=s',
                                   'physic_box': '0.0 1.0 0.0 1.0' })
            i = 0
            for midx in self.listOfMidxFiles:
                i = i+1
                dir, namestr, ext = getNameFromMIDX(midx)
                amidx = ET.SubElement(dataset, 'dataset',
                                      {'name': namestr,
                                       'url': midx,
                                       })

            # Add entry in load page
            self.parent.projectInfo.projName = self.buttons.projNametextbox.text()

            # make dir Name
            if not os.path.exists(os.path.join(self.saveDir, self.parent.projectInfo.projName)):
                os.makedirs(os.path.join(self.saveDir, self.parent.projectInfo.projName))
            # make dir VisusSlamFiles
            if not os.path.exists(os.path.join(self.saveDir, self.parent.projectInfo.projName, 'VisusSlamFiles')):
                os.makedirs(os.path.join(self.saveDir, self.parent.projectInfo.projName, 'VisusSlamFiles'))
            ET.ElementTree(dataset).write(os.path.join(self.saveDir,self.parent.projectInfo.projName, 'VisusSlamFiles','visus.midx'))


            self.parent.projectInfo.projDir = os.path.join(self.saveDir,self.parent.projectInfo.projName)
            self.parent.visoarUserLibraryData.createProject(self.parent.projectInfo.projName,
                                                            self.parent.projectInfo.projDir,
                                                            self.parent.projectInfo.projDir,
                                                            self.parent.projectInfo.projDirNDVI,
                                                            self.parent.projectInfo.srcDirNDVI,
                                                            sensorMode=self.parent.inputMode
                                                            )

            #open analytics
            self.parent.goToAnalyticsTab()


#
#             "<dataset name="slam" typename='IdxMultipleDataset'>
# 	<field name="voronoi">
# 		<code>output=voronoi()</code>
# 	</field>
# 	<dataset name='google'  url='./google.midx' />
# 	<dataset name='visus1'   url='dir1/VisusSlamFiles/visus.midx' />
# 	<dataset name='visus2'   url='dir2/VisusSlamFiles/visus.midx' />
# </dataset> 
#   "
