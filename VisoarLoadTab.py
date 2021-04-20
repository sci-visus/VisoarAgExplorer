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


import xml.etree.ElementTree as ET
import xml.dom.minidom

from editUserLibrary            import *




class VisoarLoadTabWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.DEBUG = True
        self.parent = parent
        self.setStyleSheet(LOOK_AND_FEEL)

        #def tabLoadUI(self):
        # AAG: 05152020 was:
        #		self.sublayoutTabLoad= QVBoxLayout(self)

        class Buttons:
            pass

        self.LOAD_MODE_GRID = 1
        self.LOAD_MODE_LIST = 2
        self.LOAD_MODE_TABLE = 3

        self.buttons = Buttons
        self.cellsAcross = 5
        self.LOAD_MODE =  self.LOAD_MODE_LIST
        #self.LOAD_MODE = self.LOAD_MODE_GRID
        #self.LOAD_MODE = self.LOAD_MODE_TABLE



        self.containerScroll =  QScrollArea(self)
        self.containerScroll.setWidgetResizable(True)
        self.containerScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.containerScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.container = QWidget(self )
        self.sublayoutGrid = QGridLayout(self.container)
        self.sublayoutTabLoad = QVBoxLayout()

        self.sortLayout = QHBoxLayout()

        if True:
            self.sortLibraryLabel = QLabel("Sort Library: ", self)
            self.sortLibraryLabel.setStyleSheet(
                """padding:0px; margin:0px; color: #045951;  background-color:#ffffff""")
            self.sortLibraryLabel.setFixedSize(V_LIST_LABLES, V_BUTTON_SIZE_SM)
            self.comboBoxSortLibrary = QComboBox(self)
            self.comboBoxSortLibrary.addItem("Name (A-Z)")
            self.comboBoxSortLibrary.addItem("Recently Created")
            self.comboBoxSortLibrary.addItem("Recently Updated")
            self.comboBoxSortLibrary.addItem("Name (Z-A)")
            self.comboBoxSortLibrary.addItem("Oldest Created")
            self.comboBoxSortLibrary.addItem("Oldest Updated")
            self.comboBoxSortLibrary.setStyleSheet(MY_COMBOX)
            self.comboBoxSortLibrary.currentIndexChanged.connect(self.sortUserFileBy)
            self.comboBoxSortLibrary.setFixedSize(100, 40)
            self.comboBoxSortLibrary.resize(100, 40)
            self.comboBoxSortLibrary.setFixedWidth(100)
            self.comboBoxSortLibrary.setFixedHeight(40)
            self.comboBoxSortLibrary.setCurrentIndex(1)
            self.sortLayout.addWidget(self.sortLibraryLabel, Qt.AlignLeft)
            self.sortLayout.addWidget(self.comboBoxSortLibrary, Qt.AlignLeft)
            self.sortLayout.addStretch(0)
            self.sublayoutTabLoad.addLayout(self.sortLayout, Qt.AlignLeft)

        self.sublayoutTabLoad.addWidget(self.containerScroll)

        if self.LOAD_MODE == self.LOAD_MODE_LIST or self.LOAD_MODE == self.LOAD_MODE_GRID:
            #self.sublayoutGrid = QGridLayout(self.container)
            self.sublayoutGrid.setAlignment(Qt.AlignTop)
            self.sublayoutGrid.setSpacing(GRID_SPACING)
            self.sublayoutGrid.setHorizontalSpacing(0)
        else:
            self.sublayoutGrid = None


        self.sublayoutTabLoadEditTools = QHBoxLayout()
        self.buttons.edit_library = createPushButton("Move User Library",
                                                     lambda: self.editLibrary())
        self.buttons.edit_library.setStyleSheet(WHITE_PUSH_BUTTON)
        self.buttons.edit_library.resize(280, 40)
        self.buttons.edit_library.setFixedSize(280, 40)

        self.list_group = QHBoxLayout()
        self.list_group.setSpacing(10)

        self.buttons.home = QPushButton('', self)
        self.buttons.home.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
        ##-- self.logo.setStyleSheet("QPushButton {border-style: outset; border-width: 0px;color:#ffffff}");
        self.buttons.home.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'home.png')))
        self.buttons.home.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
        self.buttons.home.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
        self.buttons.home.clicked.connect(self.parent.goHome)


        self.buttons.grid_library = createPushButton("",
                                                     lambda: self.gridModeSwitch())
        self.buttons.grid_library.setStyleSheet(WHITE_PUSH_BUTTON)
        ic = QIcon('icons/grid_green.png')
        self.buttons.grid_library.setIcon(ic)
        fixButtonsLookFeel(self.buttons.grid_library)


        self.buttons.list_library = createPushButton("",
                                                     lambda: self.listModeSwitch())
        self.buttons.list_library.setStyleSheet(WHITE_PUSH_BUTTON)
        ic = QIcon('icons/list_green.png')
        self.buttons.list_library.setIcon(ic)
        fixButtonsLookFeel(self.buttons.list_library)

        self.buttons.list_library.setStyleSheet("margin:10px; padding:10px;""")
        self.buttons.list_library.setFixedSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE)

        self.buttons.grid_library.setStyleSheet("margin:10px; padding:10px;""")
        self.buttons.grid_library.setFixedSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE)

        self.list_group.addWidget(self.buttons.home, alignment=Qt.AlignLeft)
        self.list_group.addWidget(self.buttons.list_library )  # ,row,0)
        self.list_group.addWidget(self.buttons.grid_library)  # ,row,0)

        self.sublayoutTabLoadEditTools.addLayout(self.list_group  )  # ,row,0)

        self.sublayoutTabLoadEditTools.addWidget(self.buttons.edit_library, alignment=Qt.AlignRight)  # ,row,0)

        self.sublayoutTabLoad.addLayout(self.sublayoutTabLoadEditTools)

        self.listModeSwitch()

        self.setLayout(self.sublayoutTabLoad)
        self.setStyleSheet("""background-color: #045951""")
        #self.setStyleSheet("""background-color: #045951""")
        if self.DEBUG:
            print('tabLoadUI created')

        self.parent.visoarUserLibraryData.fixDatesProject()
        # self.scrollLayout = QVBoxLayout(self)
        # self.scrollLayout.addWidget()
        self.LoadFromFile()

        self.containerScroll.setWidget(self.container)
        self.sublayoutTabLoad.setAlignment(Qt.AlignTop)
        self.setLayout(self.sublayoutTabLoad)

    def sortUserFileBy(self):
        self.parent.visoarUserLibraryData.sortUserFileBy(self.comboBoxSortLibrary.currentText() )
        self.LoadFromFile()





    def gridModeSwitch(self):
        self.LOAD_MODE = self.LOAD_MODE_GRID
        self.LoadFromFile()
        self.buttons.grid_library.setStyleSheet("background-color : white; border-radius:5px; border : 3px solid "+visoarHighlightYellow)
        self.buttons.list_library.setStyleSheet("background-color : white; border-radius:5px; border : 3px solid white")

    def listModeSwitch(self):
        self.LOAD_MODE = self.LOAD_MODE_LIST
        self.LoadFromFile()
        self.buttons.list_library.setStyleSheet("background-color : white; border-radius:5px; border : 3px solid "+visoarHighlightYellow)
        self.buttons.grid_library.setStyleSheet("background-color : white; border-radius:5px; border : 3px solid white")


    def addTableWidgetThumbnail(self,table,  r,c,projName, projDir):
        self.fixPathForNewName()
        self.parent.projectInfo.cache_dir = os.path.join(projDir, 'VisusSlamFiles')
        #thumb = os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX/', 'Thumbnail.png')
        thumb = self.getMostRecentImg(os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX'))

        alt = os.path.join(self.parent.app_dir, 'icons', 'VisoarEye80x80.png')
        alt2 = os.path.join(self.parent.app_dir, 'icons', 'VisoarLayerEye.png')

        if path.exists(thumb):
            self.addTableWidgetIcon(table, r, c, thumb)
        else:
            self.addTableWidgetIcon(table, r, c, alt)

    def addTableWidgetIcon(self, table, r, c, imgname):
        iconPixmap = QPixmap(imgname)
        icon = QIcon(iconPixmap)
        widget = QLabel(self)
        pix = QPixmap(imgname)
        pix = pix.scaled(100, 100, Qt.KeepAspectRatio)
        widget.setPixmap(pix)
        self.sublayoutGrid.addWidget(widget)

    def getMostRecentImg(self, dir):
        import glob
        import os
        latest_file = ''
        list_of_files = glob.glob(dir+'/*.png')  # * means all if need specific format then *.csv
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file

    def getThumbnailForProjName(self, imgname, projDir):
        self.fixPathForNewName()
        self.parent.projectInfo.cache_dir = os.path.join(projDir, 'VisusSlamFiles')
        #thumb = os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX/', 'Thumbnail.png')
        thumb = self.getMostRecentImg(os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX'))

        if not path.exists(thumb):
            thumb = os.path.join(self.parent.app_dir, 'icons', 'VisoarEye80x80.png')
        pix = QPixmap(thumb)
        pix = pix.scaled(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE, Qt.KeepAspectRatio)
        icon = QIcon(pix)
        return icon

    def addThumnailToButton(self, btn, projName, projDir, srcDir):
        self.fixPathForNewName()
        self.parent.projectInfo.cache_dir = os.path.join(projDir, 'VisusSlamFiles')
        thumb = self.getMostRecentImg(os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX'))

        #thumb = os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX/', 'Thumbnail.png')
        # thumb  = self.cache_dir+ '/'+projName+'IDX/'+'Thumbnail.png'
        if path.exists(thumb):
            icn = QIcon(thumb)
            btn.setIcon(icn)
            btn.setIconSize( QSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE))
            btn.setFixedSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE)
        else:
            if self.LOAD_MODE == self.LOAD_MODE_GRID:
                if self.parent.projectInfo.doesProjectHaveLayers( ):
                    btn.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'VisoarEyeLayer.png')))
                else:
                    btn.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'VisoarEye.png')))
            else:
                if self.parent.projectInfo.doesProjectHaveLayers( ):
                    btn.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'VisoarEyeLayer.png')))
                else:
                    btn.setIcon(QIcon(os.path.join(self.parent.app_dir, 'icons', 'VisoarEye80x80.png')))
            btn.setIconSize( QSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE))
            btn.setFixedSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE)

    def fixPathForNewName(self):
        import shutil
        import glob
        if os.path.exists(self.parent.projectInfo.cache_dir):
            path = Path(os.path.join(self.parent.projectInfo.cache_dir, self.parent.projectInfo.projName + 'IDX'))
            newpath = Path(os.path.join(self.parent.projectInfo.cache_dir, 'ViSOARIDX'))
            if not os.path.exists(newpath):
                os.makedirs(newpath)
                files = glob.glob(os.path.join(path, "/*"))
                for f in files:
                    print('TEST moving ' + str(f) + 'to ' + str(newpath))
                # shutil.move(f, newpath)



    def editLibrary(self):
        self.editUserLibrary = EditUserLibraryWindow(self.parent.userFileHistory, self)
        self.editUserLibrary.show()



    def cell_was_clicked(self, row, column):
        COL_NAME = 0
        COL_IMAGE = 1
        COL_EDIT = 2
        COL_DELETE = 3
        print("Row %d and Column %d was clicked" % (row, column))
        item_name = self.table.itemAt(row, 0)
        name = item_name.text()
        projectDir = self.parent.visoarUserLibraryData.getProjDirWithName(name)

        if column == COL_EDIT:
            self.editXML(name,projectDir)
        elif column == COL_DELETE:
            self.deleteXML(name)
        elif column == COL_NAME or column == COL_IMAGE:
            self.loadExisitingProject(name)

    def LoadFromFile(self):
        self.parent.visoarUserLibraryData.refreshProjectsFromXML()
        #Clear Layout
        if self.sublayoutGrid:
            clearLayout(self.sublayoutGrid)


        if self.LOAD_MODE == self.LOAD_MODE_GRID:
#            self.container.setStyleSheet("""background-color: #ffffff;color:#045951""")
            self.container.setStyleSheet("""background-color: #045951;color:#045951""")
            self.LoadFromFileGridIcons()
            #
            # self.sublayoutGrid.activate()
            # self.sublayoutTabLoad.activate()
        elif self.LOAD_MODE == self.LOAD_MODE_LIST:
            self.container.setStyleSheet("""background-color: #045951;color:#045951""")
#            self.container.setStyleSheet("""background-color: #ffffff;color:#045951""")
            self.LoadFromFileList()
            # self.sublayoutGrid.activate()
            # self.sublayoutTabLoad.activate()
        else:
            self.LoadFromFileTable()





    def LoadFromFileTable(self):
        #self.sublayoutGrid = None
        self.table = QTableWidget( self.container)
        self.table.cellClicked.connect(self.cell_was_clicked)
        # po = QSizePolicy()
        # po.setHorizontalPolicy(QSizePolicy.Preferred)
        # po.setVerticalPolicy(QSizePolicy.Preferred)
        # po.setVerticalStretch(1)
        # po.setHorizontalStretch(1)
        # self.table.setSizePolicy(po)


        self.table.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)

        ADD_EDIT_BTNS = True
        projects = self.parent.visoarUserLibraryData.projects

        # Parse users history file, contains files they have loaded before

        ROW = 0

        COL_NAME = 0
        COL_IMAGE = 1
        COL_EDIT = 2
        editIconPath = os.path.join(self.parent.app_dir, 'icons', 'Edit.png')
        COL_DELETE = 3
        delIconPath = os.path.join(self.parent.app_dir, 'icons', 'garbage.png')

        # Row count
        self.table.setRowCount(10)

        # Column count
        self.table.setColumnCount(4)

        headerLabelName = QTableWidgetItem('Project Name')
        # headerLabelName.setStyleSheet(
        #     """background-color: #045951;  color:#ffffff""")
        headerLabelEdit = QTableWidgetItem('Edit')
        # headerLabelEdit.setStyleSheet(
        #     """background-color: #045951;  color:#ffffff""")
        headerLabelDel = QTableWidgetItem('Delete')
        # headerLabelDel.setStyleSheet(
        #     """background-color: #045951;  color:#ffffff""")
        headerLabelImg = QTableWidgetItem('Thumbnail')
        #headerLabelImg

        self.table.setStyleSheet(
            """background-color: #ffffff;  color:#045951""")
        self.container.setStyleSheet(
            """background-color: #045951;  color:#ffffff""")
        self.table.setItem(  ROW, COL_NAME,headerLabelName)
        self.table.setItem(  ROW, COL_EDIT,headerLabelEdit)
        self.table.setItem(  ROW, COL_DELETE,headerLabelDel)
        self.table.setItem(  ROW, COL_IMAGE,headerLabelImg)


        ROW = 1
        if self.parent.visoarUserLibraryData.sortReversed:
            projects = reversed(projects)

        for project in  projects:

            projName = project.projName
            projDir = project.projDir
            print(projName + " " + projDir)

            widgetName  = QTableWidgetItem(projName)
            widgetButton = QTableWidgetItem('')
            widgetEdit = QTableWidgetItem('')
            widgetDelete = QTableWidgetItem('')

            # widgetName.setStyleSheet(
            #     """background-color: #ffffff; QTableWidgetItem {background-color: #045951; border-style: outset; border-width: 0px;color:#ffffff}""");
            # widgetButton.setStyleSheet(
            #     """background-color: #ffffff; QTableWidgetItem {background-color: #045951; border-style: outset; border-width: 0px;color:#ffffff}""");
            # widgetEdit.setStyleSheet(
            #     """background-color: #ffffff; QTableWidgetItem {background-color: #045951; border-style: outset; border-width: 0px;color:#ffffff}""");
            # widgetDelete.setStyleSheet(
            #     """background-color: #ffffff; QTableWidgetItem {background-color: #045951; border-style: outset; border-width: 0px;color:#ffffff}""");

            # widgetButton.setMinimumSize(220, 120)
            # widgetEdit.setMinimumSize(60, 60)
            # widgetDelete.setMinimumSize(60,60)

            if True:
                bicon = self.getThumbnailForProjName(projName, projDir)
                widgetButton.setIcon( bicon)
                widgetEdit.setIcon(QIcon(editIconPath))
                widgetDelete.setIcon(QIcon(delIconPath))


            self.parent.loadWidgetDict[projName] = widgetName
            self.parent.loadLabelsWidgetDict[projName] = widgetButton
            self.table.setItem( ROW, COL_NAME,widgetName)
            self.table.setItem( ROW, COL_EDIT,widgetEdit,)
            self.table.setItem(ROW, COL_DELETE,widgetDelete )
            self.table.setItem(ROW, COL_IMAGE,widgetButton )

            ROW= ROW + 1
        self.table.setRowCount(ROW)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
       # self.setTableWidth()
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()


    def setTableWidth(self):
        width = self.table.verticalHeader().width()+200
        width += self.table.horizontalHeader().length()
        if self.table.verticalScrollBar().isVisible():
            width += self.table.verticalScrollBar().width()
        width += self.table.frameWidth() * 2
        self.table.setFixedWidth(width)


    def resizeEvent(self, event):
        if self.LOAD_MODE == self.LOAD_MODE_TABLE:
            self.setTableWidth()



    def LoadFromFileList(self):
        import os.path, time
        #self.sublayoutGrid = QGridLayout(self.container)
        #self.sublayoutGrid.setSpacing(10)
        self.sublayoutGrid.setSpacing(GRID_SPACING)
        self.sublayoutGrid.setHorizontalSpacing(0)

        self.sublayoutGrid.setRowStretch(0, 0)
        self.sublayoutGrid.setRowStretch(1, 0)
        self.sublayoutGrid.setRowStretch(2, 0)
        self.sublayoutGrid.setRowStretch(3, 0)
        self.sublayoutGrid.setRowStretch(4, 0)
        #self.sublayoutGrid.setRowStretch(5, 0)

        projects = self.parent.visoarUserLibraryData.projects

        ROW = 0

        COL_IMAGE = 0
        COL_NAME = 1
        COL_CREATEDAT = 2
        COL_UPDATEDAT = 3
        COL_MODIFY = 4
        editIconPath = os.path.join(self.parent.app_dir, 'icons', 'Edit.png')
        delIconPath = os.path.join(self.parent.app_dir, 'icons', 'garbage.png')


        headerLabelName = QLabel('Project Name')
        headerLabelName.setStyleSheet(
            """padding:0px; margin:0px; background-color: #045951;  color:#ffffff""")
        headerLabelModify = QLabel('Modify')
        headerLabelModify.setStyleSheet(
            """padding:0px; margin:0px;background-color: #045951;  color:#ffffff""")
        #headerLabelDel = QLabel('Delete')
        #headerLabelDel.setStyleSheet(
        #    """background-color: #045951;  color:#ffffff""")
        headerLabelImg = QLabel('Thumbnail')
        headerLabelImg.setStyleSheet(
            """padding:0px; margin:0px;background-color: #045951;  color:#ffffff""")

        headerLabelCreatedAt = QLabel('Created')
        headerLabelCreatedAt.setStyleSheet(
            """padding:0px; margin:0px; background-color: #045951;  color:#ffffff""")

        headerLabelUpdatedAt = QLabel('Updated')
        headerLabelUpdatedAt.setStyleSheet(
            """padding:0px; margin:0px; background-color: #045951;  color:#ffffff""")

        h = V_BUTTON_SIZE_SM
        headerLabelName.setFixedHeight(h)
        headerLabelModify.setFixedHeight(h)
        headerLabelImg.setFixedHeight(h)
        headerLabelCreatedAt.setFixedHeight(h)
        headerLabelUpdatedAt.setFixedHeight(h)
        headerLabelName.setMinimumSize(V_LIST_LABLES, h)
        headerLabelModify.setMinimumSize(V_LIST_LABLES, h)
        headerLabelImg.setMinimumSize(V_LIST_LABLES, h)
        headerLabelCreatedAt.setMinimumSize(V_LIST_DATES, h)
        headerLabelUpdatedAt.setMinimumSize(V_LIST_DATES, h)

        self.sublayoutGrid.addWidget(headerLabelName, ROW, COL_NAME)
        self.sublayoutGrid.addWidget(headerLabelModify, ROW, COL_MODIFY)
        #self.sublayoutGrid.addWidget(headerLabelDel, ROW, COL_DELETE)
        self.sublayoutGrid.addWidget(headerLabelImg, ROW, COL_IMAGE)
        self.sublayoutGrid.addWidget(headerLabelCreatedAt, ROW, COL_CREATEDAT)
        self.sublayoutGrid.addWidget(headerLabelUpdatedAt, ROW, COL_UPDATEDAT)

        ROW = 1
        if self.parent.visoarUserLibraryData.sortReversed:
            projects = reversed(projects)

        for project in projects:

            projName = project.projName
            projDir = project.projDir
            srcDir = project.srcDir
            if project.createdAt:
                createdAtString = project.createdAt
            else:
                file = os.path.join(projDir, 'VisusSlamFiles')
                if os.path.exists(file):
                    createdAtString = datetime.fromtimestamp(os.path.getctime(file)).strftime('%m/%d/%Y')
                else:
                    createdAtString =''


            if project.updatedAt:
                updatedAtString = project.updatedAt
            else:
                file = os.path.join(projDir, 'VisusSlamFiles')
                if os.path.exists(file):
                    updatedAtString =datetime.fromtimestamp(os.path.getmtime(file)).strftime('%m/%d/%Y')
                else:
                    updatedAtString = ''
            print(projName + " " + projDir)
            project.updatedAt = updatedAtString

            widgetName  = QWidget()
            nameLabel = QToolButton(widgetName)
            nameLabel.setText(projName + "\n"+projDir)

            widgetCreatedAt  = QWidget()
            CreatedAtLabel   = QLabel(widgetCreatedAt)
            CreatedAtLabel.setText(createdAtString)
            CreatedAtLabel.setStyleSheet("""padding:10px; margin:0px; background-color: #045951;  color:#ffffff """)
            widgetCreatedAt.setStyleSheet("""padding:10px; margin:0px; background-color: #045951;  color:#ffffff """)


            widgetUpdatedAt  = QWidget()
            updatedAtLabel   = QLabel(widgetUpdatedAt)
            updatedAtLabel.setText(updatedAtString)
            updatedAtLabel.setStyleSheet("""padding:0px; margin:0px; background-color: #045951;  color:#ffffff """)
            widgetUpdatedAt.setStyleSheet("""padding:0px; margin:0px; background-color: #045951;  color:#ffffff """)

            widgetButton = QWidget()
            widgetEdit = QWidget()
            widgetDelete = QWidget()

            widgetName.setStyleSheet(
                """border-radius:10px; padding:30px; margin: 0px; background-color: #ffffff; QToolButton {background-color: #045951; border-style: outset; border-width: 0px;color:#ffffff}""");
            widgetButton.setStyleSheet(
                """border-radius:10px; padding:0px; margin: 0px; background-color: #ffffff; QPushButton {background-color: #ffffff; border-style: outset; border-width: 0px;color:#ffffff}""");
            widgetEdit.setStyleSheet(
                """background-color:none; QPushButton {background-color: none; border-style: outset; border-width: 0px;color:#ffffff}""");
            widgetDelete.setStyleSheet(
                """background-color: none; QPushButton {background-color: none; border-style: outset; border-width: 0px;color:#ffffff}""");

            widgetButton.setMinimumSize(220, V_THUMBNAIL_SIZE)
            widgetEdit.setMinimumSize(V_BUTTON_SIZE, V_BUTTON_SIZE)
            widgetDelete.setMinimumSize(V_BUTTON_SIZE,V_BUTTON_SIZE)
            widgetUpdatedAt.setMinimumSize(V_LIST_DATES, V_BUTTON_SIZE)
            widgetCreatedAt.setMinimumSize(V_LIST_DATES, V_BUTTON_SIZE)

            projMapButton = QPushButton(widgetButton)
            #projMapButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon);
            projMapButton.setStyleSheet(
                """ background-color: transparent; border-style: none; QPushButton {background-color: none; border-style: none; border-color:#ffffff;border-width: 0px;color:#ffffff}""");
            nameLabel.setStyleSheet(
                """background-color: #ffffff; border-style: none; QPushButton {background-color: #045951; border-style: none; border-color:#ffffff;border-width: 0px;color:#ffffff}""");
            self.addThumnailToButton(projMapButton, projName, projDir,srcDir)

            projMapButton.setIconSize(QSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE))
            projMapButton.setFixedSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE)
            projMapButton.setMinimumSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE)
            btnCallback = partial(self.loadExisitingProject, projName)
            projMapButton.clicked.connect(btnCallback)
            nameLabel.clicked.connect(btnCallback)

            modifyLayout = QHBoxLayout()

            widgetEdit.setStyleSheet(
                """background-color: none;  color:#045951""")
            widgetDelete.setStyleSheet(
            """background-color: none;  color:#045951""")

            editXMLButton = QPushButton(widgetEdit)
            editXMLButton.setIcon(QIcon(editIconPath))
            btnCallback = partial(self.editXML, projName, projDir)
            editXMLButton.clicked.connect(btnCallback)
            #p = projMapButton.geometry().bottomRight() - QPoint(320, 50)
            # editXMLButton.move(p)

            deleteXMLButton = QPushButton(widgetDelete)
            deleteXMLButton.setIcon(QIcon(delIconPath))
            btnCallback = partial(self.deleteXML, projName)
            deleteXMLButton.clicked.connect(btnCallback)
            #p = projMapButton.geometry().bottomRight() - QPoint(60, 50)
            #deleteXMLButton.move(p)

            editXMLButton.setStyleSheet(CLEARBACKGROUND_PUSH_BUTTON)
            btn_size = V_BUTTON_SIZE_SM
            editXMLButton.resize(btn_size, btn_size)
            editXMLButton.setFixedSize(V_BUTTON_SIZE_SM, btn_size  )
            editXMLButton.setIconSize(QSize(btn_size, btn_size))

            deleteXMLButton.setStyleSheet(CLEARBACKGROUND_PUSH_BUTTON)
            deleteXMLButton.resize(btn_size, btn_size)
            deleteXMLButton.setFixedSize(V_BUTTON_SIZE_SM, btn_size  )
            deleteXMLButton.setIconSize(QSize(btn_size, btn_size))

            widgetDelete.setFixedSize(V_BUTTON_SIZE_SM, btn_size  )
            widgetEdit.setFixedSize(V_BUTTON_SIZE_SM, btn_size )
            widgetName.setFixedHeight(V_THUMBNAIL_SIZE)
            widgetCreatedAt.setFixedSize(V_LIST_DATES, V_THUMBNAIL_SIZE)
            widgetUpdatedAt.setFixedSize(V_LIST_DATES, V_THUMBNAIL_SIZE)
            updatedAtLabel.setFixedSize(V_LIST_DATES, V_THUMBNAIL_SIZE)
            CreatedAtLabel.setFixedSize(V_LIST_DATES, V_THUMBNAIL_SIZE)
            widgetButton.setFixedSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE)

            modifyLayout.addWidget(widgetDelete )
            modifyLayout.addWidget(widgetEdit )
            # self.sublayoutGrid.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            self.parent.loadWidgetDict[projName] = nameLabel
            self.parent.loadLabelsWidgetDict[projName] = projMapButton
            self.sublayoutGrid.addWidget(widgetName, ROW, COL_NAME  )
            self.sublayoutGrid.addLayout(modifyLayout, ROW, COL_MODIFY )
            #self.sublayoutGrid.addWidget(widgetDelete, ROW, COL_DELETE)
            self.sublayoutGrid.addWidget(widgetButton, ROW, COL_IMAGE )
            self.sublayoutGrid.addWidget(widgetCreatedAt, ROW, COL_CREATEDAT )
            self.sublayoutGrid.addWidget(widgetUpdatedAt, ROW, COL_UPDATEDAT )

            ROW= ROW + 1


    # User wants to load a project that has already been stitched (this is a hope that the midx files exists)
    def LoadFromFileGridIcons(self):

        #self.sublayoutGrid = QGridLayout(self.container)
        #self.sublayoutGrid.setSpacing(10)
        self.sublayoutGrid.setSpacing(GRID_SPACING)
        self.sublayoutGrid.setRowStretch(0, self.cellsAcross)
        self.sublayoutGrid.setRowStretch(1, 4)
        self.sublayoutGrid.setRowStretch(2, 0)
        self.sublayoutGrid.setRowStretch(3, 0)

        # Parse users history file, contains files they have loaded before
        projects = self.parent.visoarUserLibraryData.projects

        x = 0
        y = 0
        width = self.cellsAcross - 1

        if self.parent.visoarUserLibraryData.sortReversed:
            projects = reversed(projects)

        for project in projects:

            projName = project.projName
            projDir = project.projDir
            srcDir = project.srcDir
            print(projName + " " + projDir)

            widget = QWidget()
            widget.setMinimumSize(PROJ_BUTTON_WIDTH, PROJ_BUTTON_HEIGHT+NAME_BUTTON_HEIGHT)
            widget.setStyleSheet("""border-radius:10px; padding:0px; margin:0px; background: #ffffff; color:#045951; """)

            projectLayout = QVBoxLayout(widget)
            projectLayout.setSpacing(0)
            nameLabel = QPushButton(widget)
            nameLabel.setText(projName)
            nameLabel.setStyleSheet("""border-radius:10px; padding:0px; margin:0px; background: #ffffff; color:#045951; """)
            nameLabel.setMinimumSize(NAME_BUTTON_WIDTH, NAME_BUTTON_HEIGHT)
            btnCallback = partial(self.loadExisitingProject, projName)
            nameLabel.clicked.connect(btnCallback)
            projectLayout.addWidget(nameLabel)

            projMapButton = QToolButton()
            projectLayout.addWidget(projMapButton)
            #projMapButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            projMapButton.setStyleSheet(
                """border-radius:10px; background-color: #ffffff; QToolButton {background-color: #045951; border-radius:10px;border-style: outset; border-width: 0px;color:#ffffff}""")
            #projMapButton.setText(projName)
            self.addThumnailToButton(projMapButton, projName, projDir,srcDir )

            projMapButton.setIconSize(QSize(ICON_BUTTON_WIDTH, ICON_BUTTON_HEIGHT))
            projMapButton.setFixedSize(PROJ_BUTTON_WIDTH, PROJ_BUTTON_HEIGHT )
            #projMapButton.setMinimumSize(PROJ_BUTTON_WIDTH, PROJ_BUTTON_HEIGHT )
            btnCallback = partial(self.loadExisitingProject, projName)
            projMapButton.clicked.connect(btnCallback)

            editXMLButton = QPushButton(widget)
            editXMLButton.setIcon(QIcon('icons/Edit_green.png'))
            editXMLButton.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
            editXMLButton.resize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
            editXMLButton.setFixedSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
            btnCallback = partial(self.editXML, projName, projDir)
            editXMLButton.clicked.connect(btnCallback)

            deleteXMLButton = QPushButton(widget)
            deleteXMLButton.setIcon(QIcon('icons/garbage_green.png'))
            deleteXMLButton.setIconSize(QSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM))
            deleteXMLButton.setFixedSize(V_BUTTON_SIZE_SM, V_BUTTON_SIZE_SM)
            btnCallback = partial(self.deleteXML, projName)
            deleteXMLButton.clicked.connect(btnCallback)
            p = projMapButton.geometry().bottomRight() - QPoint(30, 5)
            deleteXMLButton.move(p)

            editXMLButton.setStyleSheet(SEMICLEARBACKGROUND_PUSH_BUTTON)
            deleteXMLButton.setStyleSheet(SEMICLEARBACKGROUND_PUSH_BUTTON)

            p = projMapButton.geometry().bottomRight() - QPoint(PROJ_BUTTON_WIDTH-10, 5)
            editXMLButton.move(p)
            p = projMapButton.geometry().bottomRight() - QPoint(V_BUTTON_SIZE_SM/2, 5)
            deleteXMLButton.move(p)

            self.parent.loadWidgetDict[projName] = nameLabel
            self.parent.loadLabelsWidgetDict[projName] = projMapButton
            self.sublayoutGrid.addWidget(widget,x,y)

            if (y < width):
                y = y + 1
            else:
                y = 0
                x = x + 1
        if self.DEBUG:
            print('LoadFromFile finished with '+str(x)+' '+str(y))

    def removeLoadButtonWidget(self, name):
        if (self.LOAD_MODE == self.LOAD_MODE_LIST):
            # delete row of list:
            print('NYI')
        elif (self.LOAD_MODE == self.LOAD_MODE_TABLE):
            # delete row of table:
            print('NYI')
        else:
            widget = self.parent.loadWidgetDict[name]
            self.sublayoutGrid.removeWidget(widget)
            # widget.setParent(None)
            widget.deleteLater()
        self.sublayoutGrid.activate()
        self.sublayoutTabLoad.activate()

    def refreshLoadButtonWidgetWithName(self, oldProjName, newProjName):
        if not (self.LOAD_MODE == self.LOAD_MODE_GRID):
            btn = self.parent.loadWidgetDict[oldProjName]
            btn.setText(newProjName)
            btnCallback = partial(self.loadExisitingProject, newProjName)
            btn.clicked.connect(btnCallback)
            btn.repaint()

        btn = self.parent.loadLabelsWidgetDict[oldProjName]
        if not (self.LOAD_MODE == self.LOAD_MODE_LIST):
            btn.setText(newProjName)
        btnCallback = partial(self.loadExisitingProject, newProjName)
        btn.clicked.connect(btnCallback)
        btn.repaint()
        self.sublayoutGrid.activate()
        self.sublayoutTabLoad.activate()

    def refreshLoadButtonWidget(self):
        self.sublayoutGrid.activate()
        self.sublayoutTabLoad.activate()

    def refreshLoadTab(self):
        if self.sublayoutGrid:
            for i in reversed(range(self.sublayoutGrid.count())):
                widgetToRemove = self.sublayoutGrid.itemAt(i).widget()
                if (widgetToRemove != None):
                    # remove it from the layout list
                    self.sublayoutGrid.removeWidget(widgetToRemove)
                    # remove it from the gui

                    widgetToRemove.setParent(None)
        if self.parent.isViewNewStitch():
            print('On Tab: Load')
            self.LoadFromFile()

    def editXML(self, projName, projDir):

        projDir = self.parent.visoarUserLibraryData.getProjDirWithName(projName)
        editWindow = EditUserLibraryItemWindow(self.parent.userFileHistory, projName, projDir, self)
        editWindow.show()

        print('Edit Library Item')

    def deleteXML(self, projName):
        print('INPUT: {0} '.format(projName))

        qm = QMessageBox()
        qm.setWindowTitle('Delete?')
        #qm.setText("Are you sure you want to delete {0} project from your ViSOAR Library? \n(Files will still be on your drive)".format(
        #                      projName))
        qm.setStyleSheet(POPUP_LOOK_AND_FEEL)
        qm.setStyleSheet("""color: #045951; background-color:white;""")
        ret = qm.question(self, '',
                          "Are you sure you want to delete {0} project from your ViSOAR Library? \n(Files will still be on your drive)".format(
                              projName), qm.Yes | qm.No)
        #qm.findChild( QPushButton).setStyleSheet(POPUP_LOOK_AND_FEEL)

        if ret == qm.Yes:
            ret = self.parent.visoarUserLibraryData.deleteXML(projName)
            if ret:
                self.removeLoadButtonWidget(projName)
                msg = QMessageBox()
                msg.setWindowTitle('Deleted Item')
                msg.setText('Deleted Item from User Library List \n(Files are still on your drive).')
                msg.setStyleSheet(POPUP_LOOK_AND_FEEL)
                x = msg.exec_()

        print('deleteXML done')
        self.LoadFromFile()

    def saveUserFileHistory(self):
        ret = self.parent.visoarUserLibraryData.saveUserFileHistory()
        if self.DEBUG:
            print('saveUserFileHistory finished')

    def loadExisitingProject(self, projName):
        print('loadExisitingProject: '+projName)
        ret,self.parent.projectInfo = self.parent.visoarUserLibraryData.loadExisitingProject(projName)

        if ret:
            self.loadMIDX(   )
            print('Need to run visus viewer with projDir + /VisusSlamFiles/visus.midx')
        if self.DEBUG:
            print('triggerButton finished')

    def loadMIDX(self ):
        if not os.path.exists(self.parent.projectInfo.projDir):
            popUP('ERROR', 'Could not get to file. Is the drive mounted? \n' + self.parent.projectInfo.projDir)
            self.parent.goHome()
            return
        self.parent.projectInfo.cache_dir = os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles')
        ret = self.parent.projectInfo.doesProjectHaveLayers( )
        if ret:
            self.parent.enableViewStitching(enabledView= False)

        print("NYI")
        print('Run visus viewer with: ' + self.parent.projectInfo.projDir + '/VisusSlamFiles/visus.midx')
        if not os.path.exists(os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles')):
            os.makedirs(os.path.join( self.parent.projectInfo.projDir, 'VisusSlamFiles'))
        if (os.path.exists(os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles', 'visus.midx'))):
            self.addToLayerViewer(os.path.join(self.parent.projectInfo.projDir, 'VisusSlamFiles', 'visus.midx'))
        elif (os.path.exists(os.path.join(self.parent.projectInfo.projDir,'visus.midx'))):
            self.addToLayerViewer(os.path.join(self.parent.projectInfo.projDir, 'visus.midx'))
        elif (os.path.exists(os.path.join(self.parent.projectInfo.srcDir,'VisusSlamFiles', 'visus.midx'))):
            self.addToLayerViewer(os.path.join(self.parent.projectInfo.srcDir,'VisusSlamFiles', 'visus.midx'))
        ret1, ret2 = self.parent.openMIDX()

        # self.viewer.run()
        # self.viewer.hide()

        # self.tabs.setTabEnabled(2,True)
        if ret1 and ret2:
            self.parent.setUpCams()
            self.parent.enableViewAnalytics()
            self.parent.changeViewAnalytics()
        if self.DEBUG:
            print('loadMIDX finished')
        return ret1

    def addToLayerViewer(self, filename):
        # Need to parse the midx
        #look over sub datasets and see if the url ends in midx
        #if it does, add it to the layer list
        self.parent.visoarLayerList = []

        tree = ET.parse(filename)
        print(tree.getroot())
        root = tree.getroot()
        row = 0
        for aMidx in root.iterfind('dataset'):
            row = row+1
            aurl = aMidx.attrib.get('url')
            aname = aMidx.attrib.get('name')
            print(aurl)
            print(aname)
            self.parent.visoarLayerList.append(VisoarLayer(aurl,aname,row))


