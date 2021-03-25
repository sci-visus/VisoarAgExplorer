import sys, os
import time

import importlib
visus_gui_spec = importlib.util.find_spec("OpenVisus.VisusGuiPy")

if visus_gui_spec is not None:
    from PyQt5 import Qt,QtCore,QtGui,QtWidgets
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *

    try:
        from PyQt5 import sip as  sip
    except ImportError:
        import sip

from slampy.image_utils import *

# ///////////////////////////////////////////////////////////////
def ProcessQtEvents():
	QApplication.instance().processEvents()

# ///////////////////////////////////////////////////////////////////////////////////////
class ProgressLine(QHBoxLayout):
	
	# constructor
	def __init__(self):
		super(ProgressLine, self).__init__()
		self.message=QLabel()
		self.bar=QProgressBar()
		self.addWidget(self.message)
		self.addWidget(self.bar)
		self.hide()

	# show
	def show(self):
		self.bar.show()
		self.message.show()
		ProcessQtEvents()

	# hide
	def hide(self):
		self.bar.hide()
		self.message.hide()
		ProcessQtEvents()

	# setRange
	def setRange(self,min,max):
		self.bar.setMinimum(min)
		self.bar.setMaximum(max)
		self.bar.setValue(min)
		ProcessQtEvents()

	# setMessage
	def setMessage(self,msg):
		print(msg)
		self.message.setText(msg)
		ProcessQtEvents()

	# value
	def value(self):
		return self.bar.value()
		
	# setValue
	def setValue(self,value):
		value=max(value,self.bar.minimum())
		value=min(value,self.bar.maximum())
		self.bar.setValue(value)
		ProcessQtEvents()	

__splash__=None
			
# ////////////////////////////////////////////////////////////////////////////////////////////
def ShowSplash():
	global __splash__
	if __splash__: return
	filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/images/visoar.png')
	if not os.path.isfile(filename): raise Exception('internal error')
	img = QPixmap(filename)
	__splash__ = QSplashScreen(img)
	__splash__.setWindowFlags(QtCore.Qt.FramelessWindowHint) # QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
	__splash__.setEnabled(False)
	__splash__.show()
	__splash__.showMessage("<h1><font color='green'>Welcome</font></h1>", QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter, QtCore.Qt.black)	

# ////////////////////////////////////////////////////////////////////////////////////////////
def HideSplash():
	global __splash__
	if not __splash__: return
	__splash__.close()
	__splash__=None

# ////////////////////////////////////////////////////////////////////////////////////////////
class PreviewImage(QWidget):

	# constructor
	def __init__(self,max_size=1024):
		super(PreviewImage,self).__init__()
		self.label = QLabel(self)
		self.max_size=max_size

	# showPreview
	def showPreview(self,img,title):
		img=ResizeImage(img,self.max_size)

		img=img[:,:,0:3]
		H,W,nchannels=img.shape[0:3]

		if nchannels==1:
			qimage = QtGui.QImage(img, W,H, nchannels * W, QtGui.QImage.Format_Grayscale8)
		elif nchannels==2:
			R,G=img[:,:,0], img[:,:,1] 
			img=InterleaveChannels(R,G,G)
			qimage = QtGui.QImage(img, W,H, nchannels * W, QtGui.QImage.Format_RGB888)
		else:
			qimage = QtGui.QImage(img, W,H, nchannels * W, QtGui.QImage.Format_RGB888)

		pixmap = QPixmap(qimage)
		self.label.setPixmap(pixmap)
		self.resize(pixmap.width(),pixmap.height())
		self.setWindowTitle(title)
		self.show()
