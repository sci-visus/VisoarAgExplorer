import os
from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5.uic as uic
import cv2
import csv
import numpy as np
import copy
LUT_Class, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_LUT.ui'))


class Applicator(QtWidgets.QDialog, LUT_Class):

    _lut = None
    _min = None
    _max = None
    yval = [[165, 0, 38],
            [215, 46, 39],
            [251, 174, 98],
            [255, 255, 190],
            [168, 217, 105],
            [33, 178, 25],
            [12, 103, 56]]
    def __init__(self, parent=None):
        """Constructor."""
        super(Applicator, self).__init__(parent=parent)
        self.parent = parent

        self.setupUi(self)
        self.parent.LUTButton.setEnabled(False)
        self.RasterMin.setText(str(round(self.parent.LUT_Min, 2)))
        self.RasterMax.setText(str(round(self.parent.LUT_Max, 2)))
        try:
            img = cv2.imread(os.path.dirname(__file__) + "/lut_red-to-green.jpg")
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w = img.shape[:2]
            img2 = QtGui.QImage(img, w, h, w * 3, QtGui.QImage.Format_RGB888)
            self.LUTColors.setPixmap(QtGui.QPixmap.fromImage(img2))
        except Exception as e:
            print(e)

    def on_RasterApplyButton_released(self):
        self.process_and_apply_lut()

    def on_RasterOkButton_released(self):
        self.process_and_apply_lut()
        self.parent.LUTButton.setStyleSheet("QComboBox {width: 111; height: 27;}")
        self.parent.LUTButton.setEnabled(True)
        self.close()

    def process_and_apply_lut(self):
        try:
            self.processLUT()
            self.parent.LUTBox.setEnabled(True)

            if self.parent.LUTBox.isChecked():
                self.parent.applyLUT()
            else:
                self.parent.LUTBox.setChecked(True)
        except Exception as e:
            print(e)

    def on_RasterCloseButton_released(self):
        self.parent.LUTButton.setStyleSheet("QComboBox {width: 111; height: 27;}")
        self.parent.LUTButton.setEnabled(True)
        self.close()

    def processLUT(self):

        self._lut = np.zeros((256, 1, 3), dtype=np.uint8)

        if self.ColorMap.currentIndex() == 0:
            self._lut[0:256, 0, 0] = [33, ] * 256
            self._lut[0:256, 0, 1] = [178, ] * 256
            self._lut[0:256, 0, 2] = [25, ] * 256

        elif self.ColorMap.currentIndex() == 1:
            for x, y in enumerate(range(0, 170)):
                self._lut[y, 0, 0] = int(self.yval[1][0] + (x * ((self.yval[3][0] - self.yval[1][0]) / 170)))
                self._lut[y, 0, 1] = int(self.yval[1][1] + (x * ((self.yval[3][1] - self.yval[1][1]) / 170)))
                self._lut[y, 0, 2] = int(self.yval[1][2] + (x * ((self.yval[3][2] - self.yval[1][2]) / 170)))
            # self._lut[0:85, 0, 0] = [215, ] * 85
            # self._lut[0:85, 0, 1] = [46, ] * 85
            # self._lut[0:85, 0, 2] = [39, ] * 85
            for x, y in enumerate(range(170, 256)):
                self._lut[y, 0, 0] = int(self.yval[3][0] + (x * ((self.yval[5][0] - self.yval[3][0]) / 171)))
                self._lut[y, 0, 1] = int(self.yval[3][1] + (x * ((self.yval[5][1] - self.yval[3][1]) / 171)))
                self._lut[y, 0, 2] = int(self.yval[3][2] + (x * ((self.yval[5][2] - self.yval[3][2]) / 171)))

            # for x, y in enumerate(range(170, 256)):
            #     self._lut[y, 0, 0] = int(33 - (x * (222 / 86)))
            #     self._lut[y, 0, 1] = int(178 - (x * (77 / 86)))
            #     self._lut[y, 0, 2] = int(25 - (x * (165 / 86)))

            # self._lut[170:256, 0, 0] = [33, ] * 86
            # self._lut[170:256, 0, 1] = [178, ] * 86
            # self._lut[170:256, 0, 2] = [25, ] * 86

        elif self.ColorMap.currentIndex() == 2:

            #TODO Change these values to match 5 and 7 color luts
            for x, y in enumerate(range(0, 64)):
                self._lut[y, 0, 0] = int(self.yval[1][0] + (x * ((self.yval[2][0] - self.yval[1][0]) / 64)))
                self._lut[y, 0, 1] = int(self.yval[1][1] + (x * ((self.yval[2][1] - self.yval[1][1]) / 64)))
                self._lut[y, 0, 2] = int(self.yval[1][2] + (x * ((self.yval[2][2] - self.yval[1][2]) / 64)))

            for x, y in enumerate(range(64, 128)):
                self._lut[y, 0, 0] = int(self.yval[2][0] + (x * ((self.yval[3][0] - self.yval[2][0]) / 64)))
                self._lut[y, 0, 1] = int(self.yval[2][1] + (x * ((self.yval[3][1] - self.yval[2][1]) / 64)))
                self._lut[y, 0, 2] = int(self.yval[2][2] + (x * ((self.yval[3][2] - self.yval[2][2]) / 64)))

            for x, y in enumerate(range(128, 192)):
                self._lut[y, 0, 0] = int(self.yval[3][0] + (x * ((self.yval[4][0] - self.yval[3][0]) / 64)))
                self._lut[y, 0, 1] = int(self.yval[3][1] + (x * ((self.yval[4][1] - self.yval[3][1]) / 64)))
                self._lut[y, 0, 2] = int(self.yval[3][2] + (x * ((self.yval[4][2] - self.yval[3][2]) / 64)))

            for x, y in enumerate(range(192, 256)):
                self._lut[y, 0, 0] = int(self.yval[4][0] + (x * ((self.yval[5][0] - self.yval[4][0]) / 64)))
                self._lut[y, 0, 1] = int(self.yval[4][1] + (x * ((self.yval[5][1] - self.yval[4][1]) / 64)))
                self._lut[y, 0, 2] = int(self.yval[4][2] + (x * ((self.yval[5][2] - self.yval[4][2]) / 64)))

            # self._lut[153:204, 0, 0] = [168, ] * 51
            # self._lut[153:204, 0, 1] = [217, ] * 51
            # self._lut[153:204, 0, 2] = [105, ] * 51
            #
            # self._lut[204:256, 0, 0] = [33, ] * 52
            # self._lut[204:256, 0, 1] = [178, ] * 52
            # self._lut[204:256, 0, 2] = [25, ] * 52


        elif self.ColorMap.currentIndex() == 3:

            for x, y in enumerate(range(0, 42)):
                self._lut[y, 0, 0] = int(self.yval[0][0] + (x * ((self.yval[1][0] - self.yval[0][0]) / 42)))
                self._lut[y, 0, 1] = int(self.yval[0][1] + (x * ((self.yval[1][1] - self.yval[0][1]) / 42)))
                self._lut[y, 0, 2] = int(self.yval[0][2] + (x * ((self.yval[1][2] - self.yval[0][2]) / 42)))

            for x, y in enumerate(range(42, 84)):
                self._lut[y, 0, 0] = int(self.yval[1][0] + (x * ((self.yval[2][0] - self.yval[1][0]) / 42)))
                self._lut[y, 0, 1] = int(self.yval[1][1] + (x * ((self.yval[2][1] - self.yval[1][1]) / 42)))
                self._lut[y, 0, 2] = int(self.yval[1][2] + (x * ((self.yval[2][2] - self.yval[1][2]) / 42)))

            for x, y in enumerate(range(84, 126)):
                self._lut[y, 0, 0] = int(self.yval[2][0] + (x * ((self.yval[3][0] - self.yval[2][0]) / 42)))
                self._lut[y, 0, 1] = int(self.yval[2][1] + (x * ((self.yval[3][1] - self.yval[2][1]) / 42)))
                self._lut[y, 0, 2] = int(self.yval[2][2] + (x * ((self.yval[3][2] - self.yval[2][2]) / 42)))

            for x, y in enumerate(range(126, 168)):
                self._lut[y, 0, 0] = int(self.yval[3][0] + (x * ((self.yval[4][0] - self.yval[3][0]) / 42)))
                self._lut[y, 0, 1] = int(self.yval[3][1] + (x * ((self.yval[4][1] - self.yval[3][1]) / 42)))
                self._lut[y, 0, 2] = int(self.yval[3][2] + (x * ((self.yval[4][2] - self.yval[3][2]) / 42)))

            for x, y in enumerate(range(168, 210)):
                self._lut[y, 0, 0] = int(self.yval[4][0] + (x * ((self.yval[5][0] - self.yval[4][0]) / 42)))
                self._lut[y, 0, 1] = int(self.yval[4][1] + (x * ((self.yval[5][1] - self.yval[4][1]) / 42)))
                self._lut[y, 0, 2] = int(self.yval[4][2] + (x * ((self.yval[5][2] - self.yval[4][2]) / 42)))

            for x, y in enumerate(range(210, 256)):
                self._lut[y, 0, 0] = int(self.yval[5][0] + (x * ((self.yval[6][0] - self.yval[5][0]) / 46)))
                self._lut[y, 0, 1] = int(self.yval[5][1] + (x * ((self.yval[6][1] - self.yval[5][1]) / 46)))
                self._lut[y, 0, 2] = int(self.yval[5][2] + (x * ((self.yval[6][2] - self.yval[5][2]) / 46)))

            # self._lut[0:36, 0, 0] = [165, ] * 36
            # self._lut[0:36, 0, 1] = [0, ] * 36
            # self._lut[0:36, 0, 2] = [38, ] * 36
            #
            # self._lut[36:72, 0, 0] = [215, ] * 36
            # self._lut[36:72, 0, 1] = [46, ] * 36
            # self._lut[36:72, 0, 2] = [39, ] * 36
            #
            # self._lut[72:108, 0, 0] = [251, ] * 36
            # self._lut[72:108, 0, 1] = [174, ] * 36
            # self._lut[72:108, 0, 2] = [98, ] * 36
            #
            # self._lut[108:144, 0, 0] = [255, ] * 36
            # self._lut[108:144, 0, 1] = [255, ] * 36
            # self._lut[108:144, 0, 2] = [190, ] * 36
            #
            # self._lut[144:180, 0, 0] = [168, ] * 36
            # self._lut[144:180, 0, 1] = [217, ] * 36
            # self._lut[144:180, 0, 2] = [105, ] * 36
            #
            # self._lut[180:216, 0, 0] = [33, ] * 36
            # self._lut[180:216, 0, 1] = [178, ] * 36
            # self._lut[180:216, 0, 2] = [25, ] * 36
            #
            # self._lut[216:256, 0, 0] = [12, ] * 40
            # self._lut[216:256, 0, 1] = [103, ] * 40
            # self._lut[216:256, 0, 2] = [56, ] * 40
        try:
            self._min = float(self.RasterMin.text())
            self._max = float(self.RasterMax.text())
            range_ = copy.deepcopy(self.parent.calcwindow.ndvi)
            temp = copy.deepcopy(self.parent.calcwindow.ndvi)

            global_lut_min = round(self.parent.LUT_Min, 2)
            global_lut_max = round(self.parent.LUT_Max, 2)

            workingmin = (((self._min / (abs((global_lut_min)) if self._min < 0 else global_lut_min * -1)) + 1)/2) * 255
            workingmax = (((self._max / (abs((global_lut_max)) if self._max > 0 else global_lut_min * -1)) + 1)/2) * 255

            range_[range_ < workingmin] = workingmin
            range_[range_ > workingmax] = workingmax
            range_ = (((range_ - range_.min())/(range_.max() - range_.min())) * 255).astype("uint8")
            range_ = cv2.cvtColor(range_, cv2.COLOR_GRAY2RGB)
            legend = cv2.imread(os.path.dirname(__file__) + r'\lut_legend_rgb.jpg', -1).astype("uint8")
            legend = cv2.cvtColor(legend, cv2.COLOR_BGR2RGB)
            h, w = legend.shape[:2]
            self.parent.legend_frame = QtGui.QImage(legend.data, w, h, w * 3, QtGui.QImage.Format_RGB888)


            # legend = cv2.LUT(legend, self._lut)
            # legend = cv2.cvtColor(legend, cv2.COLOR_RGB2BGR)
            self.parent.ndvipsuedo = cv2.LUT(range_, self._lut)
            # cv2.imwrite(os.path.dirname(__file__) + r'\lut_legend_rgb.jpg', legend)

            # self.parent.legend_scene = QtWidgets.QGraphicsScene()
            self.parent.LUTGraphic.setPixmap(QtGui.QPixmap.fromImage(
                QtGui.QImage(self.parent.legend_frame)))

            #TODO Calculate based on distance
            midpoint = (self._max - self._min)/2
            steps = midpoint * 1/3
            self.parent.legend_max.setText(str(round(self._max, 2)))
            self.parent.legend_2thirds.setText(str(round(self._max - (steps), 2)))
            self.parent.legend_1third.setText(str(round(self._max - (steps * 2), 2)))
            self.parent.legend_zero.setText(str(round(self._max - (steps * 3), 2)))
            self.parent.legend_min.setText(str(round(self._min, 2)))
            self.parent.legend_neg2thirds.setText(str(round(self._max - (steps * 5), 2)))
            self.parent.legend_neg1third.setText(str(round(self._max - (steps * 4), 2)))
            QtWidgets.QApplication.processEvents()


            if self.ClipOption.currentIndex() == 1:
                self.parent.ndvipsuedo[temp <= workingmin] = 0
                self.parent.ndvipsuedo[temp >= workingmax] = 0
                self.parent.ndvipsuedo = cv2.cvtColor(self.parent.ndvipsuedo, cv2.COLOR_RGB2RGBA)
                alpha = self.parent.ndvipsuedo[:, :, 3]
                alpha[self.parent.ndvipsuedo[:, :, 0] == 0] = 0
                alpha[self.parent.ndvipsuedo[:, :, 1] == 0] = 0
                alpha[self.parent.ndvipsuedo[:, :, 2] == 0] = 0
            elif self.ClipOption.currentIndex() == 2:
                self.parent.ndvipsuedo[temp <= workingmin, 0] = temp[temp <= workingmin]
                self.parent.ndvipsuedo[temp <= workingmin, 1] = temp[temp <= workingmin]
                self.parent.ndvipsuedo[temp <= workingmin, 2] = temp[temp <= workingmin]
                self.parent.ndvipsuedo[temp >= workingmax, 0] = temp[temp >= workingmax]
                self.parent.ndvipsuedo[temp >= workingmax, 1] = temp[temp >= workingmax]
                self.parent.ndvipsuedo[temp >= workingmax, 2] = temp[temp >= workingmax]
            elif self.ClipOption.currentIndex() == 3:

                if self.parent.ViewerStretchBox.isChecked():
                    self.parent.ndvipsuedo[temp <= workingmin] = self.parent.display_image[temp <= workingmin]
                    # self.parent.ndvipsuedo[temp <= workingmin, 1] = temp[temp <= workingmin]
                    # self.parent.ndvipsuedo[temp <= workingmin, 2] = temp[temp <= workingmin]
                    self.parent.ndvipsuedo[temp >= workingmax] = self.parent.display_image[temp >= workingmax]
                    # self.parent.ndvipsuedo[temp >= workingmax, 1] = temp[temp >= workingmax]
                    # self.parent.ndvipsuedo[temp >= workingmax, 2] = temp[temp >= workingmax]
                else:
                    self.parent.ndvipsuedo[temp <= workingmin] = self.parent.display_image_original[temp <= workingmin]
                    self.parent.ndvipsuedo[temp >= workingmax] = self.parent.display_image_original[temp >= workingmax]

            self.parent.LUT_to_save = cv2.cvtColor(self.parent.ndvipsuedo, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(e)