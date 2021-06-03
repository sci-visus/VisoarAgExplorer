import os
from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5.uic as uic
os.umask(0)
BANDORDER_Class, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_BandOrder.ui'))

class BandOrder(QtWidgets.QDialog, BANDORDER_Class):
    _items = []


    def __init__(self, parent=None, items=None):
        """Constructor."""
        super(BandOrder, self).__init__(parent=parent)
        self.parent = parent

        self._items = items

        self.setupUi(self)
        for itm in self._items:
            self.Band1.addItem(itm)
            self.Band2.addItem(itm)
            self.Band3.addItem(itm)
            self.Band4.addItem(itm)
            self.Band5.addItem(itm)
            self.Band6.addItem(itm)
    def on_SaveButton_released(self):
        self.parent.rdr = [self.Band1.currentIndex() - 1,
            self.Band2.currentIndex() - 1,
            self.Band3.currentIndex() - 1,
            self.Band4.currentIndex() - 1,
            self.Band5.currentIndex() - 1,
            self.Band6.currentIndex() - 1]
        self.close()

    def on_CancelButton_released(self):
        self.close()

