import sys, os
from VisoarSettings 		import *
from PyQt5.QtGui 					  import QFont, QColor, QPainter, QPen, QIcon, QBrush
from PyQt5.QtCore                     import QUrl, Qt, QSize, QDir, QRect
from PyQt5.QtWidgets                  import QApplication, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtWidgets                  import QMainWindow, QPushButton, QVBoxLayout,QSplashScreen,QProxyStyle, QStyle, QAbstractButton
from PyQt5.QtWidgets                  import QWidget, QMessageBox, QGroupBox, QShortcut,QSizePolicy,QPlainTextEdit,QDialog, QFileDialog
from PyQt5.QtGui import  QPalette, QColor
from PyQt5.QtCore import Qt

#Color Scheme:  https://www.colorhexa.com/045951
visoarGreen = '#045951'   #4,89,81
visoarRed = '#59040c'
visoarBlue = '#043759'
visoarLightGreen = '#067f73'
visoarDarkGreen = '#02332f'  #2,51,47
visoarGreenWebSafe = '#006666'
visoarHighlightYellow = '#d6d2b1' #214,210,177
GRID_SPACING = 10


if sys.platform.startswith('win'):
    V_BUTTON_SIZE = 120
    V_BUTTON_SIZE_SM = 80
    V_THUMBNAIL_SIZE = 160
    V_SWITCH_W_SIZE = 140
    V_SWITCH_H_SIZE = 44
    V_LIST_LABLES = 320
    V_LIST_DATES = 240
    PROJ_BUTTON_HEIGHT = 140*2
    PROJ_BUTTON_WIDTH = 240*2
    NAME_BUTTON_HEIGHT = 50*2
    NAME_BUTTON_WIDTH = 240*2
    ICON_BUTTON_HEIGHT = 180*2
    ICON_BUTTON_WIDTH = 180*2

else:
    V_BUTTON_SIZE = 60
    V_BUTTON_SIZE_SM = 40
    V_THUMBNAIL_SIZE = 80
    V_SWITCH_W_SIZE = 70
    V_SWITCH_H_SIZE = 22
    V_LIST_LABLES = 160
    V_LIST_DATES = 120
    PROJ_BUTTON_HEIGHT = 140
    PROJ_BUTTON_WIDTH = 240
    NAME_BUTTON_HEIGHT = 50
    NAME_BUTTON_WIDTH = 240
    DATE_BUTTON_WIDTH = 60
    ICON_BUTTON_HEIGHT = 180
    ICON_BUTTON_WIDTH = 180



class MySwitch(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        print('init')
        self.setCheckable(True)
        self.resize(V_SWITCH_W_SIZE, V_SWITCH_H_SIZE)
        self.setFixedSize(V_SWITCH_W_SIZE, V_SWITCH_H_SIZE)
        self.setMinimumWidth(V_SWITCH_W_SIZE)  #66
        self.setMinimumHeight(V_SWITCH_H_SIZE) #22
        self.setGeometry(0,0,V_SWITCH_W_SIZE,V_SWITCH_H_SIZE)

    def paintEvent(self, event):
        label = "ON" if self.isChecked() else "OFF"
        bg_color = QColor('#045951')  if self.isChecked() else Qt.white
        fg_color =  Qt.white  if self.isChecked() else Qt.black
        radius = 10
        width = (V_SWITCH_W_SIZE-4)/2
        center = self.rect().center()

        painter =  QPainter(self)
        painter.setRenderHint( QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush( QColor(0,0,0))

        pen =  QPen(fg_color)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2*width, 2*radius), radius, radius)
        painter.setBrush( QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2*radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignCenter, label)


def getTextFromScript(scriptFile):
	data = ''
	with open(scriptFile, 'r') as myfile:
		data = myfile.read()
		myfile.close()
	print('getTextFromScript ({0} ) '.format(scriptFile))
	print(data)
	#return "\""+data+"\"".strip()
	return  data.strip()+'\n'


def popUP( title, text):
	msg = QMessageBox()
	# msg = QMessageBox.about(self, title, text)
	msg.setWindowTitle(title)
	msg.setText(text)
	msg.setStyleSheet(POPUP_LOOK_AND_FEEL)
	# msg.setIcon(QMessageBox.Information)
	# msg.setStandardButtons(QMessageBox.Retry | QMessageBox.Ignore | QMessageBox.Cancel)
	# msg.setDefaultButton(QMessageBox.Ignore)
	# msg.buttonClicked.connect(self.popup_clicked)
	# if details  :
	#	msg.setDetailedText(details)
	x = msg.exec_()
	msg.raise_()
	msg.activateWindow()

def createPushButton(text,callback=None, img=None ):
	ret=QPushButton(text)
	#ret.setStyleSheet("QPushButton{background: transparent;}");
	ret.setAutoDefault(False)
	if callback:
		ret.clicked.connect(callback)
	if img:
		ret.setIcon(QIcon(img))
		ret.setIconSize(QSize(V_THUMBNAIL_SIZE, V_THUMBNAIL_SIZE))
	if DEBUG:
		print('createPushButton finished')
	return ret

# self.visusGoogleAuth = VisusGoogleWebAutho(self)
def fixButtonsLookFeel( btn):
	btn.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)
	btn.setIconSize(QSize(V_BUTTON_SIZE, V_BUTTON_SIZE))
	btn.resize(V_BUTTON_SIZE, V_BUTTON_SIZE)
	btn.setFixedSize(V_BUTTON_SIZE, V_BUTTON_SIZE)

def fixButtonsLookFeelGreen( btn):
	btn.setStyleSheet(GREEN_BACKGROUND_PUSH_BUTTON)
	btn.setIconSize(QSize(V_BUTTON_SIZE, V_BUTTON_SIZE))
	btn.resize(V_BUTTON_SIZE, V_BUTTON_SIZE)
	btn.setFixedSize(V_BUTTON_SIZE, V_BUTTON_SIZE)

def recursive_copy_files(source_path, destination_path, override=False):
    print('Copy from: {0} to: {1}'.format(source_path, destination_path))
    return
    """
    Recursive copies files from source  to destination directory.
    :param source_path: source directory
    :param destination_path: destination directory
    :param override if True all files will be overridden otherwise skip if file exist
    :return: count of copied files
    """
    import shutil
    files_count = 0
    if not os.path.exists(destination_path):
        os.mkdir(destination_path)
    items = glob.glob(source_path + '/*')
    for item in items:
        if os.path.isdir(item):
            path = os.path.join(destination_path, item.split('/')[-1])
            files_count += recursive_copy_files(source_path=item, destination_path=path, override=override)
        else:
            file = os.path.join(destination_path, item.split('/')[-1])
            if not os.path.exists(file) or override:
                shutil.copyfile(item, file)
                files_count += 1
    return files_count



LOOK_AND_FEEL = """
		font-family: Roboto;font-style: normal;font-size: 14pt; 
		background-color: #ffffff;
		color: #7A7A7A;
		padding: 15px 15px 15px 15px; 
		selection-background-color: rgb(168,168,168);
		QTabBar::tab:selected {
			background: #045951
		}
		QMainWindow {
			#background-color: #7A7A7A;
			#color: #ffffff;
			background-color: #ffffff;
			color: #7A7A7A
			
			}
			QLabel {
			background-color: #7A7A7A;
			color: #ffffff
			}
		QToolTip {
			border: 1px solid #76797C;
			border-radius: 20px;
			background-color: rgb(90, 102, 117);
			color: white;
			padding: 5px 5px 5px 5px;
			opacity: 200
		}
		QLabel {
			font: 20pt Roboto
		}
		QPushButton {
			border-radius: 7;
			border-style: outset; 
			border-width: 0px;
			color: #ffffff;
			background-color: #045951;
			padding: 10px 10px 10px 10px;
			margin: 5px 5px 5px 5px;
		}
		QPushButton:pressed { 
			background-color:  #e6e6e6;
			border-radius:5px; 
			border : 3px solid #d6d2b1
		}
		QLineEdit { background-color: #e6e6e6; border-color: #045951 }
        QPushButton::clicked
        {
            border-radius:5px; 
            border : 3px solid #d6d2b1
        }
    QDialog{
        background-color:  #FFFFFF;
    	border: 2px solid #045951;
		border-radius: 6px;
		width : 800;
    }
    QInputDialog {background-color: red;} 
    QWidget
		{
    	border: 0px solid #999900;
    	background-color: #045951;
    	color: white
	}
QMessageBox {
    background-color: #ffffff;
}

QMessageBox QLabel {
    color: #045951;
    background-color: #ffffff;
}

QRadioButton {
    background-color:       gray;
    color:                  white;
}

QRadioButton::indicator {
    width:                  10px;
    height:                 10px;
    border-radius:          7px;
}

QRadioButton::indicator:checked {
    background-color:       #045951;
    border:                 2px solid white;
}

QRadioButton::indicator:unchecked {
    background-color:       black;
    border:                 2px solid white;
}

QCheckBox {
    background-color:       #045951;
    color:                  white;
    border:                 2px solid #045951;
}

QCheckBox::indicator {
    width:                  10px;
    height:                 10px;
    border-radius:          7px;
}

QCheckBox::indicator:checked {
    background-color:       #045951;
    border:                 2px solid #045951;
}

QCheckBox::indicator:unchecked {
    background-color:       black;
    border:                 2px solid #045951;
} 
""".strip()


QCHECKBOX_LOOK_AND_FEEL = """
QCheckBox {
    background-color:       white;
    color:                  #045951;
    
}

QCheckBox::indicator {
    width:                  15px;
    height:                 15px;
    border-radius:          5px;
    color:                  white;
}

QCheckBox::indicator:checked {
    background-color:       #045951;
    border:                 2px solid #045951;
}

QCheckBox::indicator:hover
{
background-color : #067f73;
}
QCheckBox::indicator:unchecked {
    background-color:       white;
    border:                 2px solid #045951;
}
""".strip()

QCHECKBOX_LOOK_AND_FEEL_OLD = """
        QCheckBox::indicator {
            border: 3px solid #045951;
        } 
        
QCheckBox::indicator:unchecked {
    image: url(:./icons/unchecked.png);
}

QCheckBox::indicator:unchecked:hover {
    image: url(:./icons/unchecked.png);
}

QCheckBox::indicator:unchecked:pressed {
    image: url(:./icons/unchecked.png);
}

QCheckBox::indicator:checked {
    image: url(:./icons/checked.png);
}

QCheckBox::indicator:checked:hover {
    image: url(:./icons/checked.png);
}

QCheckBox::indicator:checked:pressed {
    image: url(:./icons/checked.png);
}

QCheckBox::indicator:indeterminate:hover {
    image: url(:./icons/unchecked.png);
}

QCheckBox::indicator:indeterminate:pressed {
    image: url(:./icons/unchecked.png);
}
       
""".strip()

QGROUPBOX_LOOK_AND_FEEL= """
		QGroupBox {
			font: bold;
			background-color:  #FFFFFF;
			border: 2px solid #045951;
			border-radius: 6px;
			margin-top: 10px; /* leave space at the top for the title */
			margin-left: 140px;
			margin-right:140px;
			min-height:350px;
		}
		QGroupBox::title { 
			subcontrol-origin: margin;
			background-color: #ffffff;
			#subcontrol-position: top left; /* position at the top left*/ 
			#padding:2 13px;
			color: #045951;
			#left: 7px;
    		padding: 0px 5px 10px 5px;
		} 

""".strip()



 

PROGRESSBAR_LOOK_AND_FEEL = """
QProgressBar {
    border: 2px solid 02332f;
    border-radius: 5px;
    text-align: center
}

QProgressBar::chunk {
    background-color: #045951;
    width: 20px;
}
	""".strip()

POPUP_LOOK_AND_FEEL = """
font-family: Roboto;
font-style: normal;
font-size: 14pt; 
background-color: #ffffff; 
color: #045951;
QMessageBox QLabel {
    color: #045951;
    background-color: white; 
}
QMessageBox QPushButton {
    max-width:300px;
    border-radius: 7;
    border-style: outset; 
    border-width: 1px;
    color: #045951;
    background-color: #ffffff; 
    padding: 10px 10px 10px 10px;
}
QMessageBox::question QLabel,
QMessageBox::warning QLabel,
QMessageBox::critical QLabel,
QMessageBox::Information QLabel{
    color: #045951;
}
QMessageBox::question,
QMessageBox::warning,
QMessageBox::critical,
QMessageBox::Information {
    color: #045951;
     background-color:white; 
}
QLabel {
    min-width:500 px;
    font: 20pt Roboto
}
QPushButton {
    width:250px;
    border-radius: 7;
    border-style: outset;
    border-width: 0px;
    color: #ffffff;
    background-color: #045951;
    padding: 10px 10px 10px 10px;
}
QPushButton:pressed {
    background-color:  #e6e6e6
}
QMainWindow {
    min-width:500 px;
    background-color: #ffffff;
    color: #045951
}
""".strip()

TAB_LOOK = """
			/* Style the tab using the tab sub-control. Note that
		it reads QTabBar _not_ QTabWidget */
		QTabBar::tab {
			background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
			stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
			stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
			border: 2px solid #C4C4C3;
			border-bottom-color: #C2C7CB; /* same as the pane color */
			border-top-left-radius: 4px;
			border-top-right-radius: 4px;
			min-width: 100px;
			padding: 12px 12px 12px 12px;
		}

		QTabBar::tab:selected {
			background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
			stop: 0 #045951, stop: 0.4 #045951,
			stop: 0.5 #034640, stop: 1.0 #045951);
			color: #ffffff
		}
		QTabBar::tab:hover  {
			background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
			stop: 0 #07a294, stop: 0.4 #07a294,
			stop: 0.5 #045951, stop: 1.0 #07a294);
			color: #ffffff
		}

		QTabBar::tab:selected {
			border-color: #9B9B9B;
			border-bottom-color: #C2C7CB /* same as pane color */
		}

		QTabBar::tab:!selected {
			margin-top: 2px /* make non-selected tabs look smaller */
		}""".strip()


GREEN_BACKGROUND_PUSH_BUTTON = """QPushButton {
			border-radius: 7;
			border-style: outset; 
			border-width: 0px;
			color: #ffffff;
			background-color: #045951;
			padding-left: 40px;
			padding-right: 40px;
			padding-top: 10px;
			padding-bottom: 10px;
			text-align:center
		}
		QPushButton:pressed { 
			background-color:  #e6e6e6

		}""".strip()


NOBACKGROUND_PUSH_BUTTON = """QPushButton {
			border-color: #ffffff;
			border-radius: 7;
			border-style: outset; 
			border-width: 0px;
			color: #ffffff;
			background-color: #ffffff;
			padding-left: 40px;
			padding-right: 40px;
			padding-top: 10px;
			padding-bottom: 10px;
			text-align:center;
		}
		QPushButton:pressed { 
			background-color:  #e6e6e6;
		}""".strip()

CLEARBACKGROUND_PUSH_BUTTON = """QPushButton {
			border-radius: 20;
			border-style: outset; 
			border-width: 0px;
			color: #ffffff;
			background-color: transparent;
			padding-left: 40px;
			padding-right: 40px;
			padding-top: 10px;
			padding-bottom: 10px;
			text-align:center
		}
		QPushButton:pressed { 
			background-color:  #e6e6e6

		}""".strip()


SEMICLEARBACKGROUND_PUSH_BUTTON = """QPushButton {
			border-radius: 20;
			border-style: outset; 
			border-width: 0px;
			color: #ffffff;
			background-color: rgba(255, 255, 255, 200);
			padding-left: 40px;
			padding-right: 40px;
			padding-top: 10px;
			padding-bottom: 10px;
			text-align:center
		}
		QPushButton:pressed { 
			background-color:  #e6e6e6

		}""".strip()

GREEN_PUSH_BUTTON = """QPushButton {
			min-width:300px;
			border-radius: 7;
			border-style: outset; 
			border-width: 0px;
			color: #ffffff;
			background-color: #045951;
			padding-left: 40px;
			padding-right: 40px;
			padding-top: 10px;
			padding-bottom: 10px;
			text-align:center
		}
		QPushButton:pressed { 
			background-color:  #e6e6e6

		}""".strip()


GRAY_PUSH_BUTTON = """QPushButton {
			max-width:300px;
			border-radius: 7;
			border-style: outset; 
			border-width: 0px;
			color: #045951;
			background-color: #e6e6e6;
			padding: 10px 10px 10px 10px;
		}
		QPushButton:pressed { 
			background-color:  #e6e6e6
		}""".strip()

WHITE_PUSH_BUTTON = """QPushButton {
		max-width:300px;
		border-radius: 7;
		border-style: outset; 
		border-width: 1px;
		color: #045951;
		background-color: #ffffff;
		padding: 10px 10px 10px 10px;
	}
	QPushButton:pressed { 
		background-color:  #e6e6e6
	}""".strip()

WHITE_TOOL_BUTTON = """QToolButton {
		max-width:300px;
		border-radius: 7;
		border-style: outset; 
		border-width: 1px;
		color: #045951;
		background-color: #ffffff;
		padding: 10px 10px 10px 10px;
	}
	QPushButton:pressed { 
		background-color:  #e6e6e6
	}""".strip()


DISABLED_PUSH_BUTTON = """QPushButton {
	max-width:300px;
	border-radius: 7;
	border-style: outset; 
	border-width: 0px;
	color: #ffffff;
	background-color: #e6e6e6;
	padding: 10px 10px 10px 10px;
}
QPushButton:pressed { 
	background-color:  #e6e6e6

}""".strip()


MY_COMBOX = """
QWidget:item:disabled
{
    color: grey;
    background-color: #045951;
}
QWidget:item:selected
{
    border: 1px solid #999999;
    background-color: #08a596;
    color: white
}
QFrame { 
    border: 2px solid #045951;  
    padding: 5px;
    margin: 5px;}
QWidget
{
    border: 0px solid #999900;
    background-color: white;
    color: #045951;
}
QWidget:item:checked
{
     font-weight: bold
}
QComboBox {
    border-radius: 3px;
    padding: 1px 10px 1px 3px;
    color: #045951;
    background-color: white;
    min-width:120px;
    min-height:30px;
    border : 2px  #045951;
    border-style : solid;
    padding: 5px;
    margin: 5px;
   }

""".strip()

MY_QTOOLBOX = """QToolBox {
    border-radius: 3px;
    padding: 1px 10px 1px 3px;
    color: #045951;
    background-color: white;
    min-width:120px;
    min-height:30px;
    border : 2px  #045951;
    border-style : solid;
    }
    """.strip()

OTHER_MY_COMBOX = """
QWidget:item:selected
{
    border: 1px solid #08a596;
    #background: transparent;
    color: white;
    background: #08a596
 
}
QWidget:item:checked
{
     font-weight: bold
}

QComboBox QAbstractItemView{
    background: white;
    color: #08a596;
  	selection-background-color: yellow; 
    selection-color: white

}

QCombobox:!editable
{
	background: white;
    color:#045951
}
QCombobox:editable
{
	background: white;
     color:#045951
}

QLabel {
	background: white;
 	color: #045951
 }
QListView
{
	background: white;
   	color: #045951
}
QListView::item
{
	background: white;
   	color: #045951
}

QLineEdit {  
 	background: white;
    color: #045951
 }

QComboBox {
    border: 1px solid gray;
    border-radius: 3px;
    padding: 1px 18px 1px 3px;
    background: #045951;
    color: white;
    selection-background-color: #045951;
    selection-color: white

}
QComboBox::hover
{
	background: white;
    color: #045951
}

QComboBox:on { /* shift the text when the popup opens */
    padding-top: 3px;
    padding-left: 4px;
    padding: 10px;
    #color: white;
    #selection-background-color: 
    color: #045951;
	background: white
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
	padding: 10px 10px 10px 10px;
    border-left-width: 1px;
    border-left-color: #045951;
    border-left-style: solid; /* just a single line */
    border-top-right-radius: 3px; /* same radius as the QComboBox */
    border-bottom-right-radius: 3px;
    background: white;
    color: #045951
}

QComboBox::drop-down:button{
	#background-color: #045951;
	#color:   #045951
}

QComboBox::down-arrow:on { /* shift the arrow when popup is open */
    top: 1px;
    left: 1px;
    color: white;
    #background: white;
    #color: #045951
}


""".strip()

MY_OUTPUT_LOOK= """
    background-color: #eeeeee;
    color: #000000
""".strip()

MY_SCROLL_LOOK = """
QScrollBar:horizontal
 {
     height: 15px;
     margin: 3px 15px 3px 15px;
     border: 1px transparent #2A2929;
     border-radius: 4px;
     background-color:   #045951; 
 }

 QScrollBar::handle:horizontal
 {
     background-color: white;      /* #605F5F; */
     min-width: 5px;
     border-radius: 4px;
 }
 
 QScrollBar:vertical
 {
     background-color: #045951;
     width: 15px;
     margin: 15px 3px 15px 3px;
     border: 1px transparent white;
     border-radius: 4px;
 }

 QScrollBar::handle:vertical
 {
     background-color: white;         /* #605F5F; */
     min-height: 5px;
     border-radius: 4px;
 }
 

 QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical
 {
     background: none;
 }


 QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical
 {
     background: none;
 }
""".strip()