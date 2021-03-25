
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

class ViSOARGradientMapViewWidget(QDialog):
    def __init__(self, parent,viewer,MODE):
        super(QDialog, self).__init__(parent)
        self.parent = parent
        self.viewer =viewer
        self.MODE = MODE
        self.setGeometry(30, 30, 600, 400)

        self.gradient = Gradient()
        # self.gradient.setGradient([(1, QColor.fromRgbF(0, .4, 0.2)),
        #                            (.75, QColor.fromRgbF(0, .4, 0.2)),
        #                            (0.5, QColor.fromRgbF(0, .83, 0.94)),
        #                            (0.25, QColor.fromRgbF(.008, .14, .286)),
        #                            (0, QColor.fromRgbF(.019, .019, .56))])

        # self.gradient.setGradient([(1, QColor.fromRgbF(.2, .4, 0)),
        #                            (.75, QColor.fromRgbF(.2, .4, 0)),
        #                            (0.5, QColor.fromRgbF(.94, .83, 0)),
        #                            (0.25, QColor.fromRgbF(.286, .14, .008)),
        #                       (0, QColor.fromRgbF(.56, .019, .019) ) ])
        self.gradient.setGradient([(1, QColor.fromRgbF(.2, .4, 0)),
                                   (.75, QColor.fromRgbF(.2, .4, 0)),
                                   (0.5, QColor.fromRgbF(0.94, 0.65 ,0.27)),
                                   (0.25, QColor.fromRgbF(0.74, 0.34 ,0.04)),
                              (0, QColor.fromRgbF(.56, .019, .019) ) ])
        self.gradient.setGeometry(0,0,300,100)

        # self.timeline = QTimeLine(500 )
        # self.timeline.setFrameRange(-1, 1)

        #gradient.setGradient([(0, 'purple'), (.25, 'purple'), (0.5, 'red'), (0.75, 'yellow'),
        #                  (1, 'green'), ])

        self.mapPiecesLayout =  QVBoxLayout()
        self.mapPiecesLayout.addWidget(self.gradient)

        self.outputGradient = createPushButton('Output Colors',
                                                  lambda: self.applyNewScript())
        self.outputGradient.setStyleSheet(NOBACKGROUND_PUSH_BUTTON)

        self.outputGradient.setStyleSheet(' color: #045951;')
        self.mapPiecesLayout.addWidget(self.outputGradient)

        # self.mapPiecesLayout.addWidget(self.timeline)

        self.setLayout(self.mapPiecesLayout)

        # self.pen =  QPen( QColor(0, 0, 0))  # set lineColor
        # self.pen.setWidth(3)  # set lineWidth
        # self.brush =  QBrush( QColor(255, 255, 255, 255))  # set fillColor
        # self.polygon = self.createPoly(8, 150, 0)  # polygon with n points, radius, angle of the first point


    def applyNewScript(self):
        MODE="NDVI"
        if (MODE == "RGB"):
            script = self.gradient.makeNewScriptRGB()
        else:
            script = self.gradient.makeNewScriptAgrocam()

        self.parent.runThisScript(script, self.viewer)

    # def createPoly(self, n, r, s):
    #     polygon =  QPolygonF()
    #     w = 360 / n  # angle per step
    #     for i in range(n):  # add the points of polygon
    #         t = w * i + s
    #         x = r * math.cos(math.radians(t))
    #         y = r * math.sin(math.radians(t))
    #         polygon.append( QPointF(self.width() / 2 + x, self.height() / 2 + y))
    #
    #     return polygon
    #
    #
    # def paintEvent(self, event):
    #     painter =  QPainter(self)
    #     painter.setPen(self.pen)
    #     painter.setBrush(self.brush)
    #     painter.drawPolygon(self.polygon)