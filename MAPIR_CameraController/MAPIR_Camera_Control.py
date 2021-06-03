import os
from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from MAPIR_Processing_dockwidget import *
import breeze_resouces

modpath = os.path.dirname(os.path.realpath(__file__))
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        # splash_pix = QPixmap(os.path.dirname(os.path.realpath(__file__)) + 'lut_legend_rgb.jpg')
        #
        # splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        # splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        # splash.setEnabled(True)
        # progressBar = QProgressBar(splash)
        # progressBar.setMaximum(30)
        # progressBar.setGeometry(0, splash_pix.height() - 50, splash_pix.width(), 20)
        # splash.show()
        # for i in range(1, 31):
        #         progressBar.setValue(i)
        #         t = time.time()
        #         while time.time() < t + 0.1:
        #                 app.processEvents()
        file = QFile(resource_path("dark.qss"))
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
        myapp = MAPIR_ProcessingDockWidget()
        myapp.setWindowIcon(QIcon(resource_path(".\corn_logo_taskbar.png")))
        myapp.show()
        # splash.finish(myapp)

    except Exception as e:
            print(e)
    sys.exit(app.exec_())
