import sys

#https://www.learnpyqt.com/widgets/gradient/
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtGui 					  import QFont,QPainter,QPen, QColor
from PyQt5.QtWidgets                  import QApplication,QVBoxLayout, QHBoxLayout, QLineEdit,QLabel, QLineEdit, QTextEdit, QGridLayout


class Gradient(QtWidgets.QWidget):

    gradientChanged = Signal()

    def __init__(self, gradient=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.BLANK_SPACE = 40
        self.MARGIN_SPACE = 20
        self.BGR = False
        self.mousex = 0
        self.mousey = 0
        self.setMouseTracking(True)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        if gradient:
            self._gradient = gradient

        else:
            self._gradient = [
                (0.0, '#000000'),
                (1.0, '#ffffff'),
            ]

        # Stop point handle sizes.
        self._handle_w = 20
        self._handle_h = 20

        self._drag_position = None
        self.text = f'x: {self.mousex},  y: {self.mousey}'

        # self.gLayout = QVBoxLayout()
        # self.label = QLabel(self.text, self)
        # self.gLayout.addWidget(self.label)
        # self.setLayout(self.gLayout)

    def getColors(self):
        nodes = []
        nodesStr = 'nodes =['
        colors = []
        colorStr = "cdict = ["
        for t in self._gradient:
            nodes.append(t[0])
            nodesStr = nodesStr+str(t[0])+','
            colors.append(t[1])
            aColor=  t[1]
            if type(aColor) == str:
                aColor = QColor(aColor)
            if aColor :
                if (self.BGR):
                    colorStr =colorStr +" ({0}, {1} ,{2}),".format(round(aColor.blue()/255.0,2),round(aColor.green()/255.0,2),round(aColor.red()/255.0,2))
                else:
                    colorStr =colorStr +" ({0}, {1} ,{2}),".format(round(aColor.red()/255.0,2),round(aColor.green()/255.0,2),round(aColor.blue()/255.0,2))
                #print(" ({0}, {1} ,{2}),".format(round(t[1].red(),2),round(t[1].green(),2),round(t[1].blue(),2)))
        colorStr = colorStr +"]"
        nodesStr = nodesStr +"]"
        print(colorStr)
        return nodes,nodesStr, colors, colorStr

    def makeNewScriptRGB(self):
        nodes,nodesStr,c1, colorstr = self.getColors()
        print(nodes)
        print(nodesStr)
        print(c1)
        print(colorstr)
        script = """
import cv2, numpy
import matplotlib  
img = input.astype(numpy.float32)
red = img[:, :, 0]
green = img[:, :, 1]
blue = img[:, :, 2]
scaleRed = (0.39 * red)
scaleBlue = (.61 * blue)
TGI = green - scaleRed - scaleBlue
TGI = (TGI+1.0)/2.0
#TGI = cv2.normalize(TGI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]

gray = numpy.float32(TGI)
"""
        scriptEnd = """
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, cdict)))
out = cmap(TGI)
#out = cmap(gray)
out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_BGR2RGB)
out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)
output = out.astype(numpy.float32)
""".strip()
        print(script + "\n"+colorstr+"\n"+ nodesStr+"\n" + scriptEnd)
        return script+ "\n"+ colorstr+"\n" + nodesStr+"\n" + scriptEnd

    def makeNewScriptAgrocam(self):
        nodes, nodesStr, c1, colorstr = self.getColors()
        print(colorstr)
        script = """
import cv2, numpy
import matplotlib  
img = input.astype(numpy.float32)
NIR = img[:, :, 0]
green = img[:, :, 1]
blue = img[:, :, 2]

NDVI_u = (NIR - blue)
NDVI_d = (NIR + blue)
NDVI_d[NDVI_d == 0] = 0.01
NDVI = NDVI_u / NDVI_d
gray = numpy.float32(NDVI)
"""
        scriptEnd = """
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)

cmap2 = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, cdict)))
#out = cmap2(NDVI)
out = cmap2(gray)
out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_BGR2RGB)
out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)
output = out.astype(numpy.float32)
""".strip()
        print(script + "\n"+colorstr + "\n" + nodesStr + "\n" + scriptEnd)
        return script + "\n"+colorstr + "\n" + nodesStr + "\n" + scriptEnd

    def makeNewScriptMAPIR(self):
            nodes, nodesStr, c1, colorstr = self.getColors()
            print(colorstr)
            script = """
import cv2, numpy
import matplotlib  
img = input.astype(numpy.float32)
orange = img[:, :, 0]
cyan = img[:, :, 1]
NIR = img[:, :, 2]

NDVI_u = (NIR - orange)
NDVI_d = (NIR + orange)
NDVI_d[NDVI_d == 0] = 0.01
NDVI = NDVI_u / NDVI_d
NDVI = cv2.normalize(NDVI, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)  # normalize data [0,1]
gray = numpy.float32(NDVI)
    """
            scriptEnd = """
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(name='my_colormap', colors=cdict, N=1000)

cmap2 = matplotlib.colors.LinearSegmentedColormap.from_list("mycmap", list(zip(nodes, cdict)))
#out = cmap2(NDVI)
out = cmap2(gray)
out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_BGR2RGB)
out = cv2.cvtColor(numpy.float32(out), cv2.COLOR_RGB2BGR)
output = out.astype(numpy.float32)
    """.strip()
            print(script + "\n"+colorstr + "\n" + nodesStr + "\n" + scriptEnd)
            return script + "\n"+colorstr + "\n" + nodesStr + "\n" + scriptEnd

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        width = painter.device().width()-(2*self.MARGIN_SPACE)
        height = painter.device().height()

        # Draw the linear horizontal gradient.
        gradient = QtGui.QLinearGradient(self.MARGIN_SPACE, 0, width, 0)
        for stop, color in self._gradient:
            gradient.setColorAt(stop, QtGui.QColor(color))



        rect = QtCore.QRect(self.MARGIN_SPACE, self.BLANK_SPACE, width, height)
        painter.fillRect(rect, gradient)

        pen = QtGui.QPen()

        y = painter.device().height() / 2


        # Draw the stop handles.
        for stop, _ in self._gradient:
            pen.setColor(QtGui.QColor('white'))
            painter.setPen(pen)
            xStart = (stop * width)+self.MARGIN_SPACE

            painter.drawLine(xStart, y - self._handle_h, xStart, y + self._handle_h)

            pen.setColor(QtGui.QColor('red'))
            painter.setPen(pen)

            rect = QtCore.QRect(
                xStart - self._handle_w/2,
                y - self._handle_h/2,
                self._handle_w,
                self._handle_h
            )
            painter.drawRect(rect)

            #Add tick marks to line
            painter.setBrush(Qt.black)
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
            painter.drawLine(xStart, 0, xStart, 20)

            #Add numbers
            painter.drawText(xStart-10, 30, "{:.2f}".format(stop))  # fifth option

        #draw line for numbers
        painter.setBrush(Qt.black)
        painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
        painter.drawLine(self.MARGIN_SPACE, 10, width+self.MARGIN_SPACE, 10)
        painter.drawText(width-100, height-20, "{0}, {1}".format(self.mousex,self.mousey))  # fifth option

        painter.end()

    def sizeHint(self):
        return QtCore.QSize(200, 50)

    def _sort_gradient(self):
        self._gradient = sorted(self._gradient, key=lambda g:g[0])

    def _constrain_gradient(self):
        self._gradient = [
            # Ensure values within valid range.
            (max(0.0, min(1.0, stop)), color)
            for stop, color in self._gradient
        ]

    def setGradient(self, gradient):
        assert all([0.0 <= stop <= 1.0 for stop, _ in gradient])
        self._gradient = gradient
        self._constrain_gradient()
        self._sort_gradient()
        self.gradientChanged.emit()

    def gradient(self):
        return self._gradient

    @property
    def _end_stops(self):
        return [0, len(self._gradient)-1]

    def addStop(self, stop, color=None):
        # Stop is a value 0...1, find the point to insert this stop
        # in the list.
        assert 0.0 <= stop <= 1.0

        for n, g in enumerate(self._gradient):
            if g[0] > stop:
                # Insert before this entry, with specified or next color.
                self._gradient.insert(n, (stop, color or g[1]))
                break
        self._constrain_gradient()
        self.gradientChanged.emit()
        self.update()

    def removeStopAtPosition(self, n):
        if n not in self._end_stops:
            del self._gradient[n]
            self.gradientChanged.emit()
            self.update()

    def setColorAtPosition(self, n, color):
        if n < len(self._gradient):
            stop, _ = self._gradient[n]
            self._gradient[n] = stop, color
            self.gradientChanged.emit()
            self.show()
            self.update()

    def chooseColorAtPosition(self, n, current_color=None):
        dlg = QtWidgets.QColorDialog(self)
        if current_color:
            dlg.setCurrentColor(QtGui.QColor(current_color))

        if dlg.exec_():
            self.setColorAtPosition(n, dlg.currentColor().name())

    def _find_stop_handle_for_event(self, e, to_exclude=None):
        width = self.width() -( self.MARGIN_SPACE/2)
        height = self.height()
        midpoint = height / 2

        # Are we inside a stop point? First check y.
        if (
            e.y() >= midpoint - self._handle_h and
            e.y() <= midpoint + self._handle_h
        ):

            for n, (stop, color) in enumerate(self._gradient):
                if to_exclude and n in to_exclude:
                    # Allow us to skip the extreme ends of the gradient.
                    continue
                if (
                    e.x() >= stop * width - self._handle_w and
                    e.x() <= stop * width + self._handle_w
                ):
                    return n

    def mousePressEvent(self, e):
        self.mousex = e.x()
        self.mousey = e.y()
        # We're in this stop point.
        if e.button() == Qt.RightButton:
            n = self._find_stop_handle_for_event(e)
            if n is not None:
                _, color = self._gradient[n]
                self.chooseColorAtPosition(n, color)

        elif e.button() == Qt.LeftButton:
            n = self._find_stop_handle_for_event(e, to_exclude=self._end_stops)
            if n is not None:
                # Activate drag mode.
                self._drag_position = n


    def mouseReleaseEvent(self, e):
        self._drag_position = None
        self._sort_gradient()

    def mouseMoveEvent(self, e):
        self.mousex = e.x()
        self.mousey = e.y()
        # If drag active, move the stop.
        if self._drag_position:
            stop = e.x() / (self.width()-(self.MARGIN_SPACE))
            _, color = self._gradient[self._drag_position]
            self._gradient[self._drag_position] = stop, color
            self._constrain_gradient()
        self.update()

    def mouseDoubleClickEvent(self, e):
        # Calculate the position of the click relative 0..1 to the width.
        n = self._find_stop_handle_for_event(e)
        if n:
            self._sort_gradient() # Ensure ordered.
            # Delete existing, if not at the ends.
            if n > 0 and n < len(self._gradient) - 1:
                self.removeStopAtPosition(n)

        else:
            stop = e.x() / (self.width()-(self.MARGIN_SPACE))
            self.addStop(stop)





