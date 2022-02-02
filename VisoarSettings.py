import sys, os
import os.path

from pathlib import Path

from os import path

import platform, subprocess, glob
from functools import partial

from PyQt5.QtWidgets                  import QScrollArea, QToolButton
from PyQt5.QtWebEngineWidgets         import QWebEngineView
from OpenVisus                        import *
from OpenVisus.VisusKernelPy                        import *
from OpenVisus.gui                    import *
from datetime import datetime

DEBUG = False
ENABLE_SAVE_IDX = False

MASTER_SCRIPT_LIST = ["Original","NDVI_MAPIR", "NDVI_MAPIR_normalized",  "TGI","TGI_normalized", "NDVI_Agrocam","NDVI", "TGI_Threshold", "NDVI_Threshold",  "Threshold"]
EXPERIMENTAL_SCRIPT_LIST = ["Original","NDVI_MAPIR","NDVI_MAPIR_normalized","NDVI_MAPIR_normalized_Nzones","NDVI_Agrocam","channel_1", "channel_2", "channel_3","NDVI_Sentera", "NDRE_Sentera",  "Contour", "Count", "NDVI",
                            "NDVI_Threshold", "Row", "Segment", "TGI","TGI_normalized", "TGI_alone",
                            "TGI_matplotlib", "TGI_nomatplotlib", "TGI_Threshold", "Threshold"]

SHOW_OUTPUT_BOX = False  # I can't get it to capture anything from the scripting node yet

from lookAndFeel import *

import xml.etree.ElementTree as ET
import xml.dom.minidom


def checkForUpdates(parent, log=None):
    if log:
        log.print("Checking for updates")
    import git
    ThisDir = os.path.dirname(os.path.realpath(__file__))
    g = git.Git( ThisDir )
    try:
        retcode = g.pull('origin', 'master')
        if retcode.startswith('Already'):
            message = "Software is already updated"
            if log:
                log.print(message)
            QMessageBox.about(parent, "Ok", message)
        else:
            message = "Software has been updated. You NEED TO RESTART"
            if log:
                log.print(message)
            QMessageBox.about(parent, "Error", message)
    except :
        QMessageBox.about(parent, "Error", 'Error with git')


# createButton
def createButton( text, callback=None):
    ret = QPushButton(text)
    if callback is not None:
        ret.clicked.connect(callback)
    return ret


# createComboBox
def createComboBox( options=[], callback=None):
    ret = QComboBox()
    ret.addItems(options)
    if callback:
        ret.currentIndexChanged.connect(callback)
    return ret


# separator
def separator():
    line = QLabel(" ")
    # line.setFrameShape(QFrame.HLine)
    # line.setFrameShadow(QFrame.Sunken)
    return line


# hlayout
def hlayout( items):
    ret = QHBoxLayout()
    for item in items:
        try:
            ret.addWidget(item)
        except:
            ret.addLayout(item)
    return ret


# vlayout
def vlayout( items):
    ret = QVBoxLayout()
    for item in items:
        if item.widget() is not None:
            ret.addWidget(item)
        else:
            ret.addLayout(item)
    return ret


# clearLayout
def clearLayout(  layout):
    if layout is None: return
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            clearLayout(item.layout())


def getNameFromMIDX( filename):
    dir, filestr = os.path.split(filename)
    filesplit = os.path.splitext(filestr)
    namestr = filesplit[0]
    ext = filesplit[1]
    if (namestr == 'google'):
        #print('{0} {1} {2}'.format(dir, namestr, ext))
        return dir, namestr, ext
    else:
        s1, s2 = os.path.split(dir)
        s3, s4 = os.path.split(s1)
        #print('{0} {1} {2}'.format(dir, s4, ext))
        return dir, s4, ext




class VisoarLayer():
    def __init__(self, dir,name,rowInt):
        self.dir = dir
        self.name = name
        self.rowInt = rowInt


class VisoarLayerView(QDialog):
    def __init__(self, parent,layers,viewer):
        super(VisoarLayerView, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.parent = parent
        self.viewer = viewer
        self.DEBUG = True
        self.visoarLayersList = layers
        self.GRID_SPACING = 10
        self.ShowXMLButton = []
        self.ShowMapButton = []
        self.HideXMLButton = []
        self.ShowIconGreenPath = os.path.join(self.parent.app_dir, 'icons', 'Show_green.png')
        self.hideIconGreenPath = os.path.join(self.parent.app_dir, 'icons', 'Hide_green.png')
        self.ShowIconGrayPath = os.path.join(self.parent.app_dir, 'icons', 'Show.png')
        self.hideIconGrayPath = os.path.join(self.parent.app_dir, 'icons', 'Hide.png')

        class Buttons:
            pass

        self.buttons = Buttons

        self.layout = QVBoxLayout()
        self.layout.setSpacing(self.GRID_SPACING)
        #self.setStyleSheet(LOOK_AND_FEEL)
        self.setStyleSheet("""QDialog{min-width : 350;min-height:500}""")

        # self.nameLayout = QHBoxLayout()
        # self.buttons.projNameLabel = QLabel('New Project Name:')
        # self.buttons.projNametextbox = QLineEdit(self)
        # self.buttons.projNametextbox.setStyleSheet(
        #     "min-height:30; min-width:180; padding:0px; background-color: #e6e6e6; color: rgb(0, 0, 0);  border: 2px solid #09cab8")
        # self.nameLayout.addWidget(self.buttons.projNameLabel, alignment=Qt.AlignLeft)
        # self.nameLayout.addWidget(self.buttons.projNametextbox, alignment=Qt.AlignLeft)
        # self.nameLayout.addStretch(True)
        # self.layout.addLayout(self.nameLayout )
        #
        # self.saveLayout = QHBoxLayout()
        # self.buttons.saveDirLabel = QLabel('Save Time Series Directory: ')
        # self.buttons.saveDirNameLabel = QLabel('')
        #
        # self.buttons.btnSetSaveDir = QPushButton(". . .")
        # self.buttons.btnSetSaveDir.clicked.connect(self.setSaveDirectory)
        # self.buttons.btnSetSaveDir.setStyleSheet(GREEN_PUSH_BUTTON)
        # self.saveLayout.addWidget(self.buttons.saveDirLabel, alignment=Qt.AlignLeft)
        # self.saveLayout.addWidget(self.buttons.saveDirNameLabel, alignment=Qt.AlignLeft)
        # self.saveLayout.addWidget(self.buttons.btnSetSaveDir, alignment=Qt.AlignLeft)
        # self.saveLayout.addStretch(True)
        # self.layout.addLayout(self.saveLayout)
        #
        # self.buttons.buttonStitching = QPushButton('Add MIDX file', self)
        # self.buttons.buttonStitching.resize(180, 40)
        # self.buttons.buttonStitching.clicked.connect(self.addMIDXFiles)
        # self.buttons.buttonStitching.setStyleSheet(GREEN_PUSH_BUTTON)
        # self.layout.addWidget(self.buttons.buttonStitching, alignment=Qt.AlignLeft)

        self.buttons.listLabel = QLabel('Layers:')
        self.layout.addWidget(self.buttons.listLabel, alignment=Qt.AlignLeft)

        # List View of Files
        self.containerScroll = QScrollArea(self)
        self.containerScroll.setWidgetResizable(True)
        self.containerScroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.containerScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.container = QWidget(self)
        self.sublayoutGrid = QGridLayout(self.container)
        self.sublayoutGrid.setSpacing(GRID_SPACING)
        self.sublayoutGrid.setHorizontalSpacing(0)
        self.sublayoutGrid.setAlignment(Qt.AlignTop)

        self.layout.addWidget(self.containerScroll)

        # self.buttons.btnCreateTimeSeries = QPushButton("")
        # self.buttons.btnCreateTimeSeries.clicked.connect(self.createTimeSeries)
        # self.buttons.btnCreateTimeSeries.setStyleSheet(GREEN_PUSH_BUTTON)
        # self.layout.addWidget(self.buttons.btnCreateTimeSeries, alignment=Qt.AlignRight)

        self.containerScroll.setWidget(self.container)
        self.setLayout(self.layout)

        self.createLayerLayout()

    def createLayerLayout(self):
        clearLayout(self.sublayoutGrid)
        COL_NAME = 0
        COL_MODIFY = 1
        COL_MAP = 2

        ROW = 0
        headerLabelName = QLabel('Project Name')
        headerLabelName.setStyleSheet(
            """padding:0px; margin:0px; background-color: #045951;  color:#ffffff""")
        headerLabelModify = QLabel('Dataset')
        headerLabelModify.setStyleSheet(
            """padding:0px; margin:0px;background-color: #045951;  color:#ffffff""")
        headerLabelMap = QLabel('With Map')
        headerLabelMap.setStyleSheet(
            """padding:0px; margin:0px;background-color: #045951;  color:#ffffff""")
        h = V_BUTTON_SIZE_SM
        headerLabelName.setFixedHeight(h)
        headerLabelModify.setFixedHeight(h)
        headerLabelMap.setFixedHeight(h)
        headerLabelName.setMinimumSize(V_LIST_LABLES, h)
        headerLabelModify.setMinimumSize(V_LIST_LABLES, h)
        headerLabelMap.setMinimumSize(V_LIST_LABLES, h)
        self.sublayoutGrid.addWidget(headerLabelName, ROW, COL_NAME)
        self.sublayoutGrid.addWidget(headerLabelModify, ROW, COL_MODIFY)
        self.sublayoutGrid.addWidget(headerLabelMap, ROW, COL_MAP)
        self.ShowXMLButton.append(QPushButton())
        self.HideXMLButton.append(QPushButton())
        self.ShowMapButton.append(QPushButton())
        ROW = ROW + 1
        for alayer in self.visoarLayersList:
            #print(alayer.name)
            widgetName = QWidget()
            nameLabel = QToolButton(widgetName)
            if (alayer.name=='google'):
                nameLabel.setText('All layers')
            else:
                nameLabel.setText(alayer.name)
            widgetShow = QWidget()
            # widgetHide = QWidget()
            widgetName.setStyleSheet(
                """border-radius:10px; padding:10px; margin: 0px; background-color: #eeeeee; QToolButton {background-color: #eeeeee; border-style: outset; border-width: 0px;color:#045951}""");
            widgetShow.setStyleSheet(
                """background-color:none; QPushButton {background-color: none; border-style: outset; border-width: 0px;color:#045951}""");
            # widgetHide.setStyleSheet(
            #     """background-color: none; QPushButton {background-color: none; border-style: outset; border-width: 0px;color:#045951}""");

            widgetShow.setMinimumSize(h, h)
            # widgetHide.setMinimumSize(h, h)
            widgetShow.setStyleSheet(
                """background-color: none;  color:#ffffff""")
            #widgetHide.setStyleSheet("""background-color: none;  color:#ffffff""")
            self.ShowXMLButton.append(QPushButton(widgetShow))
            self.ShowXMLButton[ROW].setIcon(QIcon(self.ShowIconGreenPath))
            btnCallback = partial(self.ShowName, alayer.name)
            self.ShowXMLButton[ROW].clicked.connect(btnCallback)

            # self.HideXMLButton.append(QPushButton(widgetHide))
            # self.HideXMLButton[ROW].setIcon(QIcon(self.hideIconGreenPath))
            # btnCallback = partial(self.HideName, alayer.name)
            # self.HideXMLButton[ROW].clicked.connect(btnCallback)

            self.ShowXMLButton[ROW].setStyleSheet(CLEARBACKGROUND_PUSH_BUTTON)
            self.ShowXMLButton[ROW].resize(h, h)
            self.ShowXMLButton[ROW].setFixedSize(h, h)
            self.ShowXMLButton[ROW].setIconSize(QSize(h, h))

            widgetMap = QWidget()
            widgetMap.setStyleSheet(
                """border-radius:10px; padding:10px; margin: 0px; background-color: #eeeeee; QToolButton {background-color: #eeeeee; border-style: outset; border-width: 0px;color:#045951}""");
            widgetMap.setMinimumSize(h, h)
            widgetMap.setFixedHeight(h)
            self.ShowMapButton.append(QPushButton(widgetMap))
            self.ShowMapButton[ROW].setIcon(QIcon(self.ShowIconGreenPath))
            btnCallback = partial(self.ShowMap, alayer.name)
            self.ShowMapButton[ROW].clicked.connect(btnCallback)
            self.ShowMapButton[ROW].setStyleSheet(CLEARBACKGROUND_PUSH_BUTTON)
            self.ShowMapButton[ROW].resize(h, h)
            self.ShowMapButton[ROW].setFixedSize(h, h)
            self.ShowMapButton[ROW].setIconSize(QSize(h, h))

            if (alayer.name == 'google'):
                self.ShowXMLButton[ROW].hide()

            widgetShow.setFixedSize(h, h)
            widgetName.setFixedHeight(h)
            modifyLayout = QHBoxLayout()
            modifyLayout2 = QHBoxLayout()

            modifyLayout.addWidget(widgetShow)
            modifyLayout2.addWidget(widgetMap)

            self.sublayoutGrid.addWidget(widgetName, ROW, COL_NAME)
            self.sublayoutGrid.addLayout(modifyLayout, ROW, COL_MODIFY)
            self.sublayoutGrid.addLayout(modifyLayout2, ROW, COL_MAP)
            ROW = ROW + 1

    def ShowName(self, name):
        ROW = 0
        #fixview = False
        self.cam = self.viewer.getGLCamera()
        if name == 'google':
            try:
                self.viewer.open(os.path.join(self.parent.projectInfo.cache_dir, 'visus.midx'))
            except:
                popUP('Error', 'Error VisoarSetting 323 loading: {0}'.format(os.path.join(self.parent.projectInfo.cache_dir, 'visus.midx')))
            # db = self.viewer.getDataset()
            # for alayer in self.visoarLayersList:
            #     if alayer.name != 'google' and db.getChild(alayer.name) and (not fixview):
            #         box = db.getChild(alayer.name).getDatasetBounds().toAxisAlignedBox()
            #         self.viewer.getGLCamera().guessPosition(box)
            #         fixview = True

        for alayer in self.visoarLayersList:
            ROW = ROW+1
            if alayer.name == name:
                self.ShowXMLButton[ROW].setIcon(QIcon(self.ShowIconGreenPath))
                self.ShowMapButton[ROW].setIcon(QIcon(self.hideIconGreenPath))
                #self.HideXMLButton[ROW].setIcon(QIcon(self.hideIconGrayPath))
                if (name != 'google'):
                    try:
                        ret1 = self.viewer.open(alayer.dir )
                    except:
                        popUP('Error', 'Error VisoarSettings 341 loading: {0}'.format(alayer.dir))

                #ret2 = self.parent.viewer2.open( alayer.dir )
            else:
                self.ShowXMLButton[ROW].setIcon(QIcon(self.hideIconGreenPath))
                self.ShowMapButton[ROW].setIcon(QIcon(self.hideIconGreenPath))
        self.fixCamera( self.cam)
        self.update()
        #print('NYI')

    def ShowMap(self,name):
        self.cam = self.viewer.getGLCamera()
        ROW = 0
        #fixview = False
        if name == 'google':
            try:
                self.viewer.open(os.path.join(self.parent.projectInfo.cache_dir, 'visus.midx'))
            except:
                popUP('Error', 'Error VisoarSettings 359 loading: {0}'.format(os.path.join(self.parent.projectInfo.cache_dir, 'visus.midx')))
            # db = self.viewer.getDataset()
            # for alayer in self.visoarLayersList:
            #     if alayer.name != 'google' and db.getChild(alayer.name) and (not fixview):
            #         box = db.getChild(alayer.name).getDatasetBounds().toAxisAlignedBox()
            #         self.viewer.getGLCamera().guessPosition(box)
            #         fixview=True

        for alayer in self.visoarLayersList:
            ROW = ROW + 1
            if alayer.name == name:
                self.ShowMapButton[ROW].setIcon(QIcon(self.ShowIconGreenPath))
                self.ShowXMLButton[ROW].setIcon(QIcon(self.hideIconGreenPath))
                if (name != 'google'):
                    import re
                    fname = alayer.dir
                    newfname=re.sub('visus.midx$', 'google.midx', fname)
                    try:
                        ret1 = self.viewer.open(newfname)
                        db = self.viewer.getDataset()
                        box = db.getChild('visus').getDatasetBounds().toAxisAlignedBox()
                        self.viewer.getGLCamera().guessPosition(box)
                    except:
                        popUP('Error', 'Error VisoarSettings 379 loading: {0}'.format(newfname))

            else:
                self.ShowMapButton[ROW].setIcon(QIcon(self.hideIconGreenPath))
                self.ShowXMLButton[ROW].setIcon(QIcon(self.hideIconGreenPath))
        self.fixCamera( self.cam)
        self.update()



    def HideName(self, name):
        print('NYI: VisoarSettings.py HideName Function')

    def fixCamera(self, cam1):
        cam2 = self.viewer.getGLCamera()
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

class VisoarProject():
    def __init__(self):
        self.projDir = ''
        self.srcDirNDVI = ''
        self.projDirNDVI = ''
        self.projName = ''
        self.srcDir = ''
        self.cache_dir = os.path.join(self.projDir, 'VisusSlamFiles')
        self.createdAt =  ''
        self.updatedAt = ''
        self.sensor = ''

    def update(self, projName, projDir, cache_dir, srcDir, createdAt, updatedAt, projDirNDVI,srcDirNDVI, sensorMode='Unknown'):
        self.projDir = projDir
        self.projName = projName
        self.srcDir = srcDir
        self.projDirNDVI = projDirNDVI
        self.srcDirNDVI = srcDirNDVI
        self.cache_dir = cache_dir
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.sensor = sensorMode

    def reset(self):
        self.projDir = ''
        self.srcDirNDVI = ''
        self.projDirNDVI = ''
        self.projName = ''
        self.srcDir = ''
        self.cache_dir = ''
        self.createdAt = ''
        self.updatedAt = ''
        self.sensor = ''


    def doesProjectHaveLayers(self):
        #ignoring google, does this project have layers
        if  not os.path.exists(os.path.join(self.projDir, 'VisusSlamFiles', 'visus.midx')):
            #popUP('File not found', 'Could not find file: \n' + os.path.join(os.path.join(projDir, 'VisusSlamFiles', 'visus.midx')+ '\nThis error is due to errors in the userFileHistory.xml not matching the content on disk.'))
            #This error is due to errors in the userhistory not matching the content on disk
            return False
        try:
            tree = ET.parse(os.path.join(self.projDir, 'VisusSlamFiles', 'visus.midx'))
            wrapperdataset = tree.getroot()
            count = 0
            for visusfile in wrapperdataset.iterfind('dataset'):
                if  visusfile.attrib['name'] == 'google':
                     print('found google')
                else:
                    count = count + 1
            if count > 1:
                return True
            else:
                return False
        except:
            self.parent.popUP('Does Project Have Layers',
                  'Error in Does Project Have Layers')
            print('Error VisoarSettings.py: in Does Project Have Layers')
            return False


    # def setSrcDirNDVI(self,dir):
    #     self.srcDirNDVI = dir
    #     self.projDirNDVI =  os.path.join(self.projDir,'NDVI')
    #     if not os.path.exists(self.projDirNDVI):
    #         os.mkdir(self.projDirNDVI)

def clearLayout(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())

def pretty_print_xml_given_root(root, output_xml):
    #from xml.dom import minidom
    """
    Useful for when you are editing xml data on the fly
    """
    xml_string = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml()
    xml_string = os.linesep.join(
        [s for s in xml_string.splitlines() if s.strip()])  # remove the weird newline issue
    with open(output_xml, "w") as file_out:
        file_out.write(xml_string)
        file_out.write('\n\n')

def pretty_print_xml_given_file(input_xml, output_xml):
    #from xml.dom import minidom
    """
    Useful for when you want to reformat an already existing xml file
    """
    tree = ET.parse(input_xml)
    root = tree.getroot()
    pretty_print_xml_given_root(root, output_xml)

class VisoarUserLibraryData():
    def __init__(self, userFileHistory):
        visoarUserLibraryProjects = []
        self.userFileHistory = userFileHistory
        self.projects = []
        self.refreshProjectsFromXML()
        self.sortReversed = False

    def createProject(self, projName, projDir,srcDir,projDirNDVI, srcDirNDVI, sensorMode='Unknown'):
        tree = ET.parse(self.userFileHistory)
        #print(tree.getroot())
        root = tree.getroot()

        # etree.SubElement(item, 'Date').text = '2014-01-01'
        element = ET.Element('project')
        ET.SubElement(element, 'projName').text = projName
        ET.SubElement(element, 'projDir').text =  projDir
        ET.SubElement(element, 'srcDir').text =  srcDir
        ET.SubElement(element, 'srcDirNDVI').text =  srcDirNDVI
        ET.SubElement(element, 'projDirNDVI').text =  projDirNDVI
        ET.SubElement(element, 'cache_dir').text = os.path.join(projDir,'VisusSlamFiles')
        ET.SubElement(element, 'sensor').text =  sensorMode
        from datetime import datetime
        today = datetime.now()
        todayFormated = today.strftime("%Y%m%d_%H%M%S")
        ET.SubElement(element, 'createdAt').text = todayFormated
        ET.SubElement(element, 'updatedAt').text = todayFormated

        root.append(element)

        # from xml.dom import minidom
        #
        # xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        # with open(self.userFileHistory, "w") as f:
        #     f.write(xmlstr)

        pretty_print_xml_given_root(root,self.userFileHistory)
        #tree.write(self.userFileHistory)
        print('Wrote new project to history')

    def refreshProjectsFromXML(self):
        self.projects = []
        tree = ET.ElementTree(file=self.userFileHistory)
        # print (tree.getroot())
        root = tree.getroot()
        for project in root.iterfind('project'):
            #print(project.attrib)
            projName = project.find('projName').text
            projDir = project.find('projDir').text
            if (project.find('srcDir'))!=None:
                srcDir= project.find('srcDir').text
            else:
                srcDir = ''
            if (project.find('projDirNDVI'))!=None:
                projDirNDVI = project.find('projDirNDVI').text
            else:
                projDirNDVI = ''
            if (project.find('srcDirNDVI'))!=None:
                srcDirNDVI= project.find('srcDirNDVI').text
            else:
                srcDirNDVI = ''
            if (project.find('cache_dir'))!=None:
                cache_dir = os.path.join(projDir, 'VisusSlamFiles')
            else:
                 cache_dir = ''
            if project.find('createdAt')!=None:
                mydt = project.find('createdAt').text
                myformat = "%Y%m%d_%H%M%S"
                createdAt = datetime.strptime(mydt,myformat).strftime('%m/%d/%y')

            else:
                 createdAt = ''
            if project.find('updatedAt')!=None:
                mydt = project.find('updatedAt').text
                myformat = "%Y%m%d_%H%M%S"
                updatedAt = datetime.strptime(mydt, myformat).strftime('%m/%d/%y')
                # updatedAt = datetime.fromtimestamp(int(project.find('updatedAt').text)).strftime("%Y%m%d_%H%M%S")
            else:
                 updatedAt =''
            if project.find('sensor') != None:
                sensor = project.find('sensor').text
            else:
                sensor = 'Unknown'

            vProj = VisoarProject()
            vProj.update(projName, projDir, cache_dir, srcDir,createdAt,updatedAt,projDirNDVI, srcDirNDVI, sensorMode = sensor)
            self.projects.append(vProj)


    def isUniqueName(self, name):

        original = True
        tree = ET.ElementTree(file=self.userFileHistory)
        root = tree.getroot()
        for project in root.iterfind('project'):
            thisprojName = project.find('projName').text
            if name == thisprojName:
                original = False
        return original

    def getProjDirWithName(self, name):
        projectDir = ''
        tree = ET.ElementTree(file=self.userFileHistory)
        # print (tree.getroot())
        root = tree.getroot()
        for project in root.iterfind('project'):
            if (project.find('projName').text == name):
                projectDir = project.find('projDir').text
        return projectDir

    def changeDirectoryAllProjects(self, olddir, newdir):
        valid = False
        #'Select Old Directory'
            # Parse users history file, contains files they have loaded before
        tree = ET.ElementTree(file=self.userFileHistory)

        #Make backup

        now = datetime.now()
        date_time = now.strftime("_%Y%m%d_%H%M%S")
        if False:
            prefixFimename =   self.userFileHistory.replace('.xml','')
            tree.write(prefixFimename+date_time+'.xml')

        #print(tree.getroot())
        root = tree.getroot()

        print('will replace {0} with {1}'.format(olddir, newdir))
        if olddir and newdir:
            for project in root.iterfind('project'):
                projName = project.find('projName').text
                projDir = project.find('projDir')
                projDir.text =  projDir.text.replace(olddir, newdir)
                today = datetime.now()
                todayFormated = today.strftime("%Y%m%d_%H%M%S")
                foundUdpatedAt = project.find('updatedAt').text
                if foundUdpatedAt:
                    foundUdpatedAt.text = todayFormated

            # with open(self.userFileHistory+"_new", "w") as f:
                #indent(root)
            #tree.write(self.userFileHistory)
            # from xml.dom import minidom
            #
            # xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
            # with open(self.userFileHistory, "w") as f:
            #     f.write(xmlstr)
            pretty_print_xml_given_root(root, self.userFileHistory)
            valid= True
        self.refreshProjectsFromXML()
        return valid


    def changeDirectoryForAProject(self,olddir, newdir, oldName, newName):
        valid = False
        #'Select Old Directory'
            # Parse users history file, contains files they have loaded before
        tree = ET.ElementTree(file=self.userFileHistory)

        #Make backup
        now = datetime.now()
        date_time = now.strftime("_%Y%m%d_%H%M%S")
        if False:
            prefixFimename =   self.userFileHistory.replace('.xml','')
            tree.write(prefixFimename+date_time+'.xml')

        #print(tree.getroot())
        root = tree.getroot()

        print('will replace {0} with {1}'.format(olddir, newdir))
        if olddir and newdir:
            for project in root.iterfind('project'):
                foundprojName = project.find('projName')
                foundprojDir = project.find('projDir')
                today = datetime.now()
                todayFormated = today.strftime("%Y%m%d_%H%M%S")
                foundUdpatedAt = project.find('updatedAt')

                foundprojDir.text =  foundprojDir.text.replace(olddir, newdir)
                foundprojName.text =  foundprojName.text.replace(oldName, newName)
                if foundUdpatedAt:
                    foundUdpatedAt.text =  todayFormated

           # with open(self.userFileHistory+"_new", "w") as f:
                #indent(root)
            #tree.write(self.userFileHistory)
            # from xml.dom import minidom
            #
            # xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
            # with open(self.userFileHistory, "w") as f:
            #     f.write(xmlstr)
            pretty_print_xml_given_root(root, self.userFileHistory)
            valid =  True
        self.refreshProjectsFromXML()
        return valid

    def backup(self):
        # Make backup
        now = datetime.now()
        date_time = now.strftime("_%Y%m%d_%H%M%S")
        prefixFimename = self.userFileHistory.replace('.xml', '')

        tree = ET.ElementTree(file=self.userFileHistory)
        tree.write(prefixFimename + date_time + '.xml')

        #print('Backup library')

    def deleteXML(self, projName):
        valid = False
        print('INPUT: {0} '.format(projName))

        self.backup()
        tree = ET.ElementTree(file=self.userFileHistory)
        root = tree.getroot()
        for project in root.iterfind('project'):
            projNameI = project.find('projName').text
            # projDirI = project.find('projDir')
            print('{0}  ? {1}'.format(projNameI, projName))
            if projNameI == projName:
                print("{0} matches {1}, so it will be removed".format(projNameI, projName))
                root.remove(project)
                valid = True

        # from xml.dom import minidom
        #
        # xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        # with open(self.userFileHistory, "w") as f:
        #     f.write(xmlstr)
        pretty_print_xml_given_root(root, self.userFileHistory)

        self.refreshProjectsFromXML()
        return valid

        print('deleteXML done')


    def sortUserFileBy(self, whichFnt):
        def getkeyName(elem):
            return elem.findtext("projName")

        def getkeyCreatedAt(elem):
            return elem.findtext("createdAt")

        def getkeyUpdatedAt(elem):
            return elem.findtext("updatedAt")

        if False:
            self.backup()
        tree = ET.ElementTree(file=self.userFileHistory)
        #container = tree.find("data")

        root = tree.getroot()
        self.sortReversed = False

        if whichFnt == "Name (A-Z)":
            getkey = getkeyName
        elif whichFnt == "Recently Created":
            getkey = getkeyCreatedAt
            self.sortReversed = True
        elif whichFnt == "Recently Updated":
            getkey = getkeyUpdatedAt
            self.sortReversed = True
        if whichFnt == "Name (Z-A)":
            getkey = getkeyName
            self.sortReversed = True
        elif whichFnt == "Oldest Created":
            getkey = getkeyCreatedAt

        elif whichFnt == "Oldest Updated":
            getkey = getkeyUpdatedAt


        root[:] = sorted(root, key=getkey)

        # from xml.dom import minidom
        #
        # xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        # with open(self.userFileHistory, "w") as f:
        #     f.write(xmlstr)
        pretty_print_xml_given_root(root, self.userFileHistory)
        self.refreshProjectsFromXML()



    def indent(elem, level=0, more_sibs=False):
        i = "\n"
        if level:
            i += (level - 1) * '  '
        num_kids = len(elem)
        if num_kids:
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
                if level:
                    elem.text += '  '
            count = 0
            for kid in elem:
                self.indent(kid, level + 1, count < num_kids - 1)
                count += 1
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
                if more_sibs:
                    elem.tail += '  '
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
                if more_sibs:
                    elem.tail += '  '

    def saveUserFileHistory(self):
        tree = ET.ElementTree(file=self.userFileHistory)
        #print(tree.getroot())
        root = tree.getroot()

        tree = ET.ElementTree(root)
        with open("updated.xml", "w") as f:
            self.indent(root)
            tree.write(f)


    def loadExisitingProject(self, projName):
        tree = ET.ElementTree(file=self.userFileHistory)
        # print (tree.getroot())
        root = tree.getroot()
        projectInfo = VisoarProject()
        for project in root.iterfind('project'):
            if (project.find('projName').text == projName):
                projectInfo.projName = project.find('projName').text
                projectInfo.projDir = project.find('projDir').text
                projectInfo.srcDir = project.find('srcDir').text
                projectInfo.projDirNDVI = project.find('projDirNDVI').text
                projectInfo.srcDirNDVI = project.find('srcDirNDVI').text
                projectInfo.cache_dir = os.path.join(projectInfo.projDir, 'VisusSlamFiles')
                projectInfo.createdAt = project.find('createdAt').text
                if project.find('sensor') != None:
                    projectInfo.sensor = project.find('sensor').text

                today = datetime.now()
                todayFormated = today.strftime("%Y%m%d_%H%M%S")
                #projectInfo.updatedAt = project.find('updatedAt').text
                projectInfo.updatedAt = todayFormated

                #print(projectDir)
                return True, projectInfo
                #print('Need to run visus viewer with projDir + /VisusSlamFiles/visus.midx')

        # from xml.dom import minidom
        #
        # xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        # with open(self.userFileHistory, "w") as f:
        #     f.write(xmlstr)
        pretty_print_xml_given_root(root, self.userFileHistory)
        return False, ''


    def fixDatesProject(self ):
        tree = ET.ElementTree(file=self.userFileHistory)
        # print (tree.getroot())
        root = tree.getroot()
        for project in root.iterfind('project'):
            #if (project.find('projName').text == projName):
            projectDir = project.find('projDir').text

            if project.find('createdAt') == None:
                file = os.path.join(projectDir, 'VisusSlamFiles')
                if os.path.exists(file):
                    createdAtString = datetime.fromtimestamp(os.path.getctime(file)).strftime("%Y%m%d_%H%M%S")
                else:
                    createdAtString = ''
                createdAtElement = ET.SubElement(project, 'createdAt')
                createdAtElement.text = createdAtString

            if project.find('updatedAt')==None:
                file = os.path.join(projectDir, 'VisusSlamFiles')
                if os.path.exists(file):
                    updatedAtString = datetime.fromtimestamp(os.path.getmtime(file)).strftime("%Y%m%d_%H%M%S")
                else:
                    updatedAtString = ''
                updatedAtElement = ET.SubElement(project, 'updatedAt')
                updatedAtElement.text = updatedAtString

        # from xml.dom import minidom
        #
        # xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        # with open(self.userFileHistory, "w") as f:
        #     f.write(xmlstr)
        pretty_print_xml_given_root(root, self.userFileHistory)
        return False, ''
