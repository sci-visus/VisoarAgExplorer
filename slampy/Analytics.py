
import os
import numpy 

import cv2
import cmapy   
import matplotlib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot 

from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from slampy.image_utils import *

# //////////////////////////////////////////////////////////////////////
def CreateColorMap(colors, position=None, bit=False):
	"""
	NDVI: calculates range -1 to 1
	water/rocks: [-1, -.5]
	healthy plants [0.2, 1]
	This is not a great way to make color maps, we probably want to be able to control where the colors are... 
	this does linear spread and linear blend    
	
	http://schubert.atmos.colostate.edu/~cslocum/custom_cmap.html#code
	CreateColorMap takes a list of tuples which contain RGB values. The RGB
	values may either be in 8-bit [0 to 255] (in which bit must be set to
	True when called) or arithmetic [0 to 1] (default). CreateColorMap returns
	a cmap with equally spaced colors.
	Arrange your tuples so that the first color is the lowest value for the
	colorbar and the last is the highest.
	position contains values from 0 to 1 to dictate the location of each color.
	"""
	bit_rgb = numpy.linspace(0,1,256)
	
	if position is None:
		position = numpy.linspace(0,1,len(colors))
	  
	if len(position) != len(colors):
		raise Exception("position length must be the same as colors")
		
	if position[0] != 0 or position[-1] != 1:
		raise Exception("position must start with 0 and end with 1")
            
	if bit:
		for i in range(len(colors)):
			colors[i] = (bit_rgb[colors[i][0]],bit_rgb[colors[i][1]],bit_rgb[colors[i][2]])
            
	red,green,blue = [],[],[]
    	
	for pos, color in zip(position, colors):
		red  .append((pos, color[0], color[0]))
		green.append((pos, color[1], color[1]))
		blue .append((pos, color[2], color[2]))

	return matplotlib.colors.LinearSegmentedColormap('my_colormap',{'red':red, 'green':green, 'blue':blue},256)



# //////////////////////////////////////////////////////////////////////
def Div0(a,b):
	""" 
	Divide a by b and watch out for zeros;  ignore / 0, div0( [-1, 0, 1], 0 ) -> [0, 0, 0] 
	"""
	with numpy.errstate(divide='ignore', invalid='ignore'):
		c = numpy.true_divide( a, b )
		c[ ~ numpy.isfinite( c )] = 0  # -inf inf NaN
	return c

# //////////////////////////////////////////////////////////////////////
def Normalize(data):
	return cv2.normalize(data , None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  #  normalize data [0,1]

# //////////////////////////////////////////////////////////////////////
def LoadFloatImage(filename):
	ret = cv2.imread(filename, 0) # load grayscale
	if ret.dtype =='uint8': ret =numpy.float32(ret)
	return ret


# //////////////////////////////////////////////////////////////////////////////////
class GuiUtils:
		
	# creteTextButton
	@staticmethod
	def creteTextButton(text,callback):	
		ret = QPushButton(text)
		ret.clicked.connect(callback)		
		return ret
		
	# horizontalLayout
	@staticmethod
	def horizontalLayout(*widgets):
		ret=QHBoxLayout()
		for it in widgets: 
			try:
				ret.addWidget(it) 
			except:
				try:
					ret.addLayout(it)	
				except:
					ret.addItem(it)
		return ret			
		
	# verticalLayout
	@staticmethod
	def verticalLayout(*widgets):
		ret=QVBoxLayout()
		for it in widgets: 
			try:
				ret.addWidget(it) 
			except:
				try:
					ret.addLayout(it)	
				except:
					ret.addItem(it)
		return ret				

		
	# createExpandingSpacer
	@staticmethod
	def createExpandingSpacer():
		ret = QWidget()
		ret.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)		
		return ret
		
	# toQtImage
	def toQtImage(img):
		
		if img is None:
			return QImage()
			
		if img.dtype!=numpy.uint8:
			raise Exception("error here")
			
		W,H=img.shape[1], img.shape[0]
		bytes_per_line=img.strides[0]

		if len(img.shape) == 2:
			ret = QImage(img.data, W, H, bytes_per_line, QImage.Format_Indexed8)
			ret.setColorTable([qRgb(i, i, i) for i in range(256)])
			return ret
		
		if len(img.shape) == 3:
			
			if img.shape[2] == 3:
				return QImage(img.data, W, H, bytes_per_line,QImage.Format_RGB888)
				
			if img.shape[2] == 4:
				return QImage(img.data, W, H, bytes_per_line, QImage.Format_ARGB32)
		

		raise Exception("error here")


# ////////////////////////////////////////////////////////////////////////////////// 
class AnalitycsWindow(QMainWindow):
	
	# init
	def __init__(self):
		super().__init__()
		self.createGui()
		self.channels={}
		self.channels["red"]   = LoadFloatImage(os.path.join(os.path.abspath(__file__),"/resources/rededge-mx","red670nm.tif"))
		self.channels["blue"]  = LoadFloatImage(os.path.join(os.path.abspath(__file__),"/resources/rededge-mx","blue475nm.tif"))
		self.channels["green"] = LoadFloatImage(os.path.join(os.path.abspath(__file__),"/resources/rededge-mx","green560nm.tif"))
		self.channels["re"]    = LoadFloatImage(os.path.join(os.path.abspath(__file__),"/resources/rededge-mx","rededge720nm.tif"))
		self.channels["nir"]   = LoadFloatImage(os.path.join(os.path.abspath(__file__),"/resources/rededge-mx","nir840nm.tif"))		
		self.setChannel("red")
		self.setColorBar(0)

	# setChannel
	def setChannel(self,value):
		value=value.lower()
		self.choose_channel.setCurrentText(value)
		
		if value=="rgb":
			img = cv2.merge([
				numpy.uint8(self.channels["red"  ] * 255),
				numpy.uint8(self.channels["green"] * 255),
				numpy.uint8(self.channels["blue" ] * 255)])	
		else:
			img=self.channels[value]
			img = numpy.uint8(img *255)
		
		pixmap = QPixmap(GuiUtils.toQtImage(img))
		pixmap = pixmap.scaled(512,512, Qt.KeepAspectRatio, Qt.FastTransformation)
		self.show_channel.setPixmap(pixmap)		
		
	# setColorBar
	def setColorBar(self,index):
		# todo
		# self.choose_colormap.setCurrentIndex(index)
			
		# Create a color map 
		# colors = ['#28ea2d', '#f9f837', '#f84e26', '#f61cb1', '#1b23f6', '#272727']
		# colors = [(255,0,0), (255,255,0), (255,255,255), (0,157,0), (0,0,255)] # This example uses the 8-bit RGB
		
		# Backwards:
		# colors = [(40,236,45), (78,198,35), (222,222,47), (249,158,39), (248,39,70), (246,28,178), (153,37,247), (8,31,222), (0,0,0)] # green to #yellow to red to purple to black 
		# colors = [(40,236,45), (78,198,35), (222,222,47), (249,158,39), (248,39,70) , (246,28,178)] # green to red to purple
		# colors = [ (0,102,51),(0,102,51), (169,169,34), (127,6,6), (77,32,127), (4,39,255) ] #  reversed and truncated
		
		# Extended palette
		# colors = [ (0,0,0), (8,31,222), (153,37,247), (246,28,178), (248,39,70), (249,158,39), (222,222,47), (78,198,35),(40,236,45)] 
		# colors = [ (246,28,178), (248,39,70), (249,158,39), (222,222,47), (78,198,35),(40,236,45)] #  truncated
		
		colors = [(4,39,255),(77,32,127), (127,6,6), (169,169,34), (0,102,51), (0,102,51) ] 
		self.colormap =  CreateColorMap(colors, bit=True)		
		

	# createGui
	def createGui(self):
		
		self.setWindowTitle('ViSOAR Ag Explorer Analytics Prototype')

		# toolbar
		self.toolbar = QToolBar()
		self.toolbar.setToolButtonStyle( Qt.ToolButtonTextUnderIcon)
		self.toolbar.setIconSize(QSize(100, 100))	
		self.addToolBar(self.toolbar)		

		# choose channel
		self.choose_channel = QComboBox()
		self.choose_channel.addItems(["red","green","blue", "nir", "re", "rgb"])
		self.choose_channel.currentIndexChanged.connect(lambda: self.setChannel(self.choose_channel.currentText()))	
		
		# choose colorbar
		self.choose_colormap = QComboBox()
		self.choose_colormap.setIconSize(QSize(400,100))
		self.choose_colormap.addItem(QIcon(os.path.join(os.path.abspath(__file__),'resources/images','colorbar_brg.png')) , "Colormap 1")
		self.choose_colormap.addItem(QIcon(os.path.join(os.path.abspath(__file__),'resources/images','colorbar_ryg.png')) , "Colormap 2")
		self.choose_colormap.setEditable(False) 	
		self.choose_colormap.setObjectName("Colormap") 
		self.choose_colormap.setIconSize(QSize(400,100))
		self.choose_colormap.currentIndexChanged.connect(lambda: self.setColorBar(self.choose_colormap.currentIndex()))	
		
		# quit button
		self.quit = QAction("&Quit", self)
		self.quit.setShortcut("Ctrl+Q")
		self.quit.setStatusTip('Leave The App')
		self.quit.triggered.connect(self.closeApplication)		
		self.toolbar.addAction(self.quit)
		
		# status bar
		self.statusbar = QStatusBar()
		self.setStatusBar(self.statusbar)		
		self.show_message   = QLabel("")
		self.statusbar.addWidget(self.show_message)
		
		# show_channel
		self.show_channel = QLabel()
		
		# show_analytics
		self.show_analytics = QLabel()

		# buttons (TODO: need to compute stuff)
		class Buttons:  pass
		self.buttons=[]
		
		
		self.buttons.append(GuiUtils.creteTextButton('ndvi'  , lambda: self.computeAnalitycs('ndvi' ,"Div0((nir  - red  ) , (nir + red  ))")))
		self.buttons.append(GuiUtils.creteTextButton('gndvi' , lambda: self.computeAnalitycs('gndvi',"Div0((nir  - green) , (nir + green))")))
		self.buttons.append(GuiUtils.creteTextButton('bndvi' , lambda: self.computeAnalitycs('bndvi',"Div0((nir  - blue ) , (nir + blue ))")))
		self.buttons.append(GuiUtils.creteTextButton('ndre'  , lambda: self.computeAnalitycs('ndre' ,"Div0((nir  - re   ) , (nir + re   ))")))
		self.buttons.append(GuiUtils.creteTextButton('lci'   , lambda: self.computeAnalitycs('lci'  ,"Div0((nir  - re   ) , (nir + red  ))")))
		self.buttons.append(GuiUtils.creteTextButton('vari'  , lambda: self.computeAnalitycs('vari' ,"Div0((green - red ) , (green + red + blue))")))
		self.buttons.append(GuiUtils.creteTextButton('tgi'   , lambda: self.computeAnalitycs('tgi'  ,"1.0* green - 0.39 * red - 0.61 * blue")))
		
		main_layout=GuiUtils.verticalLayout()
		main_layout.addLayout(GuiUtils.horizontalLayout(self.choose_channel))
		main_layout.addLayout(GuiUtils.horizontalLayout(self.show_channel,self.show_analytics))
		main_layout.addLayout(GuiUtils.horizontalLayout(self.choose_colormap))
		main_layout.addLayout(GuiUtils.horizontalLayout(*self.buttons))
		
		central_widget = QFrame()
		central_widget.setLayout(main_layout)
		central_widget.setFrameShape(QFrame.NoFrame)
		self.setCentralWidget(central_widget)
		self.show()		

	# closeApplication
	def closeApplication(self):
		app.quit()
		
	# computeAnalitycs
	def computeAnalitycs(self,algorithm,expression):
		
		red   = self.channels["red"]   
		blue  = self.channels["blue"] 
		green = self.channels["green"]
		re    = self.channels["re"]   
		nir   = self.channels["nir"]
		
		img=Normalize(eval(expression))
		
		# todo: apply colormap
		#img = cv2.cvtColor(numpy.float32(data), cv2.COLOR_GRAY2BGR)  
		#img = cmapy.colorize(img,self.colormap) 		
		
		img = GuiUtils.toQtImage(numpy.uint8(img *255))
		pixmap=QPixmap.fromImage(img.scaled(512,512, Qt.KeepAspectRatio, Qt.FastTransformation))
		self.show_analytics.setPixmap(pixmap)
		
		msg="Showing Channel({}) Analytics({})".format(self.choose_channel.currentText(),algorithm)
		
		self.show_message.setText(msg)
		self.repaint()		
			
	

# //////////////////////////////////////////////////////////////////////
def Main():
	app = QApplication([])
	QFontDatabase.addApplicationFont(os.path.join(os.path.abspath(__file__),"resources/fonts","Roboto-Regular.ttf"))
	
	font = QFont("Roboto")
	font.setStyleHint(QFont.Monospace)
	font.setPointSize(16)
	app.setFont(font)

	window = AnalitycsWindow()
	window.show()
	app.exit(app.exec_())


# //////////////////////////////////////////////////////////////////////
if __name__  == '__main__' :
	Main()
	
	
	
	