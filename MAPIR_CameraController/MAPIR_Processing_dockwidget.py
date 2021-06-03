# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MAPIR_ProcessingDockWidget
                                 A QGIS plugin
 Widget for processing images captured by MAPIR cameras
                             -------------------
        begin                : 2016-09-26
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Peau Productions
        email                : ethan@peauproductions.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from os import listdir
import warnings
warnings.filterwarnings("ignore")

from PIL import Image
from PIL.TiffTags import TAGS
import sys

os.umask(0)

from  LensLookups import *
from  MAPIR_Enums import *

from datetime import datetime

import shutil
import platform
import itertools
import ctypes
import string
#import win32api
import PIL
import bitstring
import collections
# import tifffile

from PyQt5 import QtCore, QtGui, QtWidgets

import PyQt5.uic as uic

import numpy as np
import subprocess
import cv2
import copy
import hid
import time
import json
import math
import webbrowser

import Calibration
import show_image
import Geometry
from bit_depth_conversion import normalize, normalize_rgb
from camera_specs import CameraSpecs

from MAPIR_Enums import *
from Calculator import *
from LUT_Dialog import *
from Vignette import *
from BandOrder import *
from ViewerSave_Dialog import *
import xml.etree.ElementTree as ET
import KernelConfig
from MAPIR_Converter import *
from Exposure import *
from ArrayTypes import AdjustYPR, CurveAdjustment
from reg_value_conversion import *
from ExifUtils import *
from Geotiff import *


modpath = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(modpath + os.sep + "instring.txt"):
    istr = open(modpath + os.sep + "instring.txt", "w")
    istr.close()

# from osgeo import gdal
# gdal.UseExceptions()
# fp, pathname, description = imp.find_module('_gdal', [dirname(gdal.__file__)])
# dist_dir = "dist"
# shutil.copy(pathname, dist_dir)
# import gdal as gdal2
# import gdal

import glob

all_cameras = []
if sys.platform == "win32":
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    si = None
# if sys.platform == "win32":
#       import exiftool
#       exiftool.executable = modpath + os.sep + "exiftool.exe"
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_base.ui'))
MODAL_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_modal.ui'))
CAN_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_CAN.ui'))
TIME_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_time.ui'))
# DEL_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_delete.ui'))
TRANSFER_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_transfer.ui'))
ADVANCED_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_Advanced.ui'))
MATRIX_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_matrix.ui'))

class DebayerMatrix(QtWidgets.QDialog, MATRIX_CLASS):
    parent = None

    GAMMA_LIST = [
        {
            "CCM": [1,0,0,0,1,0,0,0,1],
            "RGB_OFFSET": [0,0,0],
            "GAMMA": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
        },
        {
            "CCM": [1,0,1.402,1,-0.34414,-0.71414,1,1.772,0],
            "RGB_OFFSET": [0, 0, 0],
            "GAMMA": [2.3,1.3,2.3,0.3,0.3,0.3,2.3,2.3,1,2,1,2,2,2,1,2,1,2,2,0,2,0,2,0]
        },
        {
            "CCM": [3.2406,-1.5372,-0.498,-0.9689,1.8756,0.0415,0.0557,-0.2040,1.0570 ],
            "RGB_OFFSET": [0, 0, 0],
            "GAMMA": [7.0,0.0,6.5,3.0,6.0,8.0,5.5,13.0,5.0,22.0,4.5,38.0,3.5,102.0,2.5,230.0,1.75,422.0,1.25,679.0,0.875,1062.0,0.625,1575.0]
        }
    ]

    def __init__(self, parent=None):
        """Constructor."""
        super(DebayerMatrix, self).__init__(parent=parent)
        self.parent = parent

        self.setupUi(self)

    def on_ModalSaveButton_released(self):
        self.close()

    def on_ModalCancelButton_released(self):
        self.close()


class AdvancedOptions(QtWidgets.QDialog, ADVANCED_CLASS):
    parent = None

    def __init__(self, parent=None):
        """Constructor."""
        super(AdvancedOptions, self).__init__(parent=parent)
        self.parent = parent

        self.setupUi(self)
        try:
            buf = [0] * 512
            buf[0] = self.parent.SET_REGISTER_READ_REPORT
            buf[1] = eRegister.RG_UNMOUNT_SD_CARD_S.value
            # if self.SDCTUM.text():
            #     buf[2] = int(self.SDCTUM.text()) if 0 <= int(self.SDCTUM.text()) < 255 else 255

            res = self.parent.writeToKernel(buf)[2]
            self.SDCTUM.setText(str(res))

            buf = [0] * 512
            buf[0] = self.parent.SET_REGISTER_READ_REPORT
            buf[1] = eRegister.RG_VIDEO_ON_DELAY.value
            # buf[2] = int(self.VCRD.text()) if 0 <= int(self.VCRD.text()) < 255 else 255

            res = self.parent.writeToKernel(buf)[2]
            self.VCRD.setText(str(res))

            buf = [0] * 512
            buf[0] = self.parent.SET_REGISTER_READ_REPORT
            buf[1] = eRegister.RG_PHOTO_FORMAT.value


            res = self.parent.writeToKernel(buf)[2]
            self.KernelPhotoFormat.setCurrentIndex(int(res))

            buf = [0] * 512
            buf[0] = self.parent.SET_REGISTER_BLOCK_READ_REPORT
            buf[1] = eRegister.RG_MEDIA_FILE_NAME_A.value
            buf[2] = 3
            # buf[3] = ord(self.CustomFilter.text()[0])
            # buf[4] = ord(self.CustomFilter.text()[1])
            # buf[5] = ord(self.CustomFilter.text()[2])
            res = self.parent.writeToKernel(buf)
            filt = chr(res[2]) + chr(res[3]) + chr(res[4])

            self.CustomFilter.setText(str(filt))

            # buf = [0] * 512
            # buf[0] = self.parent.SET_REGISTER_READ_REPORT
            # buf[1] = eRegister.RG_DEBOUNCE_HIGH.value

            # db_trig_high = self.parent.writeToKernel(buf)[2]

            # buf = [0] * 512
            # buf[0] = self.parent.SET_REGISTER_READ_REPORT
            # buf[1] = eRegister.RG_DEBOUNCE_LOW.value

            # db_trig_low = self.parent.writeToKernel(buf)[2]

            # db_trig_value = db_trig_high*255 + db_trig_low
            # self.TriggerDebounce.setText(str(db_trig_value))

            QtWidgets.QApplication.processEvents()

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            self.parent.KernelLog.append(str(e) + ' Line: ' + str(exc_tb.tb_lineno))
            # QtWidgets.QApplication.processEvents()

        finally:
            QtWidgets.QApplication.processEvents()
            self.close()
        # for i in range(1, 256):
        #     self.SDCTUM.addItem(str(i))
        #
        # for j in range(1, 256):
        #     self.VCRD.addItem(str(j))
    # def on_ModalBrowseButton_released(self):
    #     with open(modpath + os.sep + "instring.txt", "r+") as instring:
    #         self.ModalOutputFolder.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
    #         instring.truncate(0)
    #         instring.seek(0)
    #         instring.write(self.ModalOutputFolder.text())
    #         self.ModalSaveButton.setEnabled(True)
    def on_SaveButton_released(self):
        # self.parent.transferoutfolder  = self.ModalOutputFolder.text()
        # self.parent.yestransfer = self.TransferBox.isChecked()
        # self.parent.yesdelete = self.DeleteBox.isChecked()
        # self.parent.selection_made = True
        try:

            buf = [0] * 512
            buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_UNMOUNT_SD_CARD_S.value
            val = int(self.SDCTUM.text()) if 0 < int(self.SDCTUM.text()) < 255 else 255
            buf[2] = val

            self.parent.writeToKernel(buf)

            # trigger_debounce_high = math.floor(int(self.TriggerDebounce.text()) / 255)
            # trigger_debounce_low = int(self.TriggerDebounce.text()) % 255

            # buf = [0] * 512
            # buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
            # buf[1] = eRegister.RG_DEBOUNCE_HIGH.value

            # val = int(trigger_debounce_high) if 0 <= int(trigger_debounce_high) <= 255 else 255
            # buf[2] = val

            # self.parent.writeToKernel(buf)

            # buf = [0] * 512
            # buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
            # buf[1] = eRegister.RG_DEBOUNCE_LOW.value

            # val = int(trigger_debounce_low) if 0 <= int(trigger_debounce_low) <= 255 else 255
            # buf[2] = val

            # self.parent.writeToKernel(buf)

            buf = [0] * 512
            buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_VIDEO_ON_DELAY.value
            val = int(self.VCRD.text()) if 0 < int(self.VCRD.text()) < 255 else 255
            buf[2] = val

            self.parent.writeToKernel(buf)

            buf = [0] * 512
            buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_PHOTO_FORMAT.value
            buf[2] = int(self.KernelPhotoFormat.currentIndex())


            self.parent.writeToKernel(buf)
            buf = [0] * 512
            buf[0] = self.parent.SET_REGISTER_BLOCK_WRITE_REPORT
            buf[1] = eRegister.RG_MEDIA_FILE_NAME_A.value
            buf[2] = 3
            buf[3] = ord(self.CustomFilter.text()[0])
            buf[4] = ord(self.CustomFilter.text()[1])
            buf[5] = ord(self.CustomFilter.text()[2])
            res = self.parent.writeToKernel(buf)

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            self.parent.KernelLog.append(str(e) + ' Line: ' + str(exc_tb.tb_lineno))

        finally:
            QtWidgets.QApplication.processEvents()
            self.close()

    def on_CancelButton_released(self):
        # self.parent.yestransfer = False
        # self.parent.yesdelete = False
        # self.parent.selection_made = True
        self.close()

class KernelTransfer(QtWidgets.QDialog, TRANSFER_CLASS):
    parent = None

    def __init__(self, parent=None):
        """Constructor."""
        super(KernelTransfer, self).__init__(parent=parent)
        self.parent = parent
        self.setupUi(self)

    def on_ModalBrowseButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            self.ModalOutputFolder.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.ModalOutputFolder.text())
            self.ModalSaveButton.setEnabled(True)
            self.ModalSaveButton.setStyleSheet("QComboBox {width: 116; height: 27;}")

    def on_DeleteBox_toggled(self):
        if self.DeleteBox.isChecked():
            self.ModalSaveButton.setEnabled(True)
            self.ModalSaveButton.setStyleSheet("QComboBox {width: 116; height: 27;}")
        else:
            self.ModalSaveButton.setEnabled(False)

    def on_ModalSaveButton_released(self):
        self.parent.transferoutfolder  = self.ModalOutputFolder.text()
        self.parent.yestransfer = self.TransferBox.isChecked()
        self.parent.yesdelete = self.DeleteBox.isChecked()
        self.parent.selection_made = True
        QtWidgets.QApplication.processEvents()
        self.close()

    def on_ModalCancelButton_released(self):
        self.parent.yestransfer = False
        self.parent.yesdelete = False
        self.parent.selection_made = True
        QtWidgets.QApplication.processEvents()
        self.close()

class KernelModal(QtWidgets.QDialog, MODAL_CLASS):
    parent = None

    def __init__(self, parent=None):
        """Constructor."""
        super(KernelModal, self).__init__(parent=parent)
        self.parent = parent

        self.setupUi(self)

    def on_ModalSaveButton_released(self):
        seconds = int(self.SecondsLine.text())
        minutes = int(self.MinutesLine.text())
        hours = int(self.HoursLine.text())
        days = int(self.DaysLine.text())
        weeks = int(self.WeeksLine.text())

        if (seconds / 60) > 1:
            minutes += int(seconds / 60)
            seconds = seconds % 60

        if (minutes / 60) > 1:
            hours += int(minutes / 60)
            minutes = minutes % 60

        if (hours / 24) > 1:
            days += int(hours / 24)
            hours = hours % 24

        if (days / 7) > 1:
            weeks += int(days / 7)
            days = days % 7

        self.parent.seconds = seconds
        self.parent.minutes = minutes
        self.parent.hours = hours
        self.parent.days = days
        self.parent.weeks = weeks
        self.parent.writeToIntervalLine()
        self.close()

    def on_ModalCancelButton_released(self):
        self.close()


class KernelCAN(QtWidgets.QDialog, CAN_CLASS):
    parent = None

    def __init__(self, parent=None):
        """Constructor."""
        super(KernelCAN, self).__init__(parent=parent)
        self.parent = parent

        self.setupUi(self)
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_CAN_NODE_ID.value
        nodeid = self.parent.writeToKernel(buf)[2]
        # buf[2] = nodeid

        self.KernelNodeID.setText(str(nodeid))
        # self.parent.writeToKernel(buf)
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_BLOCK_READ_REPORT
        buf[1] = eRegister.RG_CAN_BIT_RATE_1.value
        buf[2] = 2
        bitrate = self.parent.writeToKernel(buf)[2:4]
        bitval = ((bitrate[0] << 8) & 0xff00) | bitrate[1]
        self.KernelBitRate.setCurrentIndex(self.KernelBitRate.findText(str(bitval)))
        # bit1 = (bitrate >> 8) & 0xff
        # bit2 = bitrate & 0xff
        # buf[3] = bit1
        # buf[4] = bit2

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_BLOCK_READ_REPORT
        buf[1] = eRegister.RG_CAN_SAMPLE_POINT_1.value
        buf[2] = 2
        samplepoint = self.parent.writeToKernel(buf)[2:4]


        sample = ((samplepoint[0] << 8) & 0xff00) | samplepoint[1]
        self.KernelSamplePoint.setText(str(sample))

    def on_ModalSaveButton_released(self):
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_CAN_NODE_ID.value
        nodeid = int(self.KernelNodeID.text())
        buf[2] = nodeid

        self.parent.writeToKernel(buf)
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_BLOCK_WRITE_REPORT
        buf[1] = eRegister.RG_CAN_BIT_RATE_1.value
        buf[2] = 2

        bitrate = int(self.KernelBitRate.currentText())
        bit1 = (bitrate >> 8) & 0xff
        bit2 = bitrate & 0xff
        buf[3] = bit1
        buf[4] = bit2

        self.parent.writeToKernel(buf)
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_BLOCK_WRITE_REPORT
        buf[1] = eRegister.RG_CAN_SAMPLE_POINT_1.value
        buf[2] = 2

        samplepoint = int(self.KernelSamplePoint.text())
        sample1 = (samplepoint >> 8) & 0xff
        sample2 = samplepoint & 0xff
        buf[3] = sample1
        buf[4] = sample2

        self.parent.writeToKernel(buf)
        self.close()

    def on_ModalCancelButton_released(self):
        self.close()

class KernelTime(QtWidgets.QDialog, TIME_CLASS):
    parent = None
    timer = QtCore.QTimer()
    BUFF_LEN = 512
    SET_EVENT_REPORT = 1
    SET_COMMAND_REPORT = 3
    SET_REGISTER_WRITE_REPORT = 5
    SET_REGISTER_BLOCK_WRITE_REPORT = 7
    SET_REGISTER_READ_REPORT = 9
    SET_REGISTER_BLOCK_READ_REPORT = 11
    SET_CAMERA = 13

    def __init__(self, parent=None):
        """Constructor."""
        super(KernelTime, self).__init__(parent=parent)
        self.parent = parent

        self.setupUi(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1)

    def on_ModalSaveButton_released(self):
        self.timer.stop()

        # if self.parent.KernelCameraSelect.currentIndex() == 0:
        #     for p in self.parent.paths:
        #         self.parent.camera = p
        #
        #         self.adjustRTC()
        #     self.parent.camera = self.parent.paths[0]
        # else:
        self.adjustRTC()

    def adjustRTC(self):
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_BLOCK_WRITE_REPORT
        buf[1] = eRegister.RG_REALTIME_CLOCK.value
        buf[2] = 8
        t = QtCore.QDateTime.toMSecsSinceEpoch(self.KernelReferenceTime.dateTime())

        buf[3] = t & 0xff
        buf[4] = (t >> 8) & 0xff
        buf[5] = (t >> 16) & 0xff
        buf[6] = (t >> 24) & 0xff
        buf[7] = (t >> 32) & 0xff
        buf[8] = (t >> 40) & 0xff
        buf[9] = (t >> 48) & 0xff
        buf[10] = (t >> 54) & 0xff

        self.parent.writeToKernel(buf)
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
        buf[1] = eRegister.RG_REALTIME_CLOCK.value
        buf[2] = 8

        r = self.parent.writeToKernel(buf)[2:11]
        val = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24) | (r[4] << 32) | (r[5] << 40) | (r[6] << 48) | (
        r[7] << 56)
        offset = QtCore.QDateTime.currentMSecsSinceEpoch() - val

        while offset > 0.01:
            if self.KernelTimeSelect.currentIndex() == 0:
                buf[0] = self.SET_REGISTER_BLOCK_WRITE_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8
                t = QtCore.QDateTime.toMSecsSinceEpoch(QtCore.QDateTime.currentDateTimeUtc().addSecs(18).addMSecs(offset))

                buf[3] = t & 0xff
                buf[4] = (t >> 8) & 0xff
                buf[5] = (t >> 16) & 0xff
                buf[6] = (t >> 24) & 0xff
                buf[7] = (t >> 32) & 0xff
                buf[8] = (t >> 40) & 0xff
                buf[9] = (t >> 48) & 0xff
                buf[10] = (t >> 54) & 0xff

                self.parent.writeToKernel(buf)
                buf = [0] * 512
                buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8

                r = self.parent.writeToKernel(buf)[2:11]
                val = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24) | (r[4] << 32) | (r[5] << 40) | (r[6] << 48) | (
                    r[7] << 56)
                offset = QtCore.QDateTime.currentMSecsSinceEpoch() - val

            elif self.KernelTimeSelect.currentIndex() == 1:
                buf[0] = self.SET_REGISTER_BLOCK_WRITE_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8
                t = QtCore.QDateTime.toMSecsSinceEpoch(QtCore.QDateTime.currentDateTimeUtc().addMSecs(offset))

                buf[3] = t & 0xff
                buf[4] = (t >> 8) & 0xff
                buf[5] = (t >> 16) & 0xff
                buf[6] = (t >> 24) & 0xff
                buf[7] = (t >> 32) & 0xff
                buf[8] = (t >> 40) & 0xff
                buf[9] = (t >> 48) & 0xff
                buf[10] = (t >> 54) & 0xff

                self.parent.writeToKernel(buf)
                buf = [0] * 512
                buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8

                r = self.parent.writeToKernel(buf)[2:11]
                val = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24) | (r[4] << 32) | (r[5] << 40) | (r[6] << 48) | (
                    r[7] << 56)
                offset = QtCore.QDateTime.currentMSecsSinceEpoch() - val

            else:
                buf[0] = self.SET_REGISTER_BLOCK_WRITE_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8
                t = QtCore.QDateTime.toMSecsSinceEpoch(QtCore.QDateTime.currentDateTime().addMSecs(offset))

                buf[3] = t & 0xff
                buf[4] = (t >> 8) & 0xff
                buf[5] = (t >> 16) & 0xff
                buf[6] = (t >> 24) & 0xff
                buf[7] = (t >> 32) & 0xff
                buf[8] = (t >> 40) & 0xff
                buf[9] = (t >> 48) & 0xff
                buf[10] = (t >> 54) & 0xff

                self.parent.writeToKernel(buf)
                buf = [0] * 512
                buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
                buf[1] = eRegister.RG_REALTIME_CLOCK.value
                buf[2] = 8

                r = self.parent.writeToKernel(buf)[2:11]
                val = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24) | (r[4] << 32) | (r[5] << 40) | (r[6] << 48) | (
                    r[7] << 56)
                offset = QtCore.QDateTime.currentMSecsSinceEpoch() - val

        self.close()

    def on_ModalCancelButton_released(self):
        self.timer.stop()
        self.close()

    def tick(self):
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
        buf[1] = eRegister.RG_REALTIME_CLOCK.value
        buf[2] = 8

        r = self.parent.writeToKernel(buf)[2:11]
        val = r[0] | (r[1] << 8) | (r[2] << 16) | (r[3] << 24) | (r[4] << 32) | (r[5] << 40) | (r[6] << 48) | (r[7] << 56)
        self.KernelCameraTime.setDateTime(QtCore.QDateTime.fromMSecsSinceEpoch(val))

        if self.KernelTimeSelect.currentIndex() == 0:
            self.KernelReferenceTime.setDateTime(QtCore.QDateTime.currentDateTimeUtc().addSecs(18))

        elif self.KernelTimeSelect.currentIndex() == 1:
            self.KernelReferenceTime.setDateTime(QtCore.QDateTime.currentDateTimeUtc())

        else:
            self.KernelReferenceTime.setDateTime(QtCore.QDateTime.currentDateTime())

class tPoll:
    def __init__(self):
        request = 0
        code = 0
        len = 0 #Len can also store the value depending on the code given
        values = []

class tEventInfo:
    def __init__(self):
        mode = 0
        process = 0
        focusing = 0
        inversion = 0
        nr_faces = 0

class MAPIR_ProcessingDockWidget(QtWidgets.QMainWindow, FORM_CLASS):
    BASE_COEFF_SURVEY1_NDVI_JPG = {"red":   {"slope": 331.759383023, "intercept": -6.33770486888},
                                   "green": {"slope": 1.00, "intercept": 0.00},
                                   "blue":  {"slope": 51.3264675118, "intercept": -0.6931339436}
                                  }

    BASE_COEFF_SURVEY2_RED_JPG = {"slope": 16.01240929, "intercept": -2.55421832}
    BASE_COEFF_SURVEY2_RED_TIF = {"slope": 0.24177528, "intercept": -5.09645820}

    BASE_COEFF_SURVEY2_GREEN_JPG = {"slope": 4.82869470, "intercept": -0.60437250}
    BASE_COEFF_SURVEY2_GREEN_TIF = {"slope": 0.07640011, "intercept": -1.39528479}

    BASE_COEFF_SURVEY2_BLUE_JPG = {"slope": 2.67916884, "intercept": -0.39268985}
    BASE_COEFF_SURVEY2_BLUE_TIF = {"slope": 0.03943339, "intercept": -0.67299134}


    BASE_COEFF_SURVEY2_NDVI_JPG = {"red":   {"slope": 6.51199915, "intercept": -0.29870245},
                                   "green": {"slope": 1.00, "intercept": 0.00},
                                   "blue":  {"slope": 10.30416005, "intercept": -0.65112026}
                                  }

    BASE_COEFF_SURVEY2_NDVI_TIF = {"red":   {"slope": 1.06087488594, "intercept": 3.21946584661},
                                   "green": {"slope": 1.00, "intercept": 0.00},
                                   "blue":  {"slope": 1.46482226805, "intercept": -43.6505776052}
                                  }

    BASE_COEFF_SURVEY2_NIR_JPG = {"slope": 7.13619139, "intercept": -0.46967653}
    BASE_COEFF_SURVEY2_NIR_TIF = {"slope":  0.12962333, "intercept": -2.24216724}

    BASE_COEFF_SURVEY3_NGB_TIF = {"red":   {"slope": 6.9623355781520475, "intercept": -0.0864835439375467},
                                  "green": {"slope": 1.8947426321347667, "intercept": -0.0494622920687357},
                                  "blue":  {"slope": 2.743963570586564, "intercept":  -0.03883688306243116}
                                 }

    BASE_COEFF_SURVEY3_NGB_JPG = {"red":   {"slope": 1.3572359350724152, "intercept": -0.23211423412281346},
                                  "green": {"slope": 1.1880427799275182, "intercept": -0.15262065349606874},
                                  "blue":  {"slope": 1.352860697992975, "intercept":  -0.19361810260132328}
                                 }

    BASE_COEFF_SURVEY3_RGN_JPG = {"red":   {"slope": 1.3289958195489457, "intercept": -0.17638075239399503},
                                  "green": {"slope": 1.2902528664499517, "intercept": -0.15262065349606874},
                                  "blue":  {"slope": 1.387381083964384, "intercept":  -0.2193633829181454}
                                 }

    BASE_COEFF_SURVEY3_RGN_TIF = {"red":   {"slope": 3.3823966319413326, "intercept": -0.025581742423831766},
                                  "green": {"slope": 2.0198257823722026, "intercept": -0.019624370783744682},
                                  "blue":  {"slope": 6.639688121967463, "intercept":  -0.025991734455270532}
                                 }

    BASE_COEFF_SURVEY3_OCN_JPG = {"red":   {"slope": 1.0228327654792326, "intercept": -0.1847085716228949},
                                  "green": {"slope":  1.0655229303683258, "intercept": -0.1921036590734388},
                                  "blue":  {"slope": 1.0562618906633048, "intercept":  -0.2037317328293336}
                                 }

    BASE_COEFF_SURVEY3_OCN_TIF = {"red":   {"slope": 1.557354345031938, "intercept": -0.0790237907829558},
                                  "green": {"slope": 1.3794503108318112, "intercept": -0.0743811687912796},
                                  "blue":  {"slope": 2.1141137232666183, "intercept": -0.0650818927718132}
                                 }

    BASE_COEFF_SURVEY3_NIR_TIF = {"slope":  13.2610911247, "intercept": 0.0}

    BASE_COEFF_SURVEY3_RE_JPG = {"slope":  0.12962333, "intercept": -2.24216724}
    BASE_COEFF_SURVEY3_RE_TIF = {"slope":  14.637430522690837, "intercept": -0.11816284659122683}

    BASE_COEFF_DJIX3_NDVI_JPG = {"red":   {"slope": 4.63184993, "intercept": -0.34430543},
                                 "green": {"slope": 1.00, "intercept": 0.00},
                                 "blue":  {"slope": 16.36429964, "intercept": -0.49413940}
                                }

    BASE_COEFF_DJIX3_NDVI_TIF = {"red":   {"slope": 0.01350319, "intercept": -0.74925346},
                                 "green": {"slope": 1.00, "intercept": 0.00},
                                 "blue":  {"slope": 0.03478272, "intercept": -0.77810008}
                                }

    BASE_COEFF_DJIPHANTOM4_NDVI_JPG = {"red":   {"slope": 0.03333209, "intercept": -1.17016961},
                                       "green": {"slope": 1.00, "intercept": 0.00},
                                       "blue":  {"slope": 0.05373502, "intercept": -0.99455214}
                                      }

    BASE_COEFF_DJIPHANTOM4_NDVI_TIF = {"red":   {"slope": 0.03333209, "intercept": -1.17016961},
                                       "green": {"slope": 1.00, "intercept": 0.00},
                                       "blue":  {"slope": 0.05373502, "intercept": -0.99455214}
                                      }

    BASE_COEFF_DJIPHANTOM3_NDVI_JPG = {"red":   {"slope": 3.44708472, "intercept": -1.54494979},
                                       "green": {"slope": 1.00, "intercept": 0.00},
                                       "blue":  {"slope": 6.35407929, "intercept": -1.40606832}
                                      }

    BASE_COEFF_DJIPHANTOM3_NDVI_TIF = {"red":   {"slope":  0.01752340, "intercept": -1.37495554},
                                       "green": {"slope": 1.00, "intercept": 0.00},
                                       "blue":  {"slope": 0.03700812, "intercept": -1.41073753}
                                      }

    BASE_COEFF_KERNEL_F644 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F405 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F450 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F520 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F550 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F632 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F650 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F725 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F808 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F850 = [0.0, 0.0]
    BASE_COEFF_KERNEL_F395_870 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F475_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F550_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F660_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F475_550_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    BASE_COEFF_KERNEL_F550_660_850 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # eFilter = mousewheelFilter()
    camera = 0
    poll = []
    ei = tEventInfo()
    capturing = False
    SQ_TO_TARG = 2.1875
    SQ_TO_SQ = 5.0
    CORNER_TO_CORNER = 5.25
    CORNER_TO_TARG = 10.0
    TARGET_LENGTH = 2.0
    TARG_TO_TARG = 2.6
    dialog = None
    imcols = 4608
    imrows = 3456
    imsize = imcols * imrows
    closingPlugin = QtCore.pyqtSignal()
    firstpass = True
    useqr = False
    qrcoeffs = []

    qrcoeffs2 = []
    qrcoeffs3 = []
    qrcoeffs4 = []
    qrcoeffs5 = []
    qrcoeffs6 = []
    coords = []
    # drivesfound = []
    ref = ""
    refindex = ["oldrefvalues", "newrefvalues"] #version 1 - old, version 2 - new
    refvalues = {
    "oldrefvalues":{
        "660/850": [[0.87032549, 0.52135779, 0.23664799], [0, 0, 0], [0.8463514, 0.51950608, 0.22795518]],
        "446/800": [[0.8419608509, 0.520440145, 0.230113958], [0, 0, 0], [0.8645652801, 0.5037779363, 0.2359041624]],
        "850": [[0.8463514, 0.51950608, 0.22795518], [0, 0, 0], [0, 0, 0]],

        "650": [[0.87032549, 0.52135779, 0.23664799], [0, 0, 0], [0, 0, 0]],
        "550": [[0, 0, 0], [0.87415089, 0.51734381, 0.24032515], [0, 0, 0]],
        "450": [[0, 0, 0], [0, 0, 0], [0.86469794, 0.50392915, 0.23565447]],
        "725": [0.8609978650653954, 0.5211329995745606, 0.23324225504400245],
        "490/615/808": [0.8472247816774043, 0.5200480372488874, 0.23065111839727553],
        "Mono450": [0.8634818638, 0.5024087105, 0.2351860396],
        "Mono550": [0.8740616379, 0.5173070235, 0.2402423818],
        "Mono650": [0.8705783136, 0.5212290524, 0.2366437854],
        "Mono725": [0.8606071247, 0.521474266, 0.2337744252],
        "Mono808": [0.8406184266, 0.5203405498, 0.2297701185],
        "Mono850": [0.8481919553, 0.519491643, 0.2278713071],
        "Mono405": [0.8556905469, 0.4921243183, 0.2309899254],
        "Mono518": [0.8729814889, 0.5151370187, 0.2404729692],
        "Mono632": [0.8724034645, 0.5209649915, 0.2374529161],

        "Mono590": [0.8747043911, 0.5195596573, 0.2392049856],
        "550/660/850": [[0.8474610999, 0.5196055607, 0.2279922965],[0.8699940018, 0.5212235151, 0.2364397706],[0.8740311726, 0.5172611881, 0.2402870156]]

    },
    "newrefvalues":{
        "660/850": [[0.8691644285714284, 0.2624914285714286, 0.20969199999999993, 0.019544714285714283], [0, 0, 0, 0], [0.8653063177, 0.2798126291, 0.2337498097, 0.0193295348]],
        "446/800": [[0.7882333002, 0.2501235178, 0.1848459584, 0.020036883], [0, 0, 0], [0.8645652801, 0.5037779363, 0.2359041624]],
        "725" : [0.8688518306024209, 0.26302553751154756, 0.2127410973890211, 0.019551020566927594],
        "850": [[0.8649280907, 0.2800907016, 0.2340131491, 0.0195446727], [0, 0, 0], [0, 0, 0]],

        "650": [[0.8773469949, 0.2663571183, 0.199919444, 0.0192325637], [0, 0, 0], [0, 0, 0]],
        "550": [[0, 0, 0], [0.8686559344, 0.2655697585, 0.1960837144, 0.0195629009], [0, 0, 0]],
        "450": [[0, 0, 0], [0, 0, 0], [0.7882333002, 0.2501235178, 0.1848459584, 0.020036883]],
        "Mono405": [0.6959473282,  0.2437485737, 0.1799017476, 0.0205591758],
        "Mono450": [0.7882333002, 0.2501235178, 0.1848459584, 0.020036883],
        "Mono490": [0.8348841674, 0.2580074987, 0.1890252099, 0.01975703],
        "Mono518": [0.8572181897, 0.2628629357, 0.192259471, 0.0196629792],
        "Mono550": [0.8686559344, 0.2655697585, 0.1960837144, 0.0195629009],
        "Mono590": [0.874586922, 0.2676592931, 0.1993779934, 0.0193745668],
        "Mono615": [0.8748454449, 0.2673426216, 0.1996415667, 0.0192891156],
        "Mono632": [0.8758224323, 0.2670055225, 0.2023045295, 0.0192596465],
        "Mono650": [0.8773469949, 0.2663571183, 0.199919444, 0.0192325637],
        "Mono685": [0.8775925081, 0.2648548355, 0.1945563456, 0.0192860556],
        "Mono725": [0.8756774317, 0.266883373, 0.21603525, 0.194527158],
        "Mono780": [0.8722125382, 0.2721842015, 0.2238493387, 0.0196295938],
        "Mono808": [0.8699458632, 0.2780141682, 0.2283300902, 0.0216592377],
        "Mono850": [0.8649280907, 0.2800907016, 0.2340131491, 0.0195446727],
        "Mono880": [0.8577996233, 0.2673899041, 0.2371926238, 0.0202034892],
        "550/660/850": [[0.8689592421, 0.2656248359, 0.1961875592, 0.0195576511], [0.8775934407, 0.2661207692, 0.1987265874, 0.0192249327],
                        [0.8653063177, 0.2798126291, 0.2337498097, 0.0193295348]],
        "490/615/808": [[0.8414604806, 0.2594283565, 0.1897271608, 0.0197180224],
                        [0.8751529643, 0.2673261446, 0.2007025375, 0.0192817427],
                        [0.868782908, 0.27845399, 0.2298671821, 0.0211305297]],
        "475/550/850": [[0.8348841674, 0.2580074987, 0.1890252099, 0.01975703], [0.8689592421, 0.2656248359, 0.1961875592, 0.0195576511],
                        [0.8653063177, 0.2798126291, 0.2337498097, 0.0193295348]]

    }}
    pixel_min_max = {"redmax": 0.0, "redmin": 65535.0,
                     "greenmax": 0.0, "greenmin": 65535.0,
                     "bluemax": 0.0, "bluemin": 65535.0}

    multiplication_values = {"red":   {"slope": 0.00, "intercept": 0.00},
                             "green": {"slope": 0.00, "intercept": 0.00},
                             "blue":  {"slope": 0.00, "intercept": 0.00},
                             "mono":  {"slope": 0.00, "intercept": 0.00}
                            }


    qr_coeffs = {}

    monominmax = {"min": 65535.0,"max": 0.0}
    imkeys_JPG = np.array(list(range(0, 255)))
    imkeys = np.array(list(range(0, 65536)))
    weeks = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = 1
    conv = None
    kcr = None
    analyze_bands = []
    modalwindow = None
    calcwindow = None
    LUTwindow = None
    M_Shutter_Window = None
    A_Shutter_Window = None
    Bandwindow = None
    Advancedwindow = None
    rdr = []
    ManualExposurewindow = None
    AutoExposurewindow = None
    BandNames = {
        "RGB": [644, 0, 0],
        "405": [405, 0, 0],
        "450": [450, 0, 0],
        "490": [490, 0, 0],
        "518": [518, 0, 0],
        "550": [550, 0, 0],
        "590": [590, 0, 0],
        "615": [615, 0, 0],
        "632": [632, 0, 0],
        "650": [650, 0, 0],
        "685": [685, 0, 0],
        "725": [725, 0, 0],
        "780": [780, 0, 0],
        "808": [808, 0, 0],
        "850": [850, 0, 0],
        "880": [880, 0, 0],
        "940": [940, 0, 0],
        "945": [945, 0, 0],
        "UVR": [870, 0, 395],
        "NGB": [850, 550, 475],
        "RGN": [660, 550, 850],
        "OCN": [615, 490, 808],

    }
    VigWindow = None
    ndvipsuedo = None
    savewindow = None
    index_to_save = None
    LUT_to_save = None
    LUT_Min = -1.0
    LUT_Max = 1.0
    array_indicator = False
    seed_pass = False
    transferoutfolder = None
    yestransfer = False
    yesdelete = False
    selection_made = False
    POLL_TIME = 3000

    slow = 0
    regs = [0] * eRegister.RG_SIZE.value
    paths = []
    pathnames = []
    driveletters = []
    source = 0
    evt = 0
    info = 0
    VENDOR_ID = 0x525
    PRODUCT_ID = 0xa4ac
    BUFF_LEN = 512
    SET_EVENT_REPORT = 1
    SET_COMMAND_REPORT = 3
    SET_REGISTER_WRITE_REPORT = 5
    SET_REGISTER_BLOCK_WRITE_REPORT = 7
    SET_REGISTER_READ_REPORT = 9
    SET_REGISTER_BLOCK_READ_REPORT = 11
    SET_CAMERA = 13
    display_image = None
    display_image_original = None
    displaymax = None
    displaymin = None
    mapscene = None
    frame = None
    legend_frame = None
    legend_scene = None
    image_loaded = False

    COLOR_CORRECTION_VECTORS = [1.398822546, -0.09047482163, 0.1619316638, -0.01290435996, 0.8994362354, 0.1134681329, 0.007306902204, -0.05995989591, 1.577814579]#101018
    regs = []
    DJIS = ["DJI Phantom 4", "DJI Phantom 4 Pro", "DJI Phantom 3a", "DJI Phantom 3p", "DJI X3"]
    SURVEYS = ["Survey1", "Survey2", "Survey3"]
    KERNELS = ["Kernel 3.2", "Kernel 14.4"]

    ANGLE_SHIFT_QR = 7

    JPGS = ["jpg", "JPG", "jpeg", "JPEG"]
    TIFS = ["tiff", "TIFF", "tif", "TIF"]

    PIX4D_VALUES = {"3.37": {   "PRINCIPALPOINT":"3.84387, 1.53139",
                                "PERSPECTIVEFOCALLENGTH":"3.37",
                                "PERSPECTIVEDISTORTION":"0, 0, 0, 0, 0"},

                    "8.25": {   "PRINCIPALPOINT":"3.84387, 1.53139",
                                "PERSPECTIVEFOCALLENGTH":"8.444407",
                                "PERSPECTIVEDISTORTION":"-0.07569, 0.059957, -0.02031, -0.01246, 0.016932"},

                    "3.5": {    "PRINCIPALPOINT":"3.524, 2.6604",
                                "PERSPECTIVEFOCALLENGTH":"3.4097",
                                "PERSPECTIVEDISTORTION":"0.058, -0.222, 0.017, 0, 0"},

                    "5.5": {    "PRINCIPALPOINT":"3.412091, 2.745396",
                                "PERSPECTIVEFOCALLENGTH":"5.5",
                                "PERSPECTIVEDISTORTION":"0, 0, 0, 0, 0"},

                    "9.6": {    "PRINCIPALPOINT":"3.412091, 2.745396",
                                "PERSPECTIVEFOCALLENGTH":"9.6706605",
                                "PERSPECTIVEDISTORTION":"-0.107494, 0.0852713, 0.114084, 0.000263678, -0.000463052"},

                    "12.0": {   "PRINCIPALPOINT":"3.412091, 2.745396",
                                "PERSPECTIVEFOCALLENGTH":"12.0",
                                "PERSPECTIVEDISTORTION":"0, 0, 0, 0, 0"},

                    "16.0": {   "PRINCIPALPOINT":"3.412091, 2.745396",
                                "PERSPECTIVEFOCALLENGTH":"16.0",
                                "PERSPECTIVEDISTORTION":"0, 0, 0, 0, 0"},

                    "35.0": {   "PRINCIPALPOINT":"3.412091, 2.745396",
                                "PERSPECTIVEFOCALLENGTH":"35.0",
                                "PERSPECTIVEDISTORTION":"0, 0, 0, 0, 0"},

    }

    CHECKED = 2 # QT creator syntax for checkState(); 2 signifies the box is checked, 0 is unchecked
    UNCHECKED = 0

    SENSOR_LOOKUP = {6: "14.4 MP", 4: "3.2 MP"}
    SHUTTER_SPEED_LOOKUP = {1: "1/32000",
                            2: "1/16000",
                            3: "1/8000",
                            4: "1/6000",
                            5: "1/4000",
                            6: "1/2000",
                            7: "1/1600",
                            8: "1/1250",
                            9: "1/1000",
                            10: "1/800",
                            11: "1/640",
                            12: "1/500",
                            13: "1/400",
                            14: "1/320",
                            15: "1/250",
                            16: "1/200",
                            17: "1/160",
                            18: "1/125",
                            19: "1/100",
                            20: "1/80",
                            21: "1/60",
                            22: "1/50",
                            23: "1/40",
                            24: "1/30",
                            25: "1/25",
                            26: "1/20",
                            27: "1/15",
                            28: "1/12",
                            29: "1/10",
                            30: "1/8",
                            31: "1/6.4",
                            32: "1/5",
                            33: "1/4",
                            34: "1/3.2",
                            35: "1/2.5",
                            36: "1/2",
                            37: "1/1" }

    ISO_VALS = (1,2,4,8,16,32)
    lensvals = None
    def __init__(self, parent=None):
        """Constructor."""
        super(MAPIR_ProcessingDockWidget, self).__init__(parent)

        self.setupUi(self)
        self.website.setStyleSheet("QPushButton {width: 20; height: 20; font-size: 18px}")
        self.version.setStyleSheet("QLabel {font-size: 18px;}")

        try:
            legend = cv2.imread(os.path.dirname(__file__) + "/lut_legend.jpg")
            legh, legw = legend.shape[:2]

            self.legend_frame = QtGui.QImage(legend.data, legw, legh, legw, QtGui.QImage.Format_Grayscale8)
            self.LUTGraphic.setPixmap(QtGui.QPixmap.fromImage(
                QtGui.QImage(self.legend_frame)))
            self.LegendLayout_2.hide()

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))

    def exitTransfer(self, drv='C'):
        tmtf = r":/dcim/tmtf.txt"

        if drv == 'C':
            while drv is not '[':
                if os.path.isdir(drv + r":/dcim/"):

                    try:
                        if not os.path.exists(drv + tmtf):
                            self.KernelLog.append("Camera mounted at drive " + drv + " leaving transfer mode")
                            file = open(drv + tmtf, "w")
                            file.close()

                    except:
                        self.KernelLog.append("Error disconnecting drive " + drv)
                drv = chr(ord(drv) + 1)

        else:
            if os.path.isdir(drv + r":/dcim/"):
                try:
                    if not os.path.exists(drv + tmtf):
                        self.KernelLog.append("Camera mounted at drive " + drv + " leaving transfer mode")
                        file = open(drv + tmtf, "w")
                        file.close()

                except:
                    self.KernelLog.append("Error disconnecting drive " + drv)

    def on_website_released(self):
        webbrowser.open('https://www.mapir.camera/')

    def on_KernelRefreshButton_released(self):
        # self.exitTransfer()
        self.ConnectKernels()

    def on_KernelConnect_released(self):
        # self.exitTransfer()
        self.ConnectKernels()

    def ConnectKernels(self):
        filter_dic = {}
        self.KernelLog.append(' ')
        all_cameras = hid.enumerate(self.VENDOR_ID, self.PRODUCT_ID)
        if all_cameras == []:
            self.KernelLog.append("No cameras found! Please check your USB connection and try again.")

        else:
            self.paths.clear()
            self.pathnames.clear()

            for cam in all_cameras:
                if cam['product_string'] == 'HID Gadget':
                    self.camera = cam['path']
                    buf = [0] * 512
                    buf[0] = self.SET_REGISTER_READ_REPORT
                    buf[1] = eRegister.RG_CAMERA_LINK_ID.value

                    arid = self.writeToKernel(buf)[2]
                    self.paths.insert(arid, cam['path'])

                    self.camera = cam['path']
                    buf = [0] * 512
                    buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
                    buf[1] = eRegister.RG_MEDIA_FILE_NAME_A.value
                    buf[2] = 3

                    res = self.writeToKernel(buf)
                    item = chr(res[2]) + chr(res[3]) + chr(res[4])
                    filter_dic[arid] = item

                    QtWidgets.QApplication.processEvents()

            self.KernelCameraSelect.blockSignals(True)
            self.KernelCameraSelect.clear()
            self.KernelCameraSelect.blockSignals(False)

            try:
                for i, path in enumerate(self.paths):
                    QtWidgets.QApplication.processEvents()
                    self.camera = path
                    buf = [0] * 512
                    buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
                    buf[1] = eRegister.RG_MEDIA_FILE_NAME_A.value
                    buf[2] = 3

                    res = self.writeToKernel(buf)
                    item = chr(res[2]) + chr(res[3]) + chr(res[4])
                    self.pathnames.append(item)

                    if i == 0:
                        item += " (Master)"

                    else:
                        item += " (Slave)"

                    #self.KernelLog.append("Found Camera: " + str(item))
                    QtWidgets.QApplication.processEvents()
                    self.KernelCameraSelect.blockSignals(True)
                    self.KernelCameraSelect.addItem(item)
                    self.KernelCameraSelect.blockSignals(False)

                for count, filt in enumerate(sorted(list(filter_dic.keys()))):
                    item = filter_dic[filt]
                    if count == 0:
                        item += " (Master)"
                    else:
                        item += " (Slave)"

                    self.KernelLog.append("Found Camera: " + str(item))

                self.camera = self.paths[0]

                try:
                    self.KernelUpdate()
                    QtWidgets.QApplication.processEvents()

                except Exception as e:
                    exc_type, exc_obj,exc_tb = sys.exc_info()
                    print(e)
                    print("Line: " + str(exc_tb.tb_lineno))
                    QtWidgets.QApplication.processEvents()

            except Exception as e:
                exc_type, exc_obj,exc_tb = sys.exc_info()
                self.KernelLog.append("Error: (" + str(e) + ' Line: ' + str(exc_tb.tb_lineno) +  ") connecting to camera, please ensure all cameras are connected properly and not in transfer mode.")
                QtWidgets.QApplication.processEvents()

    def UpdateLensID(self):
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_LENS_ID.value
        buf[2] = DROPDOW_2_LENS.get((self.KernelFilterSelect.currentText(), self.KernelLensSelect.currentText()), 255)

        self.writeToKernel(buf)

    def on_KernelLensSelect_currentIndexChanged(self):
        try:
            self.UpdateLensID()
            self.KernelUpdate()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.KernelLog.append("Error: " + e)

    def on_KernelFilterSelect_currentIndexChanged(self):
        try:
            self.UpdateLensID()
            self.KernelUpdate()

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            self.KernelLog.append("Error: " + e)

    def on_KernelArraySelect_currentIndexChanged(self):
        if not self.KernelTransferButton.isChecked():

            try:
                dval = int(self.KernelArraySelect.currentText())
                tempcam = copy.deepcopy(self.camera)

                for cam in self.paths:
                    self.camera = cam
                    buf = [0] * 512
                    buf[0] = self.SET_REGISTER_WRITE_REPORT
                    buf[1] = eRegister.RG_CAMERA_ARRAY_TYPE.value
                    buf[2] = dval
                    self.writeToKernel(buf)

                self.camera = tempcam
                self.KernelUpdate()

            except Exception as e:
                exc_type, exc_obj,exc_tb = sys.exc_info()
                self.KernelLog.append(str(e) + ' Line: ' + str(exc_tb.tb_lineno))
        QtWidgets.QApplication.processEvents()

    def on_KernelCameraSelect_currentIndexChanged(self):
        self.camera = self.paths[self.KernelCameraSelect.currentIndex()]
        if not self.KernelTransferButton.isChecked():
            try:
                self.KernelUpdate()
            except Exception as e:
                exc_type, exc_obj,exc_tb = sys.exc_info()
                self.KernelLog.append(str(e) + ' Line: ' + str(exc_tb.tb_lineno))
        QtWidgets.QApplication.processEvents()

    def on_VignetteButton_released(self):
        if self.VigWindow == None:
            self.VigWindow = Vignette(self)
        self.VigWindow.resize(385, 160)
        self.VigWindow.show()

    def on_KernelBrowserButton_released(self):
        self.present_file_select_dialog(self.KernelBrowserFile)
        try:

            if os.path.exists(self.KernelBrowserFile.text()):
                self.display_image = cv2.imread(self.KernelBrowserFile.text(), -1)
                self.index_to_save = self.display_image

                if self.display_image.dtype == np.dtype("uint16"):
                    self.display_image = self.display_image / 65535.0
                    self.display_image = self.display_image * 255.0
                    self.display_image = self.display_image.astype("uint8")
                self.displaymin = self.display_image.min()
                self.displaymax = self.display_image.max()


                self.display_image[self.display_image > self.displaymax] = self.displaymax
                self.display_image[self.display_image < self.displaymin] = self.displaymin

                if len(self.display_image.shape) > 2:
                    self.display_image = cv2.cvtColor(self.display_image, cv2.COLOR_BGR2RGB)
                else:
                    self.display_image = cv2.cvtColor(self.display_image, cv2.COLOR_GRAY2RGB)
                self.display_image_original = copy.deepcopy(self.display_image)
                h, w = self.display_image.shape[:2]

                self.image_loaded = True
                self.stretchView()
                #self.ViewerCalcButton.blockSignals(True)
                self.LUTButton.blockSignals(True)
                self.LUTBox.blockSignals(True)
                self.ViewerIndexBox.blockSignals(True)
                self.ViewerStretchBox.blockSignals(True)

                self.ViewerCalcButton.setStyleSheet("QComboBox {width: 116; height: 27;}")
                self.ViewerCalcButton.setEnabled(True)
                self.LUTButton.setEnabled(False)
                self.LUTBox.setEnabled(False)
                self.LUTBox.setChecked(False)
                self.ViewerIndexBox.setEnabled(False)
                self.ViewerIndexBox.setChecked(False)
                self.ViewerStretchBox.setChecked(True)

                #self.ViewerCalcButton.blockSignals(False)
                self.LUTButton.blockSignals(False)
                self.LUTBox.blockSignals(False)
                self.ViewerIndexBox.blockSignals(False)
                self.ViewerStretchBox.blockSignals(False)

                self.savewindow = None
                self.LUTwindow = None
                self.LUT_to_save = None
                self.LUT_Max = 1.0
                self.LUT_Min = -1.0
                self.updateViewer(keepAspectRatio=True)

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(str(e) + ' Line: ' + str(exc_tb.tb_lineno))
    def on_ViewerStretchBox_toggled(self):
        self.stretchView()

    def stretchView(self):
        try:
            if self.image_loaded:
                if self.ViewerStretchBox.isChecked():
                    h, w = self.display_image.shape[:2]

                    if len(self.display_image.shape) > 2:
                        self.display_image[:, :, 0] = cv2.equalizeHist(self.display_image[:, :, 0])
                        self.display_image[:, :, 1] = cv2.equalizeHist(self.display_image[:, :, 1])
                        self.display_image[:, :, 2] = cv2.equalizeHist(self.display_image[:, :, 2])
                    else:
                        self.display_image = cv2.equalizeHist(self.display_image)
                    if not (self.ViewerIndexBox.isChecked() or self.LUTBox.isChecked()):
                        self.LegendLayout_2.hide()
                        if len(self.display_image.shape) > 2:
                            self.frame = QtGui.QImage(self.display_image.data, w, h, w * 3, QtGui.QImage.Format_RGB888)
                        else:
                            self.frame = QtGui.QImage(self.display_image.data, w, h, w, QtGui.QImage.Format_RGB888)
                else:
                    if not (self.ViewerIndexBox.isChecked() or self.LUTBox.isChecked()):
                        self.LegendLayout_2.hide()
                        h, w = self.display_image_original.shape[:2]
                        if len(self.display_image_original.shape) > 2:
                            self.frame = QtGui.QImage(self.display_image_original.data, w, h, w * 3, QtGui.QImage.Format_RGB888)
                        else:
                            self.frame = QtGui.QImage(self.display_image_original.data, w, h, w, QtGui.QImage.Format_RGB888)
                self.updateViewer(keepAspectRatio=False)
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))
    def on_ViewerIndexBox_toggled(self):
        self.applyRaster()

    def applyRaster(self):
        try:
            h, w = self.display_image.shape[:2]
            if self.LUTBox.isChecked():
                pass
            else:
                if self.ViewerIndexBox.isChecked():
                    self.frame = QtGui.QImage(self.calcwindow.ndvi.data, w, h, w, QtGui.QImage.Format_Grayscale8)
                    legend = cv2.imread(os.path.dirname(__file__) + r'\lut_legend.jpg', 0).astype("uint8")
                    # legend = cv2.cvtColor(legend, cv2.COLOR_GRAY2RGB)
                    legh, legw = legend.shape[:2]

                    self.legend_frame = QtGui.QImage(legend.data, legw, legh, legw, QtGui.QImage.Format_Grayscale8)
                    self.LUTGraphic.setPixmap(QtGui.QPixmap.fromImage(
                        QtGui.QImage(self.legend_frame)))
                    self.LegendLayout_2.show()
                else:
                    self.LegendLayout_2.hide()
                    self.frame = QtGui.QImage(self.display_image.data, w, h, w * 3, QtGui.QImage.Format_RGB888)
                self.updateViewer(keepAspectRatio=False)
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))

    def updateViewer(self, keepAspectRatio = True):
        self.mapscene = QtWidgets.QGraphicsScene()

        self.mapscene.addPixmap(QtGui.QPixmap.fromImage(
            QtGui.QImage(self.frame)))

        self.KernelViewer.setScene(self.mapscene)
        if keepAspectRatio:
            self.KernelViewer.fitInView(self.mapscene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.KernelViewer.setFocus()
        # self.KernelViewer.setWheelAction(2)
        QtWidgets.QApplication.processEvents()

    def on_LUTBox_toggled(self):
        self.applyLUT()

    def applyLUT(self):
        try:
            h, w = self.display_image.shape[:2]
            if self.LUTBox.isChecked():
                if self.LUTwindow.ClipOption.currentIndex() == 1:
                    self.frame = QtGui.QImage(self.ndvipsuedo.data, w, h, w * 4, QtGui.QImage.Format_RGBA8888)

                else:
                    self.frame = QtGui.QImage(self.ndvipsuedo.data, w, h, w * 3, QtGui.QImage.Format_RGB888)

                legend = cv2.imread(os.path.dirname(__file__) + r'\lut_legend_rgb.jpg', -1).astype("uint8")
                legend = cv2.cvtColor(legend, cv2.COLOR_BGR2RGB)
                legh, legw = legend.shape[:2]

                self.legend_frame = QtGui.QImage(legend.data, legw, legh, legw * 3, QtGui.QImage.Format_RGB888)
                self.LUTGraphic.setPixmap(QtGui.QPixmap.fromImage(
                    QtGui.QImage(self.legend_frame)))
                self.LegendLayout_2.show()
            else:
                legend = cv2.imread(os.path.dirname(__file__) + r'\lut_legend.jpg', 0).astype("uint8")
                # legend = cv2.cvtColor(legend, cv2.COLOR_GRAY2RGB)
                legh, legw = legend.shape[:2]

                self.legend_frame = QtGui.QImage(legend.data, legw, legh, legw, QtGui.QImage.Format_Grayscale8)
                self.LUTGraphic.setPixmap(QtGui.QPixmap.fromImage(
                    QtGui.QImage(self.legend_frame)))

                if self.ViewerIndexBox.isChecked():
                    self.LegendLayout_2.show()
                    self.frame = QtGui.QImage(self.calcwindow.ndvi.data, w, h, w, QtGui.QImage.Format_Grayscale8)

                else:
                    self.LegendLayout_2.hide()
                    self.frame = QtGui.QImage(self.display_image.data, w, h, w * 3, QtGui.QImage.Format_RGB888)
            self.updateViewer(keepAspectRatio=False)
            QtWidgets.QApplication.processEvents()

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))

    def on_ViewerSaveButton_released(self):
        if self.savewindow == None:
            self.savewindow = SaveDialog(self)
        self.savewindow.resize(385, 110)
        self.savewindow.exec_()

        QtWidgets.QApplication.processEvents()

    def on_LUTButton_released(self):
        if self.LUTwindow == None:
            self.LUTwindow = Applicator(self)
        self.LUTwindow.resize(385, 160)
        self.LUTwindow.show()

        QtWidgets.QApplication.processEvents()
    def on_ViewerCalcButton_released(self):
        if self.LUTwindow == None:
            self.calcwindow = Calculator(self)

        self.calcwindow.resize(685, 250)
        self.calcwindow.show()
        QtWidgets.QApplication.processEvents()

    def kernel_viewer_zoom_in(self):
        factor = 1.15
        self.KernelViewer.scale(factor, factor)

    def kernel_viewer_zoom_out(self):
        factor = 1.15
        self.KernelViewer.scale(1/factor, 1/factor)

    def on_ZoomIn_released(self):
        if self.image_loaded == True:
            try:
                self.kernel_viewer_zoom_in()
            except Exception as e:
                exc_type, exc_obj,exc_tb = sys.exc_info()
                print(e)
                print("Line: " + str(exc_tb.tb_lineno))
    def on_ZoomOut_released(self):
        if self.image_loaded == True:
            try:
                self.kernel_viewer_zoom_out()
            except Exception as e:
                exc_type, exc_obj,exc_tb = sys.exc_info()
                print(e)
                print("Line: " + str(exc_tb.tb_lineno))
    def on_ZoomToFit_released(self):
        self.mapscene = QtWidgets.QGraphicsScene()
        self.mapscene.addPixmap(QtGui.QPixmap.fromImage(
            QtGui.QImage(self.frame)))

        self.KernelViewer.setScene(self.mapscene)
        self.KernelViewer.fitInView(self.mapscene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.KernelViewer.setFocus()
        QtWidgets.QApplication.processEvents()
    # TODO Block
    # def wheelEvent(self, event):
    #     if self.image_loaded == True:
    #         try:
    #
    #         except Exception as e:
    # exc_type, exc_obj,exc_tb = sys.exc_info()
    #             print(str(e) + ' ) + str(exc_tb.tb_lineno

    # def eventFilter(self, obj, event):
    #
    #     if self.image_loaded == True:
    #         try:
    #             self.KernelViewer.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
    #             factor = 1.15
    #             if int(event.angleDelta().y()) > 0:
    #                 self.KernelViewer.scale(factor, factor)
    #             else:
    # def wheelEvent(self, event):
    #     if self.image_loaded == True:
    #         try:
    #             self.KernelBrowserViewer.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
    #             factor = 1.15
    #             if int(event.angleDelta().y()) > 0:
    #                 self.KernelBrowserViewer.scale(factor, factor)
    #             else:
    #                 self.KernelBrowserViewer.scale(1.0/factor, 1.0/factor)
    #         except Exception as e:
    # exc_type, exc_obj,exc_tb = sys.exc_info()
    #             print(str(e) + ' ) + str(selfexc_tb.tb_lineno):
    # TODO end block
    def resizeEvent(self, event):
        # redraw the image in the viewer every time the window is resized
        if self.image_loaded == True:
            self.mapscene = QtWidgets.QGraphicsScene()
            self.mapscene.addPixmap(QtGui.QPixmap.fromImage(
                QtGui.QImage(self.frame)))

            self.KernelViewer.setScene(self.mapscene)

            self.KernelViewer.setFocus()
            QtWidgets.QApplication.processEvents()

    # def getIMURegisterString(self, label, sign, highByte, lowByte):
    #     return label + str(convert_imu_register_value(self.getRegister(sign), self.getRegister(highByte), self.getRegister(lowByte))) + '°'

    # def appendIMURegisterValueToKernelPanel(self, label, signEnum, highByteEnum, lowByteEnum):
    #     self.KernelPanel.append(self.getIMURegisterString(label, signEnum.value, highByteEnum.value, lowByteEnum.value))

    def get_imu_value_string(self, label, reg_values):
        return label + str(round(convert_imu_reg_values_to_float(reg_values),4)) + '°'

    def append_imu_value_to_kernel_panel(self, label, reg_values):
        self.KernelPanel.append(self.get_imu_value_string(label, reg_values))

    def firmware_version_is_old(self):
        firmware_id = self.getRegister(eRegister.RG_FIRMWARE_ID)
        firmware_minor_id = self.getRegister(eRegister.RG_FIRMWARE_MINOR_ID)
        firmware_internal_version = self.getRegister(eRegister.RG_FIRMWARE_INTERNAL_VERSION)

        return firmware_id == 2 and firmware_minor_id == 0 and firmware_internal_version == 0

    # def log_trigger_debounce_to_kernel_panel(self):
    #     self.KernelPanel.append("Trigger Debounce High: " + str(self.getRegister(eRegister.RG_DEBOUNCE_HIGH.value)))
    #     self.KernelPanel.append("Trigger Debounce Low: " + str(self.getRegister(eRegister.RG_DEBOUNCE_LOW.value)))

    def log_yaw_pitch_roll_to_kernel_panel(self):
        self.KernelPanel.append("Last Photo Captured Orientation:")
        self.append_imu_value_to_kernel_panel(
            'Yaw: ', [
                self.getRegister(eRegister.RG_ACC_YAW_0.value),
                self.getRegister(eRegister.RG_ACC_YAW_1.value),
                self.getRegister(eRegister.RG_ACC_YAW_2.value),
                self.getRegister(eRegister.RG_ACC_YAW_3.value),
            ])
        self.append_imu_value_to_kernel_panel(
            'Pitch: ', [
                self.getRegister(eRegister.RG_ACC_PITCH_0.value),
                self.getRegister(eRegister.RG_ACC_PITCH_1.value),
                self.getRegister(eRegister.RG_ACC_PITCH_2.value),
                self.getRegister(eRegister.RG_ACC_PITCH_3.value),
            ])
        self.append_imu_value_to_kernel_panel(
            'Roll: ', [
                self.getRegister(eRegister.RG_ACC_ROLL_0.value),
                self.getRegister(eRegister.RG_ACC_ROLL_1.value),
                self.getRegister(eRegister.RG_ACC_ROLL_2.value),
                self.getRegister(eRegister.RG_ACC_ROLL_3.value),
            ])

    def log_firmware_version_to_kernel_panel(self):
        if self.firmware_version_is_old():
            version = "Camera Firmware: 1.2.0"
        else:
            version = "Camera Firmware: " + str(self.getRegister(eRegister.RG_FIRMWARE_ID.value)) + '.' + str(self.getRegister(eRegister.RG_FIRMWARE_MINOR_ID)) + '.' + str(self.getRegister(eRegister.RG_FIRMWARE_INTERNAL_VERSION))
        self.KernelPanel.append(version)

    def KernelUpdate(self):
        try:
            self.KernelExposureMode.blockSignals(True)
            self.KernelVideoOut.blockSignals(True)
            self.KernelFolderCount.blockSignals(True)
            self.KernelBeep.blockSignals(True)
            self.KernelPWMSignal.blockSignals(True)
            self.KernelLensSelect.blockSignals(True)
            self.KernelFilterSelect.blockSignals(True)
            self.KernelArraySelect.blockSignals(True)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
            buf[1] = eRegister.RG_CAMERA_SETTING.value
            buf[2] = eRegister.RG_SIZE.value

            res = self.writeToKernel(buf)[2:]
            self.regs = res



            shutter = self.getRegister(eRegister.RG_SHUTTER.value)
            if shutter == 0:
                self.KernelExposureMode.setCurrentIndex(0)
                self.KernelMESettingsButton.setEnabled(False)
                self.KernelAESettingsButton.setEnabled(True)
            else:
                self.KernelExposureMode.setCurrentIndex(1)
                self.KernelMESettingsButton.setEnabled(True)
                self.KernelAESettingsButton.setEnabled(False)



            dac = self.getRegister(eRegister.RG_DAC.value)

            hdmi = self.getRegister(eRegister.RG_HDMI.value)

            if hdmi == 1 and dac == 1:
                self.KernelVideoOut.setCurrentIndex(3)
            elif hdmi == 0 and dac == 1:
                self.KernelVideoOut.setCurrentIndex(2)
            elif hdmi == 1 and dac == 0:
                self.KernelVideoOut.setCurrentIndex(1)
            else:
                self.KernelVideoOut.setCurrentIndex(0)


            media = self.getRegister(eRegister.RG_MEDIA_FILES_CNT.value)
            self.KernelFolderCount.setCurrentIndex(media)

            sensor = self.SENSOR_LOOKUP.get(self.getRegister(eRegister.RG_SENSOR_ID.value), "N/A")

            if sensor == "14.4 MP":
                self.KernelLensSelect.clear()
                self.KernelLensSelect.addItems(["3.37mm", "8.25mm"])

                self.KernelFilterSelect.clear()
                self.KernelFilterSelect.addItems(["RGB", "UVR", "NGB", "RGN", "OCN", "NO FILTER"])

            else:
                self.KernelLensSelect.clear()
                self.KernelLensSelect.addItems(["3.5mm", "5.5mm", "9.6mm", "12.0mm", "16.0mm", "35.0mm"])

                self.KernelFilterSelect.clear()
                kernel_3_2_filter_list = [
                                        "250",
                                        "350",
                                        "390",
                                        "405",
                                        "450",
                                        "490",
                                        "510",
                                        "518",
                                        "550",
                                        "590",
                                        "615",
                                        "632",
                                        "650",
                                        "685",
                                        "709",
                                        "725",
                                        "750",
                                        "780",
                                        "808",
                                        "830",
                                        "850",
                                        "880",
                                        "940",
                                        "945",
                                        "1000",
                                        "NO FILTER"]

                self.KernelFilterSelect.addItems(kernel_3_2_filter_list)

            lens_id_reg_value = self.getRegister(eRegister.RG_LENS_ID.value)
            default_lens_lookup = LENS_LOOKUP.get(202)
            # tens = math.floor(lens_id_reg_value / 10)
            # ones = lens_id_reg_value % 10
            # if ((tens in [2,5,8,11,14,17]) and (ones in [5,6,7,8,9])) or tens == 19:
            #     lens_id_reg_value = 202
            lens_lookup_data = LENS_LOOKUP.get(lens_id_reg_value, default_lens_lookup)
            fil = str(lens_lookup_data[2])
            self.KernelFilterSelect.setCurrentIndex(self.KernelFilterSelect.findText(fil))

            lens = str(lens_lookup_data[0][0]) + "mm"
            self.KernelLensSelect.setCurrentIndex(self.KernelLensSelect.findText(lens))

            beep = self.getRegister(eRegister.RG_BEEPER_ENABLE.value)
            # if beep != 0:
            #     self.KernelBeep.setChecked(True)
            # else:
            #     self.KernelBeep.setChecked(False)
            self.KernelBeep.setChecked(beep != 0)

            pwm = self.getRegister(eRegister.RG_PWM_TRIGGER.value)
            # if pwm != 0:
            #     self.KernelPWMSignal.setChecked(True)
            # else:
            #     self.KernelPWMSignal.setChecked(False)
            self.KernelPWMSignal.setChecked(pwm != 0)

            self.KernelPanel.clear()

            self.KernelPanel.append("Sensor: " + self.SENSOR_LOOKUP.get(self.getRegister(eRegister.RG_SENSOR_ID.value), "N/A"))
            self.KernelPanel.append("Lens: " + lens)
            self.KernelPanel.append("Filter: " + fil)

            if shutter == 0:
                self.KernelPanel.append("Shutter: Auto")
            else:
                self.KernelPanel.append("Shutter: " + str(self.SHUTTER_SPEED_LOOKUP.get(self.getRegister(eRegister.RG_SHUTTER.value), "N/A")) + " sec")
            self.KernelPanel.append("ISO: " + str(self.getRegister(eRegister.RG_ISO.value)) + "00")

            self.KernelPanel.append('')


            buf = [0] * 512
            buf[0] = self.SET_REGISTER_READ_REPORT
            buf[1] = eRegister.RG_CAMERA_ARRAY_TYPE.value
            artype = str(self.writeToKernel(buf)[2])
            self.KernelArraySelect.setCurrentIndex(int(self.KernelArraySelect.findText(artype)))
            self.KernelPanel.append("Array Type: " + str(artype))
            buf = [0] * 512
            buf[0] = self.SET_REGISTER_READ_REPORT
            buf[1] = eRegister.RG_CAMERA_LINK_ID.value
            arid = self.writeToKernel(buf)[2]
            self.KernelPanel.append("Array ID: " + str(arid))

            self.KernelPanel.append('')
            # self.log_acceleration_values_to_kernel_panel()
            self.log_yaw_pitch_roll_to_kernel_panel()
            self.KernelPanel.append('')

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
            buf[1] = eRegister.RG_CAMERA_ID.value
            buf[2] = 6
            st = self.writeToKernel(buf)
            serno = str(chr(st[2]) + chr(st[3]) + chr(st[4]) + chr(st[5]) + chr(st[6]) + chr(st[7]))

            self.KernelPanel.append("Serial Number: " + serno)
            self.log_firmware_version_to_kernel_panel()
            self.KernelPanel.append('')
            # self.log_trigger_debounce_to_kernel_panel()

            # self.KernelPanel.append("Camera Firmware: " + str(self.getRegister(eRegister.RG_FIRMWARE_ID.value)) + '.' + str(self.getRegister(eRegister.RG_FIRMWARE_MINOR_ID)) + '.' + str(self.getRegister(eRegister.RG_FIRMWARE_INTERNAL_VERSION)))

            self.KernelExposureMode.blockSignals(False)

            self.KernelVideoOut.blockSignals(False)
            self.KernelFolderCount.blockSignals(False)
            self.KernelBeep.blockSignals(False)
            self.KernelPWMSignal.blockSignals(False)
            self.KernelLensSelect.blockSignals(False)
            self.KernelFilterSelect.blockSignals(False)
            self.KernelArraySelect.blockSignals(False)
            QtWidgets.QApplication.processEvents()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.KernelLog.append("Error: (" + str(e) + ' Line: ' + str(
                exc_tb.tb_lineno) + ") updating interface.")

    def on_KernelFolderButton_released(self):
        self.present_folder_select_dialog(self.KernelTransferFolder)

    cancel_auto = False
    def on_KernelAutoCancel_released(self):
        self.cancel_auto = True

    def present_folder_select_dialog(self, component):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            component.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
            instring.truncate(0)
            instring.seek(0)
            instring.write(component.text())

    def present_file_select_dialog(self, component):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            component.setText(QtWidgets.QFileDialog.getOpenFileName(directory=instring.read())[0])
            instring.truncate(0)
            instring.seek(0)
            instring.write(component.text())

    def on_KernelBandButton1_released(self):
        self.present_folder_select_dialog(self.KernelBand1)
    def on_KernelBandButton2_released(self):
        self.present_folder_select_dialog(self.KernelBand2)
    def on_KernelBandButton3_released(self):
        self.present_folder_select_dialog(self.KernelBand3)
    def on_KernelBandButton4_released(self):
        self.present_folder_select_dialog(self.KernelBand4)
    def on_KernelBandButton5_released(self):
        self.present_folder_select_dialog(self.KernelBand5)
    def on_KernelBandButton6_released(self):
        self.present_folder_select_dialog(self.KernelBand6)

    def on_KernelRenameOutputButton_released(self):
        self.present_folder_select_dialog(self.KernelRenameOutputFolder)

    @staticmethod
    def get_filenames_to_be_changed(kernel_band_dir_names):
        all_folders = []
        for i in range(6):
            folder = []
            if len(kernel_band_dir_names[i]) > 0:
                folder.extend(glob.glob(kernel_band_dir_names[i] + os.sep + "*.tif?"))
                folder.extend(glob.glob(kernel_band_dir_names[i] + os.sep + "*.jpg"))
                folder.extend(glob.glob(kernel_band_dir_names[i] + os.sep + "*.jpeg"))
            all_folders.append(folder)
        return all_folders

    def on_KernelRenameButton_released(self):
        try:
            kernel_band_dir_names = [
                self.KernelBand1.text(),
                self.KernelBand2.text(),
                self.KernelBand3.text(),
                self.KernelBand4.text(),
                self.KernelBand5.text(),
                self.KernelBand6.text(),
            ]
            all_folders = MAPIR_Processing.get_filenames_to_be_changed(kernel_band_dir_names)

            outfolder = self.KernelRenameOutputFolder.text()
            if not os.path.exists(outfolder):
                os.mkdir(outfolder)

            underscore = 1
            for folder in all_folders:

                counter = 1

                if len(folder) > 0:
                    if self.KernelRenameMode.currentIndex() == 0:
                        for tiff in folder:
                            shutil.copyfile(tiff, outfolder + os.sep + "IMG_" + str(counter).zfill(5) + '_' + str(underscore) + '.' + tiff.split('.')[1])
                            counter = counter + 1
                        underscore = underscore + 1
                    elif self.KernelRenameMode.currentIndex() == 2:
                        for tiff in folder:
                            shutil.copyfile(tiff, outfolder + os.sep + str(self.KernelRenamePrefix.text()) + tiff.split(os.sep)[-1])
                            counter = counter + 1
                        underscore = underscore + 1
            self.KernelLog.append("Finished Renaming All Files.")
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))

    def getXML(self):
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
        buf[1] = eRegister.RG_MEDIA_FILE_NAME_A.value
        buf[2] = 3
        res = self.writeToKernel(buf)

        filt = chr(res[2]) + chr(res[3]) + chr(res[4])

        buf = [0] * 512
        buf[0] = self.SET_REGISTER_BLOCK_READ_REPORT
        buf[1] = eRegister.RG_CAMERA_SETTING.value
        buf[2] = eRegister.RG_SIZE.value

        res = self.writeToKernel(buf)
        self.regs = res[2:]
        sens = str(self.getRegister(eRegister.RG_SENSOR_ID.value))
        lens = str(self.getRegister(eRegister.RG_LENS_ID.value))

        buf = [0] * 512
        buf[0] = self.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_CAMERA_ARRAY_TYPE.value
        artype = str(self.writeToKernel(buf)[2])

        buf = [0] * 512
        buf[0] = self.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_CAMERA_LINK_ID.value
        arid = str(self.writeToKernel(buf)[2])

        return (filt, sens, lens, arid, artype)
    def on_KernelMatrixButton_toggled(self):
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_BLOCK_WRITE_REPORT
        buf[1] = eRegister.RG_COLOR_GAMMA_START.value
        buf[2] = 192
        try:
            if self.KernelMatrixButton.isChecked():
                mtx = (np.array([3.2406,-1.5372,-0.498,-0.9689,1.8756,0.0415,0.0557,-0.2040,1.0570]) * 16384.0).astype("uint32")
                offset = (np.array([0.0, 0.0, 0.0])).astype("uint32")
                gamma = (np.array([7.0,0.0,6.5,3.0,6.0,8.0,5.5,13.0,5.0,22.0,4.5,38.0,3.5,102.0,2.5,230.0,1.75,422.0,1.25,679.0,0.875,1062.0,0.625, 1575.0]) * 16.0).astype("uint32")
                # buf[3::] = struct.pack("<36i", *(mtx.tolist() + offset.tolist() + gamma.tolist()))
            else:
                mtx = (np.array([1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0]) * 16384.0).astype("uint32")
                offset = (np.array([0.0, 0.0, 0.0])).astype("uint32")
                gamma = (np.array([1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0,1.0,0.0]) * 16.0).astype("uint32")
            buf[3::] = struct.pack("<36L", *(mtx.tolist() + gamma.tolist() + offset.tolist()))

            # for i in range(len(buf)):
            #     buf[i] = int(buf[i])
            self.writeToKernel(buf)
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            self.KernelLog.append("Error: " + str(e) + ' Line: ' + str(exc_tb.tb_lineno))
    def getAvailableDrives(self):
        if 'Windows' not in platform.system():
            return []
        drive_bitmask = ctypes.cdll.kernel32.GetLogicalDrives()
        return list(itertools.compress(string.ascii_uppercase, map(lambda x: ord(x) - ord('0'), bin(drive_bitmask)[:1:-1])))
    def on_KernelTransferButton_toggled(self):
        self.KernelLog.append(' ')
        currentcam = None
        try:
            if not self.camera:
                raise ValueError('Device not found')
            else:
                currentcam = self.camera

            if self.KernelTransferButton.isChecked():
                self.driveletters.clear()


                # if self.KernelCameraSelect.currentIndex() == 0:
                try:

                    for place, cam in enumerate(self.paths):
                        self.camera = cam
                        QtWidgets.QApplication.processEvents()
                        numds = win32api.GetLogicalDriveStrings().split(':\\\x00')[:-1]

                        # time.sleep(2)
                        xmlret = self.getXML()
                        buf = [0] * 512
                        buf[0] = self.SET_COMMAND_REPORT
                        buf[1] = eCommand.CM_TRANSFER_MODE.value
                        self.writeToKernel(buf)
                        self.KernelLog.append("Camera " + str(self.pathnames[self.paths.index(cam)]) + " entering Transfer mode")
                        QtWidgets.QApplication.processEvents()
                        treeroot = ET.parse(modpath + os.sep + "template.kernelconfig")
                        treeroot.find("Filter").text = xmlret[0]
                        treeroot.find("Sensor").text = xmlret[1]
                        treeroot.find("Lens").text = xmlret[2]
                        treeroot.find("ArrayID").text = xmlret[3]
                        treeroot.find("ArrayType").text = xmlret[4]
                        keep_looping = True
                        while keep_looping:
                            numds = set(numds)
                            numds1 = set(win32api.GetLogicalDriveStrings().split(':\\\x00')[:-1])
                            if numds == numds1:
                                pass
                            else:

                                drv = list(numds1 - numds)[0]
                                if len(drv) == 1:
                                    self.driveletters.append(drv)

                                    self.KernelLog.append("Camera " + str(self.pathnames[self.paths.index(cam)]) + " successfully connected to drive " + drv + ":" + os.sep + "\n")
                                    files = glob.glob(drv + r":" + os.sep + r"dcim/*/*.[tm]*", recursive=True)
                                    folders = glob.glob(drv + r":" + os.sep + r"dcim/*/")
                                    if folders:
                                        for fold in folders:
                                            if os.path.exists(fold + str(self.pathnames[self.paths.index(cam)]) + ".kernelconfig"):
                                                os.unlink(fold + str(self.pathnames[self.paths.index(cam)]) + ".kernelconfig")
                                            #treeroot.write(fold + str(self.pathnames[self.paths.index(cam)]) + ".kernelconfig")
                                    else:
                                        if not os.path.exists(drv + r":" + os.sep + r"dcim" + os.sep + str(self.pathnames[self.paths.index(cam)])):
                                            os.mkdir(drv + r":" + os.sep + r"dcim" + os.sep + str(self.pathnames[self.paths.index(cam)]))
                                        #treeroot.write(
                                            #drv + r":" + os.sep + r"dcim" + os.sep + str(self.pathnames[self.paths.index(cam)]) + ".kernelconfig")

                                    keep_looping = False


                                else:
                                    numds = win32api.GetLogicalDriveStrings().split(':\\\x00')[:-1]
                                QtWidgets.QApplication.processEvents()



                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    self.KernelLog.append(str(e))
                    self.KernelLog.append("Line: " + str(exc_tb.tb_lineno))
                    QtWidgets.QApplication.processEvents()
                    self.camera = currentcam

                self.camera = currentcam






                self.modalwindow = KernelTransfer(self)
                self.modalwindow.resize(400, 200)
                self.modalwindow.exec_()
                # self.KernelLog.append("We made it out of transfer window")
                if self.yestransfer:
                    # self.KernelLog.append("Transfer was enabled")
                    for place, drv in enumerate(self.driveletters):
                        ix = place + 1
                        self.KernelLog.append("Extracting images from Camera " + str(ix) + " of " + str(len(self.driveletters)) + ", at drive " + drv + r':')
                        QtWidgets.QApplication.processEvents()
                        if os.path.isdir(drv + r":" + os.sep + r"dcim"):
                            # try:
                            folders = glob.glob(drv + r":" + os.sep + r"dcim/*/")
                            files = glob.glob(drv + r":" + os.sep + r"dcim/*/*", recursive=True)
                            threechar = ''
                            try:
                                threechar = files[0].split(os.sep)[-1][1:4]
                            except Exception as e:
                                self.KernelLog.append(r"No files detected in drive " + drv + r'. Moving to next camera.')
                                pass
                            for fold in folders:


                                if os.path.exists(self.transferoutfolder + os.sep + threechar):
                                    foldercount = 1
                                    endloop = False
                                    while endloop is False:
                                        outdir = self.transferoutfolder + os.sep + threechar + '_' + str(foldercount)
                                        if os.path.exists(outdir):
                                            foldercount += 1
                                        else:
                                            shutil.copytree(fold, outdir)
                                            endloop = True
                                else:
                                    outdir = self.transferoutfolder + os.sep + threechar
                                    shutil.copytree(fold, outdir)
                                QtWidgets.QApplication.processEvents()
                                # for file in files:
                                #     # if file.split(os.sep)[-1][1:4] == threechar:

                                # else:
                                #     threechar = file.split(os.sep)[-1][1:4]
                                #     os.mkdir(self.transferoutfolder + os.sep + threechar)
                                #     shutil.copy(file, self.transferoutfolder + os.sep + threechar)
                                QtWidgets.QApplication.processEvents()
                            if threechar:
                                self.KernelLog.append("Finished extracting images from Camera " + str(threechar) + " number " + str(place + 1) + " of " + str(len(self.driveletters)) + ", at drive " + drv + r':' + "\n")
                            QtWidgets.QApplication.processEvents()
                        else:
                            self.KernelLog.append("No DCIM folder found in drive " + str(drv) + r":")
                            QtWidgets.QApplication.processEvents()
                    self.yestransfer = False

                if self.yesdelete:
                    for drv in self.driveletters:
                        if os.path.isdir(drv + r":" + os.sep + r"dcim"):
                            files = glob.glob(drv + r":" + os.sep + r"dcim/*/*")
                            self.KernelLog.append("Deleting files from drive " + str(drv))

                            for file in files:
                                os.unlink(file)
                            folds = glob.glob(drv + r":" + os.sep + r"dcim/*")

                            try:
                                for file in folds:
                                    os.unlink(file)

                            except Exception as e:
                                pass

                            self.KernelLog.append("Finished deleting files from drive " + str(drv) + "\n")


                    self.yesdelete = False
                    # self.modalwindow = KernelDelete(self)
                    # self.modalwindow.resize(400, 200)
                    # self.modalwindow.exec_()

            else:
                for place, cam in enumerate(self.paths):
                    try:
                        self.camera = cam
                        self.exitTransfer(self.driveletters[place])
                    except:

                        pass
            self.camera = currentcam
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            # self.exitTransfer()
            # self.KernelTransferButton.setChecked(False)
            self.KernelLog.append("Error: " + str(e) + ' Line: ' + str(exc_tb.tb_lineno))

            QtWidgets.QApplication.processEvents()
            self.camera = currentcam




    def on_KernelExposureMode_currentIndexChanged(self):
        # self.KernelExposureMode.blockSignals(True)
        if self.KernelExposureMode.currentIndex() == 1: #Manual

            self.KernelMESettingsButton.setEnabled(True)
            self.KernelAESettingsButton.setEnabled(False)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_SHUTTER.value
            buf[2] = 9

            res = self.writeToKernel(buf)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_ISO.value
            buf[2] = 1

            res = self.writeToKernel(buf)

            QtWidgets.QApplication.processEvents()
        else: #Auto

            self.KernelMESettingsButton.setEnabled(False)
            self.KernelAESettingsButton.setEnabled(True)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_SHUTTER.value
            buf[2] = 0

            res = self.writeToKernel(buf)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_AE_SELECTION.value
            # buf[2] = self.AutoAlgorithm.currentIndex()
            res = self.writeToKernel(buf)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_AE_MAX_SHUTTER.value
            # buf[2] = self.AutoMaxShutter.currentIndex()

            res = self.writeToKernel(buf)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_AE_MIN_SHUTTER.value
            # buf[2] = self.AutoMinShutter.currentIndex()

            res = self.writeToKernel(buf)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_AE_MAX_GAIN.value
            # buf[2] = self.AutoMaxISO.currentIndex()

            res = self.writeToKernel(buf)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_AE_F_STOP.value
            # buf[2] = self.AutoFStop.currentIndex()

            res = self.writeToKernel(buf)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_AE_GAIN.value
            # buf[2] = self.AutoGain.currentIndex()

            res = self.writeToKernel(buf)

            buf = [0] * 512
            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_AE_SETPOINT.value
            # buf[2] = self.AutoSetpoint.currentIndex()

            res = self.writeToKernel(buf)

            QtWidgets.QApplication.processEvents()
        # self.KernelExposureMode.blockSignals(False)
    def on_KernelAESettingsButton_released(self):
        self.A_Shutter_Window = A_EXP_Control(self)
        self.A_Shutter_Window.resize(350, 350)
        self.A_Shutter_Window.exec_()
        # self.KernelUpdate()
    def on_KernelMESettingsButton_released(self):
        self.M_Shutter_Window = M_EXP_Control(self)
        self.M_Shutter_Window.resize(250, 125)
        self.M_Shutter_Window.exec_()
        # self.KernelUpdate()


    def on_KernelCaptureButton_released(self):
        # if self.KernelCameraSelect.currentIndex() == 0:
        for cam in self.paths:
            self.camera = cam
            self.captureImage()
        self.camera = self.paths[0]
        # else:
        #     self.captureImage()
    def captureImage(self):
        try:
            buf = [0] * 512

            buf[0] = self.SET_COMMAND_REPORT
            if self.KernelCaptureMode.currentIndex() == 0:



                buf[1] = eCommand.CM_CAPTURE_PHOTO.value


            elif self.KernelCaptureMode.currentIndex() == 1:
                buf[1] = eCommand.CM_CONTINUOUS.value

            elif self.KernelCaptureMode.currentIndex() == 2:

                buf[1] = eCommand.CM_TIME_LAPSE.value

            elif self.KernelCaptureMode.currentIndex() == 3:

                buf[1] = eCommand.CM_RECORD_VIDEO.value
            elif self.KernelCaptureMode.currentIndex() == 4:

                buf[1] = eCommand.CM_RECORD_LOOPING_VIDEO.value
            else:
                self.KernelLog.append("Invalid capture mode.")

            if self.capturing == False:
                buf[2] = 1
                self.capturing = True
            else:
                buf[2] = 0
                self.capturing = False


            res = self.writeToKernel(buf)

            self.KernelUpdate()
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))


    def getRegister(self, code):
        if code < eRegister.RG_SIZE.value:
            return self.regs[code]
        else:
            return 0

    def setRegister(self, code, value):
        if code >= eRegister.RG_SIZE.value:
            return False
        elif value == self.regs[code]:
            return False
        else:
            self.regs[code] = value
            return True
    # def on_TestButton_released(self):
    #     buf = [0] * 512
    #     buf[0] = self.SET_COMMAND_REPORT
    #     buf[1] = eRegister.RG_CAMERA_ARRAY_TYPE.value
    #     artype = self.writeToKernel(buf)[2]
    #     print(artype)
    #     try:
    #         self.KernelUpdate()
    #     except Exception as e:
    #         exc_type, exc_obj,exc_tb = sys.exc_info()
    #         print(e)
    #         print("Line: " + str(exc_tb.tb_lineno))
    def writeToKernel(self, buffer):
        try:
            dev = hid.device()
            dev.open_path(self.camera)
            q = dev.write(buffer)
            if buffer[0] == self.SET_COMMAND_REPORT and buffer[1] == eCommand.CM_TRANSFER_MODE.value:
                dev.close()
                return q
            else:
                r = dev.read(self.BUFF_LEN)
                dev.close()
                return r
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            self.KernelLog.append("Error: " + str(e) + ' Line: ' + str(exc_tb.tb_lineno))


    def on_KernelBeep_toggled(self):
        buf = [0] * 512

        buf[0] = self.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_BEEPER_ENABLE.value
        if self.KernelBeep.isChecked():
            buf[2] = 1
        else:
            buf[2] = 0

        res = self.writeToKernel(buf)
        try:
            self.KernelUpdate()
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))
    def on_KernelPWMSignal_toggled(self):
        buf = [0] * 512

        buf[0] = self.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_PWM_TRIGGER.value
        if self.KernelPWMSignal.isChecked():
            buf[2] = 1
        else:
            buf[2] = 0

        res = self.writeToKernel(buf)
        try:
            self.KernelUpdate()
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))

    def on_KernelAdvancedSettingsButton_released(self):
        self.Advancedwindow = AdvancedOptions(self)
        # self.modalwindow = KernelCAN(self)
        self.Advancedwindow.resize(400, 200)
        self.Advancedwindow.exec_()
        # try:
        #     self.KernelUpdate()
        # except Exception as e:
        # exc_type, exc_obj,exc_tb = sys.exc_info()
        #     print(e + ' ) + exc_tb.tb_lineno
    def on_KernelFolderCount_currentIndexChanged(self):
        buf = [0] * 512
        buf[0] = self.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_MEDIA_FILES_CNT.value
        buf[2] = self.KernelFolderCount.currentIndex()

        self.writeToKernel(buf)
        try:
            self.KernelUpdate()
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))
    def on_KernelVideoOut_currentIndexChanged(self):
        if self.KernelVideoOut.currentIndex() == 0:  # No Output
            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_DAC.value  # DAC Register
            buf[2] = 0
            self.writeToKernel(buf)

            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_HDMI.value  # HDMI Register
            buf[2] = 0
            self.writeToKernel(buf)
        elif self.KernelVideoOut.currentIndex() == 1:  # HDMI
            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_DAC.value  # DAC Register
            buf[2] = 0
            self.writeToKernel(buf)

            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_HDMI.value  # HDMI Register
            buf[2] = 1
            self.writeToKernel(buf)
        elif self.KernelVideoOut.currentIndex() == 2:  # SD( DAC )
            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_DAC.value  # DAC Register
            buf[2] = 1
            self.writeToKernel(buf)

            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_HDMI.value  # HDMI Register
            buf[2] = 0
            self.writeToKernel(buf)
        else:  # Both outputs
            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_DAC.value  # DAC Register
            buf[2] = 1
            self.writeToKernel(buf)

            buf = [0] * 512

            buf[0] = self.SET_REGISTER_WRITE_REPORT
            buf[1] = eRegister.RG_HDMI.value  # HDMI Register
            buf[2] = 1
            self.writeToKernel(buf)
        # self.camera.close()
        try:
            self.KernelUpdate()
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))
    def on_KernelIntervalButton_released(self):
        self.modalwindow = KernelModal(self)
        self.modalwindow.resize(400, 200)
        self.modalwindow.exec_()

        num = self.seconds % 168
        if num == 0:
            num = 1
        self.seconds = num
        try:
            self.KernelUpdate()
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))

    def on_KernelCANButton_released(self):
        self.modalwindow = KernelCAN(self)
        self.modalwindow.resize(400, 200)
        self.modalwindow.exec_()
        # try:
        #     self.KernelUpdate()
        # except Exception as e:
        #     exc_type, exc_obj,exc_tb = sys.exc_info()
        #     print(e)
        #     print("Line: " + str(exc_tb.tb_lineno))

    def on_KernelTimeButton_released(self):
        self.modalwindow = KernelTime(self)
        self.modalwindow.resize(400, 200)
        self.modalwindow.exec_()
        # try:
        #     self.KernelUpdate()
        # except Exception as e:
        # exc_type, exc_obj,exc_tb = sys.exc_info()
        #     print(e + ' ) + exc_tb.tb_lineno

    def writeToIntervalLine(self):
        self.KernelIntervalLine.clear()
        self.KernelIntervalLine.setText(
            str(self.weeks) + 'w, ' + str(self.days) + 'd, ' + str(self.hours) + 'h, ' + str(self.minutes) + 'm,' + str(
                self.seconds) + 's')

    #########Pre-Process Steps: Start#################
    def on_PreProcessLens_currentIndexChanged(self):
        if self.PreProcessCameraModel.currentText() == "Kernel 14.4":
            if self.PreProcessFilter.currentText() in ["RGB", "RGN"]:
                self.PreProcessVignette.setEnabled(True)

            else:
                self.PreProcessVignette.setChecked(False)
                self.PreProcessVignette.setEnabled(False)

            if self.PreProcessFilter.currentText() == "RGB":
                self.PreProcessColorBox.setEnabled(True)

            else:
                self.PreProcessColorBox.setChecked(False)
                self.PreProcessColorBox.setEnabled(False)

        elif self.PreProcessCameraModel.currentText() == "Kernel 3.2":
            if self.PreProcessLens.currentText() in ["3.5mm", "5.5mm", "12.0mm", "16.0mm", "35.0mm"]:
                self.PreProcessVignette.setEnabled(False)


    def on_PreProcessFilter_currentIndexChanged(self):
        if (self.PreProcessCameraModel.currentText() == "Kernel 14.4" and self.PreProcessFilter.currentText() == "RGB"):

            self.PreProcessColorBox.setEnabled(True)
            self.PreProcessVignette.setEnabled(True)

        elif self.PreProcessCameraModel.currentText() == "Kernel 14.4":
            if self.PreProcessFilter.currentText() not in ["RGB", "RGN"]:
                self.PreProcessVignette.setChecked(False)
                self.PreProcessVignette.setEnabled(False)

            if self.PreProcessFilter.currentText() != "RGB":
                self.PreProcessColorBox.setChecked(False)
                self.PreProcessColorBox.setEnabled(False)

            if self.PreProcessFilter.currentText() in ["RGB", "RGN"]:
                self.PreProcessVignette.setEnabled(True)

        elif self.PreProcessCameraModel.currentText() == "Kernel 3.2":
            self.PreProcessMonoBandBox.setEnabled(False)
            if (self.PreProcessLens.currentText() == "9.6mm" and
                self.PreProcessFilter.currentText() in ["405", "450", "490", "518",
                                                       "550", "590", "615", "632", "650",
                                                       "685", "725", "780","808",
                                                       "850", "880","940"]):

                self.PreProcessVignette.setEnabled(True)
            else:
                self.PreProcessVignette.setChecked(False)
                self.PreProcessVignette.setEnabled(False)

        elif self.PreProcessCameraModel.currentText() == "Survey3":
            self.PreProcessColorBox.setEnabled(True)
            self.PreProcessVignette.setEnabled(False)

            if self.PreProcessFilter.currentText() == "RGB":
                self.PreProcessMonoBandBox.setChecked(False)

            elif self.PreProcessFilter.currentText() == "OCN":
                self.PreProcessMonoBandBox.setChecked(False)

            elif self.PreProcessFilter.currentText() == "RGN":
                self.PreProcessMonoBandBox.setChecked(False)

            elif self.PreProcessFilter.currentText() == "NGB":
                self.PreProcessMonoBandBox.setChecked(False)

            elif self.PreProcessFilter.currentText() == "RE":
                self.PreProcessMonoBandBox.setChecked(True)
                self.Band_Dropdown.setCurrentIndex(0)

            elif self.PreProcessFilter.currentText() == "NIR":
                self.PreProcessMonoBandBox.setChecked(True)
                self.Band_Dropdown.setCurrentIndex(0)

            if self.PreProcessFilter.currentText() != "RGB":
                self.PreProcessColorBox.setEnabled(False)


        elif self.PreProcessCameraModel.currentText() == "Survey2":
            self.PreProcessVignette.setEnabled(False)

            if self.PreProcessFilter.currentText() == "Red + NIR (NDVI)":
                self.PreProcessMonoBandBox.setChecked(False)

            elif self.PreProcessFilter.currentText() == "NIR":
                self.PreProcessMonoBandBox.setChecked(True)
                self.Band_Dropdown.setCurrentIndex(0)

            elif self.PreProcessFilter.currentText() == "Red":
                self.PreProcessMonoBandBox.setChecked(True)
                self.Band_Dropdown.setCurrentIndex(0)

            elif self.PreProcessFilter.currentText() == "Green":
                self.PreProcessMonoBandBox.setChecked(True)
                self.Band_Dropdown.setCurrentIndex(1)

            elif self.PreProcessFilter.currentText() == "Blue":
                self.PreProcessMonoBandBox.setChecked(True)
                self.Band_Dropdown.setCurrentIndex(2)

            elif self.PreProcessFilter.currentText() == "RGB":
                self.PreProcessMonoBandBox.setChecked(False)
                self.PreProcessColorBox.setEnabled(True)

            if self.PreProcessFilter.currentText() != "RGB":
                self.PreProcessColorBox.setEnabled(False)

        else:
            self.PreProcessColorBox.setChecked(False)
            self.PreProcessColorBox.setEnabled(False)
        QtWidgets.QApplication.processEvents()

    def update_pre_process_filter(self, filter_names, enabled):
        self.update_select_dropdown_component(self.PreProcessFilter, filter_names, enabled)

    def update_pre_process_lens(self, lens_names, enabled):
        self.update_select_dropdown_component(self.PreProcessLens, lens_names, enabled)

    def update_select_dropdown_component(self, component, items_to_add, enabled):
        component.clear()
        component.addItems(items_to_add)
        component.setEnabled(enabled)

    def update_pre_process_options_for_camera_model(self, model_name):
        if CameraSpecs.specs[model_name]["pre_process"]:
            pre_process_settings = CameraSpecs.specs[model_name]["pre_process"]
            self.update_pre_process_filter(
                pre_process_settings["filters"],
                pre_process_settings["enable_filter_select"]
            )
            self.update_pre_process_lens(
                pre_process_settings["lenses"],
                pre_process_settings["enable_lens_select"]
            )
            if pre_process_settings["enable_dark_box"] == True:
                self.PreProcessDarkBox.setEnabled(True)
        else:
            self.PreProcessFilter.clear()
            self.PreProcessFilter.setEnabled(False)
            self.PreProcessLens.clear()
            self.PreProcessLens.setEnabled(False)

    def on_PreProcessCameraModel_currentIndexChanged(self):
        self.PreProcessVignette.setChecked(False)
        self.PreProcessVignette.setEnabled(False)
        self.PreProcessColorBox.setChecked(False)
        self.PreProcessColorBox.setEnabled(False)
        self.PreProcessDarkBox.setChecked(False)
        self.PreProcessDarkBox.setEnabled(False)

        self.PreProcessMonoBandBox.setChecked(False)
        self.Band_Dropdown.setEnabled(False)
        self.PreProcessMonoBandBox.setEnabled(True)

        self.update_pre_process_options_for_camera_model(self.PreProcessCameraModel.currentText())


    def on_PreProcessMonoBandBox_toggled(self):
        if self.PreProcessMonoBandBox.checkState() == 2:
            self.Band_Dropdown.addItems(["Band 1 (Red)", "Band 2 (Green)", "Band 3 (Blue)"])
            self.Band_Dropdown.setEnabled(True)

        elif self.histogramClipBox.checkState() == 0:
            self.Band_Dropdown.clear()
            self.Band_Dropdown.setEnabled(False)

        QtWidgets.QApplication.processEvents()

    def on_PreProcessDarkBox_toggled(self):
        if self.PreProcessDarkBox.checkState() == 0:
            self.PreProcessJPGBox.setEnabled(True)
        else:
            self.PreProcessJPGBox.setEnabled(False)

    def on_PreProcessJPGBox_toggled(self):
        if self.PreProcessCameraModel.currentText() in self.KERNELS or self.PreProcessCameraModel.currentText() in self.SURVEYS:
            if self.PreProcessJPGBox.checkState() == 0:
                self.PreProcessDarkBox.setEnabled(True)
            else:
                self.PreProcessDarkBox.setEnabled(False)

    @staticmethod
    def populate_calibration_filter_dropdown(calibration_filter_menu, filters):
        calibration_filter_menu.clear()
        calibration_filter_menu.addItems(filters)
        enable_menu = len(filters) > 1
        calibration_filter_menu.setEnabled(enable_menu)

    @staticmethod
    def populate_calibration_lens_dropdown(calibration_lens_menu, lenses):
        calibration_lens_menu.clear()
        if lenses:
            calibration_lens_menu.addItems(lenses)
            enable_menu = len(lenses) > 1
            calibration_lens_menu.setEnabled(enable_menu)
        else:
            calibration_lens_menu.setEnabled(False)

    @staticmethod
    def on_calibration_camera_model_change(calibration_camera_model, calibration_filter, calibration_lens):
        model_name = calibration_camera_model.currentText()
        calibration_filters_for_model = CameraSpecs.specs[model_name]["calibration"]["filters"]
        calibration_lenses_for_model = CameraSpecs.specs[model_name]["calibration"]["lenses"]

        model_names = [
            "Kernel 1.2", "Kernel 3.2", "Kernel 14.4", "Survey3", "Survey2", "Survey1",
            "DJI Phantom 4", "DJI Phantom 4 Pro", "DJI Phantom 3a", "DJI Phantom 3p", "DJI X3"
        ]

        if model_name in model_names:
            MAPIR_ProcessingDockWidget.populate_calibration_filter_dropdown(calibration_filter, filters=calibration_filters_for_model)
            MAPIR_ProcessingDockWidget.populate_calibration_lens_dropdown(calibration_lens, lenses=calibration_lenses_for_model)
        else:
            calibration_filter.clear()
            calibration_filter.setEnabled(False)
            calibration_lens.clear()
            calibration_lens.setEnabled(False)

    def on_CalibrationCameraModel_currentIndexChanged(self):
        MAPIR_ProcessingDockWidget.on_calibration_camera_model_change(self.CalibrationCameraModel, self.CalibrationFilter, self.CalibrationLens)

    def on_CalibrationCameraModel_2_currentIndexChanged(self):
        MAPIR_ProcessingDockWidget.on_calibration_camera_model_change(self.CalibrationCameraModel_2, self.CalibrationFilter_2, self.CalibrationLens_2)

    def on_CalibrationCameraModel_3_currentIndexChanged(self):
        MAPIR_ProcessingDockWidget.on_calibration_camera_model_change(self.CalibrationCameraModel_3, self.CalibrationFilter_3, self.CalibrationLens_3)

    def on_CalibrationCameraModel_4_currentIndexChanged(self):
        MAPIR_ProcessingDockWidget.on_calibration_camera_model_change(self.CalibrationCameraModel_4, self.CalibrationFilter_4, self.CalibrationLens_4)

    def on_CalibrationCameraModel_5_currentIndexChanged(self):
        MAPIR_ProcessingDockWidget.on_calibration_camera_model_change(self.CalibrationCameraModel_5, self.CalibrationFilter_5, self.CalibrationLens_5)

    def on_CalibrationCameraModel_6_currentIndexChanged(self):
       MAPIR_ProcessingDockWidget.on_calibration_camera_model_change(self.CalibrationCameraModel_6, self.CalibrationFilter_6, self.CalibrationLens_6)

    def on_PreProcessInButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            folder = QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read())
            self.PreProcessInFolder.setText(folder)
            self.PreProcessOutFolder.setText(folder)
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.PreProcessInFolder.text())

    def on_PreProcessOutButton_released(self):
        self.present_folder_select_dialog(self.PreProcessOutFolder)

    def on_VignetteFileSelectButton_released(self):
        self.present_file_select_dialog(self.VignetteFileSelect)
        # with open(modpath + os.sep + "instring.txt", "r+") as instring:
        #     self.VignetteFileSelect.setText(QtWidgets.QFileDialog.getOpenFileName(directory=instring.read())[0])
        #     instring.truncate(0)
        #     instring.seek(0)
        #     instring.write(self.VignetteFileSelect.text())

    def on_PreProcessButton_released(self):
        if self.PreProcessCameraModel.currentIndex() == -1:
            self.PreProcessLog.append("Attention! Please select a camera model.\n")
        else:
            # self.PreProcessLog.append(r'Extracting vignette corection data')
            infolder = self.PreProcessInFolder.text()
            if len(infolder) == 0:
                self.PreProcessLog.append("Attention! Please select an input folder.\n")
                return 0

            outdir = self.PreProcessOutFolder.text()
            if len(outdir) == 0:
                self.PreProcessLog.append("Attention! No Output folder selected, creating output under input folder.\n")
                outdir = infolder
            foldercount = 1
            endloop = False
            while endloop is False:
                outfolder = outdir + os.sep + "Processed_" + str(foldercount)
                if os.path.exists(outfolder):
                    foldercount += 1
                else:
                    os.mkdir(outfolder)
                    endloop = True
            try:
                start = time.time()
                self.preProcessHelper(infolder, outfolder)
                end = time.time()
                print("time: ", (end - start)/ 60)

                self.PreProcessLog.append("Finished Processing Images.")

            except Exception as e:
                exc_type, exc_obj,exc_tb = sys.exc_info()
                self.PreProcessLog.append(str(e))

    def on_CalibrationInButton_released(self):
        self.present_folder_select_dialog(self.CalibrationInFolder)
        # with open(modpath + os.sep + "instring.txt", "r+") as instring:
        #     self.CalibrationInFolder.setText(QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read()))
        #     instring.truncate(0)
        #     instring.seek(0)
        #     instring.write(self.CalibrationInFolder.text())

    def on_CalibrationInButton_2_released(self):
        self.present_folder_select_dialog(self.CalibrationInFolder_2)
    def on_CalibrationInButton_3_released(self):
        self.present_folder_select_dialog(self.CalibrationInFolder_3)
    def on_CalibrationInButton_4_released(self):
        self.present_folder_select_dialog(self.CalibrationInFolder_4)
    def on_CalibrationInButton_5_released(self):
        self.present_folder_select_dialog(self.CalibrationInFolder_5)
    def on_CalibrationInButton_6_released(self):
        self.present_folder_select_dialog(self.CalibrationInFolder_6)

    def on_CalibrationQRButton_released(self):
        self.present_file_select_dialog(self.CalibrationQRFile)
    def on_CalibrationQRButton_2_released(self):
        self.present_file_select_dialog(self.CalibrationQRFile_2)
    def on_CalibrationQRButton_3_released(self):
        self.present_file_select_dialog(self.CalibrationQRFile_3)
    def on_CalibrationQRButton_4_released(self):
        self.present_file_select_dialog(self.CalibrationQRFile_4)
    def on_CalibrationQRButton_5_released(self):
        self.present_file_select_dialog(self.CalibrationQRFile_5)
    def on_CalibrationQRButton_6_released(self):
        self.present_file_select_dialog(self.CalibrationQRFile_6)

    def append_select_a_camera_message_to_calibration_log(self):
        self.CalibrationLog.append("Attention! Please select a camera model.\n")

    def append_please_select_a_target_image_message_to_calibration_log(self):
        self.CalibrationLog.append("Attention! Please select a target image.\n")

    def any_calibration_camera_model_selected(self, calibration_camera_model):
        return calibration_camera_model.currentIndex() != -1

    def any_calibration_target_image_selected(self, calibration_QR_file):
        return len(calibration_QR_file.text()) > 0

    def generate_calibration(self, calibration_camera_model, calibration_QR_file, calibration_filter, calibration_lens, qrcoeffs, qr_coeffs_index):

        self.CalibrationLog.append('calibration_camera_model')
        self.CalibrationLog.append(calibration_camera_model.currentText())  #combobox  'Survey3'

        self.CalibrationLog.append('calibration_QR_file')
        self.CalibrationLog.append(calibration_QR_file.text())  #qlineedit  path to file


        self.CalibrationLog.append('calibration_filter')
        self.CalibrationLog.append(calibration_filter.currentText()) #combobox  'OCN'

        self.CalibrationLog.append('calibration_lens')
        self.CalibrationLog.append(calibration_lens.currentText()) #Combbox   '3.37mm (Survey3W)'

        self.CalibrationLog.append('qrcoeffs')
        self.CalibrationLog.append(str(qrcoeffs))  #[]

        self.CalibrationLog.append('qr_coeffs_index')
        self.CalibrationLog.append(str(qr_coeffs_index) ) #1

        try:
            if not self.any_calibration_camera_model_selected(calibration_camera_model):
                self.append_select_a_camera_message_to_calibration_log()

            elif self.any_calibration_target_image_selected(calibration_QR_file):
                self.findQR(calibration_QR_file.text(), [calibration_camera_model, calibration_filter, calibration_lens])
                print(self.multiplication_values)

                self.qr_coeffs[qr_coeffs_index] = copy.deepcopy(self.multiplication_values["mono"])
                qrcoeffs = self.qr_coeffs
                self.useqr = True

            else:
                self.append_please_select_a_target_image_message_to_calibration_log()

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            self.CalibrationLog.append(str(e) + ' Line: ' + str(exc_tb.tb_lineno))

    def on_CalibrationGenButton_released(self):
        self.generate_calibration(self.CalibrationCameraModel, self.CalibrationQRFile, self.CalibrationFilter, self.CalibrationLens, self.qrcoeffs, qr_coeffs_index=1)
        # self.qrcoeffs = self.qr_coeffs[1]
    def on_CalibrationGenButton_2_released(self):
        self.generate_calibration(self.CalibrationCameraModel_2, self.CalibrationQRFile_2, self.CalibrationFilter_2, self.CalibrationLens_2, self.qrcoeffs2, qr_coeffs_index=2)
        # self.qrcoeffs2 = self.qr_coeffs[2]
    def on_CalibrationGenButton_3_released(self):
        self.generate_calibration(self.CalibrationCameraModel_3, self.CalibrationQRFile_3, self.CalibrationFilter_3, self.CalibrationLens_3, self.qrcoeffs3, qr_coeffs_index=3)
        # self.qrcoeffs3 = self.qr_coeffs[3]
    def on_CalibrationGenButton_4_released(self):
        self.generate_calibration(self.CalibrationCameraModel_4, self.CalibrationQRFile_4, self.CalibrationFilter_4, self.CalibrationLens_4, self.qrcoeffs4, qr_coeffs_index=4)
        # self.qrcoeffs4 = self.qr_coeffs[4]
    def on_CalibrationGenButton_5_released(self):
        self.generate_calibration(self.CalibrationCameraModel_5, self.CalibrationQRFile_5, self.CalibrationFilter_5, self.CalibrationLens_5, self.qrcoeffs5, qr_coeffs_index=5)
        # self.qrcoeffs5 = self.qr_coeffs[5]
    def on_CalibrationGenButton_6_released(self):
        self.generate_calibration(self.CalibrationCameraModel_6, self.CalibrationQRFile_6, self.CalibrationFilter_6, self.CalibrationLens_6, self.qrcoeffs6, qr_coeffs_index=6)
        # self.qrcoeffs6 = self.qr_coeffs[6]

    #Function that calibrates global max and mins
    def calibrate(self, mult_values, value):
        slope = mult_values["slope"]
        intercept = mult_values["intercept"]

        return int((slope * value) + intercept)

    def get_HC_value(self, color):
        HCP = int(self.HCP_value.text()) / 100
        unique, counts = np.unique(color, return_counts=True)
        freq_array = np.asarray((unique, counts)).T

        total_pixels = color.size

        sum_pixels = 0
        for pixel in freq_array[::-1]:
            sum_pixels += pixel[1]

            if (sum_pixels / total_pixels) >= HCP:
                return pixel[0]

    def on_histogramClipBox_toggled(self):
        if self.histogramClipBox.checkState() == 2:
            self.Histogram_Clipping_Percentage.setEnabled(True)
            self.HCP_value.setEnabled(True)

        elif self.histogramClipBox.checkState() == 0:
            self.Histogram_Clipping_Percentage.setEnabled(False)
            self.HCP_value.setEnabled(False)
            self.HCP_value.clear()

    def check_HCP_value(self):
        if "." in self.HCP_value.text():
            return True

        if self.histogramClipBox.checkState() and not self.HCP_value.text():
            return True

        elif (self.histogramClipBox.checkState() and (int(self.HCP_value.text()) < 1 or int(self.HCP_value.text()) > 100)):
            return True

        else:
            return False

    def failed_calibration(self):
        self.failed_calib = True
        self.CalibrationLog.append("No default calibration data for selected camera model. Please please supply a MAPIR Reflectance Target to proceed.\n")

    # def make_calibration_out_dir(self):
    def get_files_to_calibrate(self):
        files = []
        files.extend(MAPIR_ProcessingDockWidget.get_tiff_files_in_dir('.'))
        files.extend(MAPIR_ProcessingDockWidget.get_jpg_files_in_dir('.'))
        return files

    # def get_calibration_out_path(self, parent_dirname, folder_count):
    #     parent_dirname + os.sep + "Calibrated_" + str(folder_count)

    def make_calibration_out_dir(self, parent_dirname):
        foldercount = 1
        endloop = False
        while endloop is False:
            # outdir = self.get_calibration_out_path(parent_dirname, foldercount)
            outdir = parent_dirname + os.sep + "Calibrated_" + str(foldercount)

            if os.path.exists(outdir):
                foldercount += 1
            else:
                os.mkdir(outdir)
                endloop = True
        return outdir

    def append_calibrating_image_message_to_calibration_log(self, image_index, files_to_calibrate):
        self.CalibrationLog.append("Calibrating image " + str(image_index + 1) + " of " + str(len(files_to_calibrate)))

    def on_CalibrateButton_released(self):
        self.failed_calib = False
        outdir = None
        if not self.CalibrationQRFile.text() and self.CalibrationInFolder.text():
            self.useqr = False
            self.CalibrationLog.append("Attempting to calibrate without MAPIR Reflectance Target...\n")

        try:
            no_calibration_camera_model_selected = not (self.any_calibration_camera_model_selected(self.CalibrationCameraModel) \
                or self.any_calibration_camera_model_selected(self.CalibrationCameraModel_2) \
                or self.any_calibration_camera_model_selected(self.CalibrationCameraModel_3) \
                or self.any_calibration_camera_model_selected(self.CalibrationCameraModel_4) \
                or self.any_calibration_camera_model_selected(self.CalibrationCameraModel_5) \
                or self.any_calibration_camera_model_selected(self.CalibrationCameraModel_6))

            if no_calibration_camera_model_selected:
                self.CalibrationLog.append("Attention! Please select a camera model.\n")


            elif self.check_HCP_value():
                self.CalibrationLog.append("Attention! Please select a Histogram Clipping Percentage value between 1-100.")
                self.CalibrationLog.append("For example: for 20%, please enter 20\n")


            elif len(self.CalibrationInFolder.text()) <= 0 \
                    and len(self.CalibrationInFolder_2.text()) <= 0 \
                    and len(self.CalibrationInFolder_3.text()) <= 0 \
                    and len(self.CalibrationInFolder_4.text()) <= 0 \
                    and len(self.CalibrationInFolder_5.text()) <= 0 \
                    and len(self.CalibrationInFolder_6.text()) <= 0:
                self.CalibrationLog.append("Attention! Please select a calibration folder.\n")

            else:
                self.CalibrationLog.append("Analyzing Input Directory. Please wait... \n")
                self.firstpass = True
                # self.CalibrationLog.append("CSV Input: \n" + str(self.refvalues))
                # self.CalibrationLog.append("Calibration button pressed.\n")
                calfolder = self.CalibrationInFolder.text()
                calfolder2 = self.CalibrationInFolder_2.text()
                calfolder3 = self.CalibrationInFolder_3.text()
                calfolder4 = self.CalibrationInFolder_4.text()
                calfolder5 = self.CalibrationInFolder_5.text()
                calfolder6 = self.CalibrationInFolder_6.text()

                self.pixel_min_max = {"redmax": 0.0, "redmin": 65535.0,
                                      "greenmax": 0.0, "greenmin": 65535.0,
                                      "bluemax": 0.0, "bluemin": 65535.0}

                self.HC_max = {"redmax": 0.0,
                               "greenmax": 0.0,
                               "bluemax": 0.0, }

                self.HC_mono_max = 0
                self.multiple_inputs = False
                self.maxes = {}
                self.mins = {}
                self.HC_mult_max = {}

                # self.CalibrationLog.append("Calibration target folder is: " + calfolder + "\n")
                files_to_calibrate = []
                files_to_calibrate2 = []
                files_to_calibrate3 = []
                files_to_calibrate4 = []
                files_to_calibrate5 = []
                files_to_calibrate6 = []


                indexes = [
                    [self.CalibrationCameraModel.currentText(), self.CalibrationFilter.currentText(), self.CalibrationLens.currentText()],
                    [self.CalibrationCameraModel_2.currentText(), self.CalibrationFilter_2.currentText(), self.CalibrationLens_2.currentText()],
                    [self.CalibrationCameraModel_3.currentText(), self.CalibrationFilter_3.currentText(), self.CalibrationLens_3.currentText()],
                    [self.CalibrationCameraModel_4.currentText(), self.CalibrationFilter_4.currentText(), self.CalibrationLens_4.currentText()],
                    [self.CalibrationCameraModel_5.currentText(), self.CalibrationFilter_5.currentText(), self.CalibrationLens_5.currentText()],
                    [self.CalibrationCameraModel_6.currentText(), self.CalibrationFilter_6.currentText(), self.CalibrationLens_6.currentText()],
                ]

                if indexes[1][0] != "":
                    self.multiple_inputs = True

                folderind = [calfolder,
                             calfolder2,
                             calfolder3,
                             calfolder4,
                             calfolder5,
                             calfolder6]


                for j, ind in enumerate(indexes):
                    CHECKED = 2
                    UNCHECKED = 0

                    camera_model = ind[0]
                    filt = ind[1]
                    lens = ind[2]

                    if camera_model == "":
                        pass

                    elif self.check_if_RGB(camera_model, filt, lens):

                        if os.path.exists(folderind[j]):
                            os.chdir(folderind[j])
                            files_to_calibrate = self.get_files_to_calibrate()

                            if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate[0]:
                                outdir = self.make_calibration_out_dir(folderind[j])

                        for i, calpixel in enumerate(files_to_calibrate):
                            file_ext = calpixel.split('.')[-1]
                            # if file_ext == 'tif' or file_ext == 'TIF':
                            #     img = tifffile.imread(calpixel)
                            # else:
                            img = cv2.imread(calpixel, cv2.IMREAD_UNCHANGED)
                            if len(img.shape) < 3:
                                raise IndexError("RGB filter was selected but input folders contain MONO images")

                            blue = img[:, :, 0]
                            green = img[:, :, 1]
                            red = img[:, :, 2]

                            if camera_model == "Survey2" and filt == "Red + NIR (NDVI)":
                                red = img[:, :, 2] - (blue * 0.80)

                            # these are a little confusing, but the check to find the highest and lowest pixel value
                            # in each channel in each image and keep the highest/lowest value found.
                            if self.seed_pass == False:
                                self.pixel_min_max["redmax"] = red.max()
                                self.pixel_min_max["redmin"] = red.min()

                                self.pixel_min_max["greenmax"] = green.max()
                                self.pixel_min_max["greenmin"] = green.min()

                                self.pixel_min_max["bluemax"] = blue.max()
                                self.pixel_min_max["bluemin"] = blue.min()

                                if self.histogramClipBox.checkState() == self.CHECKED:
                                    self.HC_max["redmax"] = self.get_HC_value(red)
                                    self.HC_max["greenmax"] = self.get_HC_value(green)
                                    self.HC_max["bluemax"] = self.get_HC_value(blue)

                                self.seed_pass = True

                            else:

                                try:
                                #compare current image min-max with global min-max (non-calibrated)
                                    self.pixel_min_max["redmax"] = max(red.max(), self.pixel_min_max["redmax"])
                                    self.pixel_min_max["redmin"] = min(red.min(), self.pixel_min_max["redmin"])

                                    self.pixel_min_max["greenmax"] = max(green.max(), self.pixel_min_max["greenmax"])
                                    self.pixel_min_max["greenmin"] = min(green.min(), self.pixel_min_max["greenmin"])


                                    self.pixel_min_max["bluemax"] = max(blue.max(), self.pixel_min_max["bluemax"])
                                    self.pixel_min_max["bluemin"] = min(blue.min(), self.pixel_min_max["bluemin"])

                                    if self.histogramClipBox.checkState() == self.CHECKED:
                                        self.HC_max["redmax"] = max(self.get_HC_value(red), self.HC_max["redmax"])
                                        self.HC_max["greenmax"] = max(self.get_HC_value(green), self.HC_max["greenmax"])
                                        self.HC_max["bluemax"] = max(self.get_HC_value(blue), self.HC_max["bluemax"])


                                except Exception as e:
                                    print("ERROR: ", e)
                                    exc_type, exc_obj,exc_tb = sys.exc_info()
                                    print(' Line: ' + str(exc_tb.tb_lineno))

                        min_max_list = ["redmax", "redmin", "greenmax", "greenmin", "bluemin", "bluemax"]
                        if not self.useqr:
                            filetype = calpixel.split(".")[-1]
                            min_max_wo_g_list = ["redmax", "redmin", "bluemin", "bluemax"]

                            if camera_model == "Survey1":  # Survey1_NDVI
                                min_max_list = min_max_wo_g_list
                                if filetype in self.JPGS:
                                    base_coef = self.BASE_COEFF_SURVEY1_NDVI_JPG

                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model == "Survey2" and filt == "Red + NIR (NDVI)": #Survey 2 + Red + NIR
                                min_max_list = min_max_wo_g_list

                                if filetype in self.TIFS:
                                    base_coef = self.BASE_COEFF_SURVEY2_NDVI_TIF

                                elif filetype in self.JPGS:
                                    base_coef = self.BASE_COEFF_SURVEY2_NDVI_JPG

                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model == "DJI Phantom 3a":
                                min_max_list = min_max_wo_g_list
                                if filetype in self.TIFS:
                                    base_coef = self.BASE_COEFF_DJIX3_NDVI_TIF

                                elif filetype in self.JPGS:
                                    base_coef = self.BASE_COEFF_DJIX3_NDVI_JPG

                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model == "DJI Phantom 4":
                                min_max_list = min_max_wo_g_list
                                if filetype in self.TIFS:
                                    base_coef = self.BASE_COEFF_DJIPHANTOM4_NDVI_TIF

                                elif filetype in self.JPGS:
                                    base_coef = self.BASE_COEFF_DJIPHANTOM4_NDVI_JPG

                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model in ["DJI Phantom 4 Pro", "DJI Phantom 3a"]:
                                min_max_list = min_max_wo_g_list

                                if filetype in self.TIFS:
                                    base_coef = self.BASE_COEFF_DJIPHANTOM3_NDVI_TIF

                                elif filetype in self.JPGS:
                                    base_coef = self.BASE_COEFF_DJIPHANTOM3_NDVI_JPG
                                else:
                                    self.failed_calibration()
                                    break

                            elif camera_model == "Survey3":

                                if filt == "RGN":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY3_RGN_JPG
                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY3_RGN_TIF

                                elif filt == "OCN":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY3_OCN_JPG
                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY3_OCN_TIF

                                elif filt == "NGB":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY3_NGB_JPG
                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY3_NGB_TIF

                                else:
                                    self.failed_calibration()
                                    break

                            else:
                                self.failed_calibration()
                                break

                            for min_max in min_max_list:
                                if len(min_max) == 6:
                                    color = min_max[:3]

                                elif len(min_max) == 7:
                                    color = min_max[:4]
                                else:
                                    color = min_max[:5]

                                self.pixel_min_max[min_max] = self.calibrate(base_coef[color], self.pixel_min_max[min_max])

                            if self.histogramClipBox.checkState() == self.CHECKED:
                                self.HC_max["redmax"] = self.calibrate(base_coef["red"], self.HC_max["redmax"])
                                self.HC_max["greenmax"] = self.calibrate(base_coef["green"], self.HC_max["greenmax"])
                                self.HC_max["bluemax"] = self.calibrate(base_coef["blue"], self.HC_max["bluemax"])


                        self.seed_pass = False

                        #Calibrate global max and mins
                        if self.useqr:

                            for min_max in min_max_list:
                                if len(min_max) == 6:
                                    color = min_max[:3]
                                elif len(min_max) == 7:
                                    color = min_max[:4]
                                else:
                                    color = min_max[:5]

                                self.pixel_min_max[min_max] = self.calibrate(self.multiplication_values[color], self.pixel_min_max[min_max])


                            if self.histogramClipBox.checkState() == self.CHECKED:
                                self.HC_max["redmax"] = self.calibrate(self.multiplication_values["red"], self.HC_max["redmax"])
                                self.HC_max["greenmax"] = self.calibrate(self.multiplication_values["green"], self.HC_max["greenmax"])
                                self.HC_max["bluemax"] = self.calibrate(self.multiplication_values["blue"], self.HC_max["bluemax"])

                        for i, calfile in enumerate(files_to_calibrate):

                            cameramodel = ind
                            self.append_calibrating_image_message_to_calibration_log(i, files_to_calibrate)
                            QtWidgets.QApplication.processEvents()
                            if self.useqr:
                                try:
                                    self.CalibratePhotos(calfile, self.multiplication_values, self.pixel_min_max, outdir, ind)
                                except Exception as e:
                                    exc_type, exc_obj,exc_tb = sys.exc_info()
                                    self.CalibrationLog.append(str(e))
                            else:
                                self.CalibratePhotos(calfile, base_coef, self.pixel_min_max, outdir, ind)

                    else:
                        if os.path.exists(folderind[j]):
                            os.chdir(folderind[j])
                            files_to_calibrate = self.get_files_to_calibrate()


                            if not self.multiple_inputs:
                                if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate[0]:
                                    outdir = self.make_calibration_out_dir(folderind[j])

                        for i, calpixel in enumerate(files_to_calibrate):
                            file_ext = calpixel.split('.')[-1]
                            # if file_ext == 'tif' or file_ext == 'TIF':
                            #     img = tifffile.imread(calpixel)
                            # else:
                                # img = cv2.imread(calpixel, cv2.IMREAD_UNCHANGED)
                            img = cv2.imread(calpixel, cv2.IMREAD_UNCHANGED)
                            # img = cv2.imread(calpixel, -1)

                            if len(img.shape) > 2:
                                raise IndexError("Mono filter was selected but input folders contain RGB images")

                            if self.seed_pass == False:
                                self.monominmax["max"] = img.max()
                                self.monominmax["min"] = img.min()

                                if self.histogramClipBox.checkState() == self.CHECKED:
                                    self.HC_mono_max = self.get_HC_value(img)

                                self.seed_pass = True

                            else:

                                try:
                                    #compare current image min-max with global min-max (non-calibrated)
                                    self.monominmax["max"] = max(img.max(), self.monominmax["max"])
                                    self.monominmax["min"] = min(img.min(), self.monominmax["min"])

                                    if self.histogramClipBox.checkState() == self.CHECKED:
                                        self.HC_mono_max = max(self.get_HC_value(img), self.HC_mono_max)

                                except Exception as e:
                                    exc_type, exc_obj,exc_tb = sys.exc_info()

                        if not self.useqr:
                            filetype = calpixel.split(".")[-1]

                            if camera_model == "Survey2":
                                if filt == "Red":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY2_RED_JPG

                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY2_RED_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                                elif filt == "Green":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY2_GREEN_JPG

                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY2_GREEN_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                                elif filt == "Blue":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY2_BLUE_JPG

                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY2_BLUE_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                                elif filt == "NIR":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY2_NIR_JPG

                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY2_NIR_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                                else:
                                        self.failed_calibration()
                                        break

                            elif camera_model == "Survey3":
                                if filt == "RE":
                                    if filetype in self.JPGS:
                                        base_coef = self.BASE_COEFF_SURVEY3_RE_JPG

                                    elif filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY3_RE_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                                elif filt == "NIR":
                                    if filetype in self.TIFS:
                                        base_coef = self.BASE_COEFF_SURVEY3_NIR_TIF

                                    else:
                                        self.failed_calibration()
                                        break

                            elif camera_model == "Kernel 3.2":
                                raise UnboundLocalError("Calibration without a calibration target is not supported for Kernel 3.2")

                            if self.multiple_inputs:
                                self.maxes[j + 1] = self.calibrate(base_coef, img.max())
                                self.mins[j + 1] = self.calibrate(base_coef, img.min())

                            else:
                                self.monominmax["max"] = self.calibrate(base_coef, self.monominmax["max"])
                                self.monominmax["min"] = self.calibrate(base_coef, self.monominmax["min"])

                        if self.useqr:
                            if self.multiple_inputs:
                                self.maxes[j + 1] = self.calibrate(self.qr_coeffs[j + 1], img.max())
                                self.mins[j + 1] = self.calibrate(self.qr_coeffs[j + 1], img.min())

                                if self.histogramClipBox.checkState() == self.CHECKED:
                                    self.HC_mult_max[j + 1] = self.calibrate(self.qr_coeffs[j + 1], self.get_HC_value(img))

                            else:
                                self.monominmax["max"] = self.calibrate(self.multiplication_values["mono"], self.monominmax["max"])
                                self.monominmax["min"] = self.calibrate(self.multiplication_values["mono"], self.monominmax["min"])

                                if self.histogramClipBox.checkState() == self.CHECKED:
                                    self.HC_mono_max = self.calibrate(self.multiplication_values["mono"], self.HC_mono_max)

                        if not self.multiple_inputs:
                            for i, calfile in enumerate(files_to_calibrate):
                                cameramodel = ind
                                if self.useqr:
                                    try:
                                        self.append_calibrating_image_message_to_calibration_log(i, files_to_calibrate)
                                        QtWidgets.QApplication.processEvents()
                                        self.CalibrateMono(calfile, self.multiplication_values["mono"], outdir, ind)

                                    except Exception as e:
                                        print("ERROR: ", e)
                                        exc_type, exc_obj,exc_tb = sys.exc_info()
                                        exc_type, exc_obj,exc_tb = sys.exc_info()
                                        print(' Line: ' + str(exc_tb.tb_lineno))
                                        self.CalibrationLog.append(str(e))
                                else:
                                    self.append_calibrating_image_message_to_calibration_log(i, files_to_calibrate)
                                    QtWidgets.QApplication.processEvents()

                                    self.CalibrateMono(calfile, base_coef, outdir, ind)

                if self.multiple_inputs and not self.check_if_RGB(camera_model, filt, lens):
                    self.monominmax["max"] = max(list(self.maxes.values()))
                    self.monominmax["min"] = min(list(self.mins.values()))

                    if self.histogramClipBox.checkState() == self.CHECKED:
                        self.HC_mono_max = max(list(self.HC_mult_max.values()))

                    for j, ind in enumerate(indexes):
                        camera_model = ind[0]
                        filt = ind[1]
                        lens = ind[2]

                        if camera_model == "":
                            continue

                        if os.path.exists(folderind[j]):
                            os.chdir(folderind[j])
                            files_to_calibrate = self.get_files_to_calibrate()

                            if "tif" or "TIF" or "jpg" or "JPG" in files_to_calibrate[0]:
                                outdir = self.make_calibration_out_dir(folderind[j])

                        for i, calfile in enumerate(files_to_calibrate):
                            if self.useqr:
                                try:
                                    self.append_calibrating_image_message_to_calibration_log(i, files_to_calibrate)
                                    QtWidgets.QApplication.processEvents()
                                    self.CalibrateMono(calfile, self.qr_coeffs[j + 1], outdir, ind)

                                except Exception as e:
                                    print("ERROR: ", e)
                                    exc_type, exc_obj,exc_tb = sys.exc_info()
                                    exc_type, exc_obj,exc_tb = sys.exc_info()
                                    print(' Line: ' + str(exc_tb.tb_lineno))
                                    self.CalibrationLog.append(str(e))
                            else:
                                raise Exception("Calibrating multiple inputs without calibration target not supported for mono images")


                if not self.failed_calib:
                    self.CalibrationLog.append("Finished Calibrating " + str(len(files_to_calibrate) + len(files_to_calibrate2) + len(files_to_calibrate3) + len(files_to_calibrate4) + len(files_to_calibrate5) + len(files_to_calibrate6)) + " images\n")
                self.CalibrateButton.setEnabled(True)
                self.seed_pass = False


        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))

        return outdir

    def CalibrateMono(self, photo, coeff, output_directory, ind):
        try:
            refimg = cv2.imread(photo, -1)

            maxpixel = self.monominmax["max"]
            minpixel = self.monominmax["min"]

            refimg = ((refimg * coeff["slope"]) + coeff["intercept"])

            if self.histogramClipBox.checkState() == self.CHECKED:
                global_HC_max = self.HC_mono_max
                refimg[refimg > global_HC_max] = global_HC_max
                maxpixel = global_HC_max

            refimg = ((refimg - minpixel) / (maxpixel - minpixel))

            if self.IndexBox.checkState() == self.UNCHECKED:
            #Float to JPG
                if photo.split('.')[2].upper() == "JPG" or photo.split('.')[2].upper() == "JPEG" or self.Tiff2JpgBox.checkState() > 0:
                    refimg *= 255
                    refimg = refimg.astype(int)
                    refimg = refimg.astype("uint8")

                else: #Float to Tiff
                    refimg *= 65535
                    refimg = refimg.astype(int)
                    refimg = refimg.astype("uint16")

            else: #Float to Index
                refimg[refimg > 1.0] = 1.0
                refimg[refimg < 0.0] = 0.0
                refimg = refimg.astype("float")
                refimg = cv2.normalize(refimg.astype("float"), None, 0.0, 1.0, cv2.NORM_MINMAX)

            if self.Tiff2JpgBox.checkState() > 0:
                self.CalibrationLog.append("Making JPG")
                QtWidgets.QApplication.processEvents()
                cv2.imencode(".jpg", refimg)
                outpath = output_directory + photo.split('.')[1] + "_CALIBRATED.JPG"
                cv2.imwrite(outpath, refimg,
                            [int(cv2.IMWRITE_JPEG_QUALITY), 100])

                self.copyExif(photo, outpath)

            else:
                self.save_calibrated_image_without_conversion(photo, refimg, output_directory)

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))

    def save_calibrated_image_without_conversion(self, in_image_path, calibrated_image, out_dir):
        out_image_path = out_dir + in_image_path.split('.')[1] + "_CALIBRATED." + in_image_path.split('.')[2]
        if 'tif' in in_image_path.split('.')[2].lower():
            cv2.imencode(".tif", calibrated_image)
            cv2.imwrite(out_image_path, calibrated_image)

            # tiff = gdal.Open(in_image_path, gdal.GA_ReadOnly)
            # tiff_has_no_projection_data = tiff.GetProjection() == ''
            # tiff = None

            # # if tiff_has_no_projection_data:
            #     cv2.imencode(".tif", calibrated_image)
            #     cv2.imwrite(out_image_path, calibrated_image)
            #     self.copyExif(in_image_path, out_image_path)
            # # else:
            # #     # cv2.imencode(".tif", calibrated_image)
            # #     # cv2.imwrite(out_image_path, calibrated_image)
            # #     self.geotiff_with_metadata_from_rgba(in_image_path, calibrated_image, out_image_path)

        else:
            cv2.imwrite(out_image_path, calibrated_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

        self.copyExif(in_image_path, out_image_path)

        # self.copyExif(in_image_path, out_image_path)


    def calculate_mode(self, freq_array):
        pixel_freq = 0
        mode = 0
        for pixel in freq_array:
            if pixel[1] > pixel_freq:
                pixel_freq = pixel[1]
                mode = pixel[0]
        return mode

    def get_global_max_and_min_calibrated_pixel_values(self, camera_model, filt, minmaxes):
        ### find the global maximum (maxpixel) and minimum (minpixel) calibrated pixel values over the entire directory.
        red_min = minmaxes["redmin"]
        red_max = minmaxes["redmax"]
        blue_min = minmaxes["bluemin"]
        blue_max = minmaxes["bluemax"]
        green_min = minmaxes["greenmin"]
        green_max = minmaxes["greenmax"]

        if camera_model == "Survey1":  ###Survey1 NDVI
            maxpixel = max([blue_max, red_max])
            minpixel = min([blue_min, red_min])
            # blue = refimg[:, :, 0] - (refimg[:, :, 2] * 0.80)  # Subtract the NIR bleed over from the blue channel

        elif camera_model in ["Survey2", "Survey3"] and filt in ["NIR", "Red", "RE"]:
            maxpixel = red_max
            minpixel = red_min

        elif camera_model == 'Survey2':
            if filt == 'Green':
                maxpixel = green_max
                minpixel = green_min
            elif filt == 'Blue':
                maxpixel = blue_max
                minpixel = blue_min

        elif camera_model in ["Survey3", "DJI Phantom 4 Pro"]:
            maxpixel = max([blue_max, red_max, green_max])
            minpixel = min([blue_min, red_min, green_min])

        else:  ###Survey2 NDVI
            maxpixel = max([blue_max, red_max])
            minpixel = min([blue_min, red_min])
            # if ind[0] == 4:
            #     red = refimg[:, :, 2] - (refimg[:, :, 0] * 0.80)  # Subtract the NIR bleed over from the red channel
        return maxpixel, minpixel

    def calibrate_channel(self, channel, slope, intercept):
        return channel * slope + intercept

    def histogram_clip_channel(self, channel, global_clip_max):
        channel[channel > global_clip_max] = global_clip_max

    def histogram_clip_image(self, red, green, blue, global_HC_max):
        self.histogram_clip_channel(red, global_HC_max)
        self.histogram_clip_channel(green, global_HC_max)
        self.histogram_clip_channel(blue, global_HC_max)

    @staticmethod
    def convert_normalized_layer_to_bit_depth(layer, bit_depth):
        layer *= 2**bit_depth-1
        layer = layer.astype(int)
        dtype = 'uint' + str(bit_depth)
        layer = layer.astype(dtype)
        return layer

    def convert_normalized_image_to_bit_depth(self, bit_depth, red, green, blue, alpha=None):
        red = MAPIR_ProcessingDockWidget.convert_normalized_layer_to_bit_depth(red, bit_depth)
        green = MAPIR_ProcessingDockWidget.convert_normalized_layer_to_bit_depth(green, bit_depth)
        blue = MAPIR_ProcessingDockWidget.convert_normalized_layer_to_bit_depth(blue, bit_depth)

        if alpha is None:
            alpha = []
        if not alpha == []:
            alpha = MAPIR_ProcessingDockWidget.convert_normalized_layer_to_bit_depth(alpha, bit_depth)
            # MAPIR_ProcessingDockWidget.print_2d_list_frequencies(13228, alpha)

        return red, green, blue, alpha


    def geotiff_with_metadata_from_rgba(self, in_geotiff_path, image_data, out_geotiff_path):
        out_geotiff = Geotiff.create_geotiff(image_data, out_geotiff_path)
        out_geotiff.FlushCache()

        self.copyExif(in_geotiff_path, out_geotiff_path)

        projection, geo_transform, gcps, gcp_projection = Geotiff.get_geo_data(in_geotiff_path)
        Geotiff.set_geo_data(out_geotiff, projection, geo_transform, gcps, gcp_projection)

        bands = Geotiff.get_bands_from_image_data(image_data)
        nodata = -10000
        Geotiff.write_bands_to_geotiff(out_geotiff, bands, nodata)

        out_geotiff.FlushCache()
        out_geotiff = None

    # def save_geo_data_to_tiff(self, in_geotiff_path, calibrated_image_path):

    #     in_geotiff = gdal.Open(in_geotiff_path)
    #     projection = in_geotiff.GetProjection()
    #     geo_transform = in_geotiff.GetGeoTransform()
    #     GCPs = in_geotiff.GetGCPs()
    #     GCP_projection = in_geotiff.GetGCPProjection()

    #     calibrated_image = gdal.Open(calibrated_image_path, gdal.GA_Update)
    #     calibrated_image.SetGeoTransform(geo_transform)
    #     calibrated_image.SetProjection(projection)
    #     calibrated_image.SetGCPs(GCPs, GCP_projection)

    #     calibrated_image.FlushCache()

    #     in_geotiff = None
    #     calibrated_image = None

    @staticmethod
    def print_2d_list_frequencies(size, list):
        frequencies = collections.Counter([])
        for i in range(size):
            row = list[i]
            row_freqs = collections.Counter(row)
            frequencies += row_freqs
            # print('Row ' + str(i) + ': ' + str(row_freqs))
        print(frequencies)

    def CalibratePhotos(self, photo, coeffs, minmaxes, output_directory, ind):
        refimg = cv2.imread(photo, -1)

        camera_model = ind[0]
        filt = ind[1]
        lens = ind[2]

        ### split channels (using cv2.split caused too much overhead and made the host program crash)
        alpha = []
        has_alpha_layer = False
        blue = refimg[:, :, 0]
        green = refimg[:, :, 1]
        red = refimg[:, :, 2]

        if camera_model == "Survey2" and filt == "Red + NIR (NDVI)":
            red = refimg[:, :, 2] - (refimg[:, :, 0] * 0.80)

        if refimg.shape[2] == 4:
            alpha = refimg[:, :, 3]
            has_alpha_layer = True
            refimg = copy.deepcopy(refimg[:, :, :3])

        red = self.calibrate_channel(red, coeffs["red"]["slope"], coeffs["red"]["intercept"])
        green = self.calibrate_channel(green, coeffs["green"]["slope"], coeffs["green"]["intercept"])
        blue = self.calibrate_channel(blue, coeffs["blue"]["slope"], coeffs["blue"]["intercept"])

        maxpixel, minpixel = self.get_global_max_and_min_calibrated_pixel_values(camera_model, filt, minmaxes)


        ### Scale calibrated values back down to a useable range (Adding 1 to avoid 0 value pixels, as they will cause a
        #### divide by zero case when creating an index image

        if self.histogramClipBox.checkState() == self.CHECKED:
            global_HC_max = max([self.HC_max["bluemax"], self.HC_max["redmax"], self.HC_max["greenmax"]])
            self.histogram_clip_image(red, green, blue, global_HC_max)
            maxpixel = global_HC_max

        red, green, blue = normalize_rgb(red, green, blue, maxpixel, minpixel)

        if has_alpha_layer:
            original_alpha_depth = alpha.max() - alpha.min()
            alpha = alpha / original_alpha_depth

        # MAPIR_ProcessingDockWidget.print_2d_list_frequencies(13228, alpha)

        if self.IndexBox.checkState() == self.UNCHECKED:
            if refimg.dtype == 'uint8':
                # if 'tif' in photo.split('.')[-1].lower():
                #     # tiff = gdal.Open(photo, gdal.GA_ReadOnly)
                #     # tiff_has_projection_data = not tiff.GetProjection() == ''
                #     # self.CalibrationLog.append('tiff: ' + str(tiff))
                #     # self.CalibrationLog.append(str(gdal))
                #     # self.CalibrationLog.append(gdal.__version__)
                #     # self.CalibrationLog.append(gdal.VersionInfo())
                #     # self.CalibrationLog.append('Projection: ' + str(tiff.GetProjection()))
                #     # self.CalibrationLog.append('has_projection_data: ' + str(tiff_has_projection_data))
                #     # if tiff_has_projection_data:
                #     #     bit_depth = 16
                #     #     self.CalibrationLog.append('tiff with projection data bd=16')
                #     else:
                #         bit_depth = 8
                #         self.CalibrationLog.append('tiff without projection data bd=8')
                # else:
                    # bit_depth = 8
                bit_depth = 8
            elif refimg.dtype == 'uint16':
                bit_depth = 16
            else:
                raise Exception('Calibration input image should be 8-bit or 16-bit')

            red, green, blue, alpha = self.convert_normalized_image_to_bit_depth(bit_depth, red, green, blue, alpha)
            layers = (blue, green, red, alpha) if has_alpha_layer else (blue, green, red)
            refimg = cv2.merge(layers)

        else: #Float to Index
            red = red.astype("float32")
            green = green.astype("float32")
            blue = blue.astype("float32")

            #refimg = cv2.merge((blue, green, red))
            #refimg = cv2.normalize(refimg.astype("float32"), None, 0.0, 1.0, cv2.NORM_MINMAX)

        if self.Tiff2JpgBox.checkState() > 0:
            self.CalibrationLog.append("Making JPG")
            QtWidgets.QApplication.processEvents()

            cv2.imencode(".jpg", refimg)
            cv2.imwrite(output_directory + photo.split('.')[1] + "_CALIBRATED.JPG", refimg,
                        [int(cv2.IMWRITE_JPEG_QUALITY), 100])

            self.copyExif(photo, output_directory + photo.split('.')[1] + "_CALIBRATED.JPG")

        else:
            if self.IndexBox.isChecked():
                newimg_r = output_directory + photo.split('.')[1] + "_CALIBRATED_red." + photo.split('.')[2]
                newimg_b = output_directory + photo.split('.')[1] + "_CALIBRATED_blue." + photo.split('.')[2]
                newimg_g = output_directory + photo.split('.')[1] + "_CALIBRATED_green." + photo.split('.')[2]

                cv2.imencode(".tif", red)
                cv2.imencode(".tif", green)
                cv2.imencode(".tif", blue)

                cv2.imwrite(newimg_r, red)
                cv2.imwrite(newimg_b, blue)
                cv2.imwrite(newimg_g, green)

                # srin = gdal.Open(photo)
                # inproj = srin.GetProjection()
                # transform = srin.GetGeoTransform()
                # gcpcount = srin.GetGCPs()

                # srout = gdal.Open(newimg_r, gdal.GA_Update)
                # srout = gdal.Open(newimg_g, gdal.GA_Update)
                # srout = gdal.Open(newimg_b, gdal.GA_Update)

                # srout.SetProjection(inproj)
                # srout.SetGeoTransform(transform)
                # srout.SetGCPs(gcpcount, srin.GetGCPProjection())
                # srout = None
                # srin = None

                self.copyExif(photo, newimg_r)
                self.copyExif(photo, newimg_g)
                self.copyExif(photo, newimg_b)

            else:
                self.save_calibrated_image_without_conversion(photo, refimg, output_directory)

    def calculateIndex(self, visible, nir):
        try:
            nir[nir == 0] = 1
            visible[visible == 0] = 1
            if nir.dtype == "uint8":
                nir = nir / 255.0
                visible = visible / 255.0
            elif nir.dtype == "uint16":
                nir /= 65535.0
                visible /= 65535.0

            numer = nir - visible
            denom = nir + visible

            index = numer/denom
            return index
        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(e)
            print("Line: " + str(exc_tb.tb_lineno))
            return False

    def check_if_RGB(self, camera, filt, lens): #Kernel 14.4, Survey 3 - RGBs, and Phantoms
        if camera in self.DJIS:
            return True
        elif (camera == "Survey3" and filt not in ["RE", "NIR"]):
            return True
        elif camera == "Kernel 14.4":
            return True
        elif camera == "Survey2" and filt == "Red + NIR (NDVI)":
            return True
        elif camera == "Survey2" and filt == "RGB":
            return True
        else:
            return False

    def bad_target_photo(self, channels):
        for channel in channels:
            if channel != sorted(channel, reverse=True):
                return True

            for targ in channel:
                if math.isnan(targ):
                    return True

        return False

    def check_exposure_quality(self, x, y):
        if (x[0] == 1 and x[-1] == 0):
            x = x[1:]
            y = y[1:]

        elif (x[0] == 1):
            x = x[1:]
            y = y[1:]

        elif (x[-1] == 0):
            x = x[:-1]
            y = y[:-1]

        return x, y

    def print_center_targs(self, image, targ1values, targ2values, targ3values, targ4values, target1, target2, target3, target4, angle):
        t1_str = image.split(".")[0] + "_t1." + image.split(".")[1]
        t1_image = targ1values

        t2_str = image.split(".")[0] + "_t2." + image.split(".")[1]
        t2_image = targ2values

        t3_str = image.split(".")[0] + "_t3." + image.split(".")[1]
        t3_image = targ3values

        t4_str = image.split(".")[0] + "_t4." + image.split(".")[1]
        t4_image = targ4values

        if angle > self.ANGLE_SHIFT_QR:
            image_line = image.split(".")[0] + "_circles_shift." + image.split(".")[1]
        else:
            image_line = image.split(".")[0] + "_circles_orig." + image.split(".")[1]
        line_image = cv2.imread(image, -1)

        cv2.circle(line_image,target1, 15, (0,0,255), -1)
        cv2.circle(line_image,target2, 15, (255,0,0), -1)
        cv2.circle(line_image,target3, 15, (255,255,0), -1)
        cv2.circle(line_image,target4, 15, (255,0,255), -1)
        cv2.imwrite(image_line, line_image)

    def get_LOBF_values(self, x, y):
        try:
            mean_x = np.mean(x)
            mean_y = np.mean(y)

            numer = sum((x - mean_x) * (y - mean_y))
            denom = sum(np.power(x - mean_x, 2))

            slope = numer / denom
            intercept = mean_y - (slope * mean_x)

            return slope, intercept
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print("Error: ", e)
            print("Line: " + str(exc_tb.tb_lineno))

    def get_filetype(self, image):
        if image.split(".")[1] in self.JPGS:
            return "JPG"

        elif image.split(".")[1] in self.TIFS:
            return "TIF"

    def is_calibration_target_version_2(self):
        return self.CalibrationTargetSelect.currentIndex() == 0

    def is_calibration_target_version_1(self):
        return self.CalibrationTargetSelect.currentIndex() == 1

    def get_version_2_target_corners(self, image_path):
        self.coords = Calibration.get_image_corners(image_path)
        self.ref = self.refindex[1]
        print('self.coords: ' + str(self.coords))

    ####Function for finding the QR target and calculating the calibration coeficients\
    def findQR(self, image_path, ind):
        try:
            self.ref = ""

            if self.is_calibration_target_version_2():
                version = "V2"

            elif self.is_calibration_target_version_1():
                version = "V1"

            camera_model = ind[0].currentText()
            fil = ind[1].currentText()
            lens = ind[2].currentText()

            image = cv2.imread(image_path, -1)

            if self.check_if_RGB(camera_model, fil, lens):
                if len(image.shape) < 3:
                    raise IndexError("RGB filter was selected but input folders contain MONO images")
            else:
                if len(image.shape) > 2:
                    raise IndexError("Mono filter was selected but input folders contain RGB images")

            #Fiducial Finder only needs to be run for Version 2, calib.txt will only be written for Version 2
            if version == "V2":
                self.get_version_2_target_corners(image_path)

            #Finding coordinates for Version 1
            else:
                self.CalibrationLog.append("Looking for QR target \n")
                self.ref = self.refindex[0]

                if self.check_if_RGB(camera_model, fil, lens): #if RGB Camera
                    im = cv2.imread(image_path)
                    grayscale = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)) #increasing contrast
                    cl1 = clahe.apply(grayscale)
                else: #if mono camera
                    QtWidgets.QApplication.processEvents()
                    im = cv2.imread(image_path, 0)
                    clahe2 = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                    cl1 = clahe2.apply(im)
                denoised = cv2.fastNlMeansDenoising(cl1, None, 14, 7, 21)
                threshcounter = 17

                while threshcounter <= 255:
                    ret, thresh = cv2.threshold(denoised, threshcounter, 255, 0)

                    major = cv2.__version__.split('.')[0]
                    if major == '3':
                    # if os.name == "nt":
                        _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    else:
                        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    self.coords = []
                    count = 0

                    if hierarchy is not None:
                        for i in hierarchy[0]:
                            self.traverseHierarchy(hierarchy, contours, count, im, 0)
                            count += 1

                    if len(self.coords) == 3:
                        break
                    else:
                        threshcounter += 17

                if len(self.coords) is not 3:
                    self.CalibrationLog.append("Could not find MAPIR ground target.")
                    QtWidgets.QApplication.processEvents()
                    return

            line1 = Geometry.distance(self.coords[0], self.coords[1])
            line2 = Geometry.distance(self.coords[1], self.coords[2])
            line3 = Geometry.distance(self.coords[2], self.coords[0])
            hypotenuse = max([line1, line2, line3])

            #Finding Version 2 Target
            if version == "V2":
                center = self.coords[0]
                right = self.coords[1]
                bottom = self.coords[2]

                slope = Geometry.slope(right, bottom)
                dist = center[1] - (slope * center[0]) + ((slope * bottom[0]) - bottom[1])
                dist /= np.sqrt(np.power(slope, 2) + 1)
                # (center_y - slope * center_x + slope * bottom_x - bottom_y) / sqrt(slope^2 + 1)

                slope_right_to_center = Geometry.slope(right, center)
                angle = abs(math.degrees(math.atan(slope_right_to_center)))

            else:
                if hypotenuse == line1:
                    slope = Geometry.slope(self.coords[0], self.coords[1])
                    dist = self.coords[2][1] - (slope * self.coords[2][0]) + ((slope * self.coords[1][0]) - self.coords[1][1])
                    dist /= np.sqrt(np.power(slope, 2) + 1)
                    center = self.coords[2]

                    if (slope < 0 and dist < 0) or (slope >= 0 and dist >= 0):

                        bottom = self.coords[0]
                        right = self.coords[1]
                    else:

                        bottom = self.coords[1]
                        right = self.coords[0]
                elif hypotenuse == line2:
                    slope = Geometry.slope(self.coords[1], self.coords[2])
                    dist = self.coords[0][1] - (slope * self.coords[0][0]) + ((slope * self.coords[2][0]) - self.coords[2][1])
                    dist /= np.sqrt(np.power(slope, 2) + 1)
                    center = self.coords[0]

                    if (slope < 0 and dist < 0) or (slope >= 0 and dist >= 0):

                        bottom = self.coords[1]
                        right = self.coords[2]
                    else:

                        bottom = self.coords[2]
                        right = self.coords[1]
                else:
                    slope = Geometry.slope(self.coords[2], self.coords[0])
                    dist = self.coords[1][1] - (slope * self.coords[1][0]) + ((slope * self.coords[0][0]) - self.coords[0][1])
                    dist /= np.sqrt(np.power(slope, 2) + 1)
                    center = self.coords[1]
                    if (slope < 0 and dist < 0) or (slope >= 0 and dist >= 0):
                        # self.CalibrationLog.append("slope and dist share sign")
                        bottom = self.coords[2]
                        right = self.coords[0]
                    else:

                        bottom = self.coords[0]
                        right = self.coords[2]

            if version == "V2":
                if len(self.coords) > 0:
                    guidelength = np.sqrt(np.power((center[0] - bottom[0]), 2) + np.power((center[1] - bottom[1]), 2))
                    pixelinch = guidelength / self.CORNER_TO_CORNER

                    rad = (pixelinch * self.CORNER_TO_TARG)
                    vx = center[1] - bottom[1]
                    vy = center[0] - bottom[0]

            else:
                guidelength = np.sqrt(np.power((center[0] - bottom[0]), 2) + np.power((center[1] - bottom[1]), 2))
                pixelinch = guidelength / self.SQ_TO_SQ
                rad = (pixelinch * self.SQ_TO_TARG)
                vx = center[0] - bottom[0]
                vy = center[1] - bottom[1]

            newlen = np.sqrt(vx * vx + vy * vy)

            if version == "V2":
                if len(self.coords) > 0:
                    targ1x = (rad * (vx / newlen)) + self.coords[0][0]
                    targ1y = (rad * (vy / newlen)) + self.coords[0][1]
                    targ2x = (rad * (vx / newlen)) + self.coords[1][0]
                    targ2y = (rad * (vy / newlen)) + self.coords[1][1]
                    targ3x = (rad * (vx / newlen)) + self.coords[2][0]
                    targ3y = (rad * (vy / newlen)) + self.coords[2][1]
                    targ4x = (rad * (vx / newlen)) + self.coords[3][0]
                    targ4y = (rad * (vy / newlen)) + self.coords[3][1]

                    if angle > self.ANGLE_SHIFT_QR:
                        corn_to_targ = self.CORNER_TO_TARG - 1
                        rad = (pixelinch * corn_to_targ)
                        targ1y = -(rad * (vy / newlen)) + self.coords[0][1]
                        targ2y = -(rad * (vy / newlen)) + self.coords[1][1]
                        targ3y = -(rad * (vy / newlen)) + self.coords[2][1]
                        targ4y = -(rad * (vy / newlen)) + self.coords[3][1]


                    target1 = (int(targ1x), int(targ1y))
                    target2 = (int(targ2x), int(targ2y))
                    target3 = (int(targ3x), int(targ3y))
                    target4 = (int(targ4x), int(targ4y))

            else:
                targ1x = (rad * (vx / newlen)) + center[0]
                targ1y = (rad * (vy / newlen)) + center[1]
                targ3x = (rad * (vx / newlen)) + right[0]
                targ3y = (rad * (vy / newlen)) + right[1]

                target1 = (int(targ1x), int(targ1y))
                target3 = (int(targ3x), int(targ3y))
                target2 = (int((np.abs(target1[0] + target3[0])) / 2), int(np.abs((target1[1] + target3[1])) / 2))

            im2 = cv2.imread(image_path, -1)

            # kernel = np.ones((2, 2), np.uint16)
            # im2 = cv2.erode(im2, kernel, iterations=1)
            # im2 = cv2.dilate(im2, kernel, iterations=1)
            if camera_model == "Survey2" and fil == "Red + NIR (NDVI)":
                blue = im2[:, :, 0]
                green = im2[:, :, 1]
                red = im2[:, :, 2] - (im2[:, :, 0] * 0.80)

                if "JPG" in os.path.splitext(image_path)[1]:
                    red[red > 255.0] = 255.0
                    red[red < 0.0] = 0.0
                    red = red.astype("uint8")

                else:
                    red[red > 65535.0] = 65535.0
                    red[red < 0.0] = 0.0
                    red = red.astype("uint16")

                im2 =  cv2.merge((blue, green, red))


            if self.check_if_RGB(camera_model, fil, lens):
                try:
                    targ1values = im2[(target1[1] - int((pixelinch * 0.75) / 2)):(target1[1] + int((pixelinch * 0.75) / 2)),
                                  (target1[0] - int((pixelinch * 0.75) / 2)):(target1[0] + int((pixelinch * 0.75) / 2))]


                    targ2values = im2[(target2[1] - int((pixelinch * 0.75) / 2)):(target2[1] + int((pixelinch * 0.75) / 2)),
                                  (target2[0] - int((pixelinch * 0.75) / 2)):(target2[0] + int((pixelinch * 0.75) / 2))]

                    targ3values = im2[(target3[1] - int((pixelinch * 0.75) / 2)):(target3[1] + int((pixelinch * 0.75) / 2)),
                                  (target3[0] - int((pixelinch * 0.75) / 2)):(target3[0] + int((pixelinch * 0.75) / 2))]
                except Exception as e:
                    exc_type, exc_obj,exc_tb = sys.exc_info()
                    print(e)
                    print("Line: " + str(exc_tb.tb_lineno))

                t1redmean = np.mean(targ1values[:, :, 2])
                t1greenmean = np.mean(targ1values[:, :, 1])
                t1bluemean = np.mean(targ1values[:, :, 0])

                t2redmean = np.mean(targ2values[:, :, 2])
                t2greenmean = np.mean(targ2values[:, :, 1])
                t2bluemean = np.mean(targ2values[:, :, 0])

                t3redmean = np.mean(targ3values[:, :, 2])
                t3greenmean = np.mean(targ3values[:, :, 1])
                t3bluemean = np.mean(targ3values[:, :, 0])

                yred = []
                yblue = []
                ygreen = []
                if version == "V2":
                    if len(self.coords) > 0:
                        targ4values = im2[(target4[1] - int((pixelinch * 0.75) / 2)):(target4[1] + int((pixelinch * 0.75) / 2)),
                                      (target4[0] - int((pixelinch * 0.75) / 2)):(target4[0] + int((pixelinch * 0.75) / 2))]
                        t4redmean = np.mean(targ4values[:, :, 2])
                        t4greenmean = np.mean(targ4values[:, :, 1])
                        t4bluemean = np.mean(targ4values[:, :, 0])
                        yred = [0.87, 0.51, 0.23, 0.0]
                        yblue = [0.87, 0.51, 0.23, 0.0]
                        ygreen = [0.87, 0.51, 0.23, 0.0]

                        xred = [t1redmean, t2redmean, t3redmean, t4redmean]
                        xgreen = [t1greenmean, t2greenmean, t3greenmean, t4greenmean]
                        xblue = [t1bluemean, t2bluemean, t3bluemean, t4bluemean]

                    #self.print_center_targs(image_path, targ1values, targ2values, targ3values, targ4values, target1, target2, target3, target4, angle)

                else:
                    yred = [0.87, 0.51, 0.23]
                    yblue = [0.87, 0.51, 0.23]
                    ygreen = [0.87, 0.51, 0.23]

                    xred = [t1redmean, t2redmean, t3redmean]
                    xgreen = [t1greenmean, t2greenmean, t3greenmean]
                    xblue = [t1bluemean, t2bluemean, t3bluemean]

                if ((camera_model == "Survey3" and fil == "RGN") or (camera_model == "DJI Phantom 4 Pro") 
                        or (camera_model == "Kernel 14.4" and fil =="550/660/850")):
                    yred = self.refvalues[self.ref]["550/660/850"][0]
                    ygreen = self.refvalues[self.ref]["550/660/850"][1]
                    yblue = self.refvalues[self.ref]["550/660/850"][2]

                elif ((camera_model == "Survey3" and fil == "NGB") 
                    or (camera_model == "Kernel 14.4" and fil == "475/550/850")):

                    yred = self.refvalues[self.ref]["475/550/850"][0]
                    ygreen = self.refvalues[self.ref]["475/550/850"][1]
                    yblue = self.refvalues[self.ref]["475/550/850"][2]

                elif (camera_model == "Survey3" and fil == "OCN") or (camera_model == "Kernel 14.4" and fil == "OCN"):

                    yred = self.refvalues[self.ref]["490/615/808"][0]
                    ygreen = self.refvalues[self.ref]["490/615/808"][1]
                    yblue = self.refvalues[self.ref]["490/615/808"][2]

                else: #Survey 2 - NDVI
                    yred = self.refvalues[self.ref]["660/850"][0]
                    ygreen = self.refvalues[self.ref]["660/850"][1]
                    yblue = self.refvalues[self.ref]["660/850"][2]

                if self.get_filetype(image_path) == "JPG":
                    xred = [x / 255 for x in xred]
                    xgreen = [x / 255 for x in xgreen]
                    xblue = [x / 255 for x in xblue]

                elif self.get_filetype(image_path) == "TIF":
                    xred = [x / 65535 for x in xred]
                    xgreen = [x / 65535 for x in xgreen]
                    xblue = [x / 65535 for x in xblue]

                xred, yred = self.check_exposure_quality(xred, yred)
                xgreen, ygreen = self.check_exposure_quality(xgreen, ygreen)
                xblue, yblue = self.check_exposure_quality(xblue, yblue)

                if any(item == 1 or item == 0 or np.isnan(item) for item in xred + xgreen + xblue):
                    raise Exception("Provided calibration target photo is not generating good calibration values. Please use another calibration target photo.")

                x_channels = [xred, xgreen, xblue]

                if self.bad_target_photo(x_channels):
                    self.CalibrationLog.append("WARNING: Provided calibration target photo is not generating good calibration values. For optimal calibration, please use another calibration target photo or check that white balance and exposure settings are set to default values. \n")

                red_slope, red_intercept = self.get_LOBF_values(xred, yred)
                green_slope, green_intercept = self.get_LOBF_values(xgreen, ygreen)
                blue_slope, blue_intercept = self.get_LOBF_values(xblue, yblue)

                #return cofr, cofg, cofb
                self.multiplication_values["red"]["slope"] = red_slope
                self.multiplication_values["red"]["intercept"] = red_intercept

                self.multiplication_values["green"]["slope"] = green_slope
                self.multiplication_values["green"]["intercept"] = green_intercept

                self.multiplication_values["blue"]["slope"] = blue_slope
                self.multiplication_values["blue"]["intercept"] = blue_intercept

                if (camera_model == "Survey2" and fil == "Red + NIR (NDVI)"):
                    self.multiplication_values["green"]["slope"] = 1
                    self.multiplication_values["green"]["intercept"] = 0


                if version == "V2":
                    if len(self.coords) > 0:
                        self.CalibrationLog.append("Found QR Target Model 2, please proceed with calibration.")
                    else:
                        self.CalibrationLog.append("Could not find Calibration Target.")
                else:
                    self.CalibrationLog.append("Found QR Target Model 1, please proceed with calibration.")

            else:
                if version == "V2":
                    if len(self.coords) > 0:
                        targ1values = im2[(target1[1] - int((pixelinch * 0.75) / 2)):(target1[1] + int((pixelinch * 0.75) / 2)),
                                      (target1[0] - int((pixelinch * 0.75) / 2)):(target1[0] + int((pixelinch * 0.75) / 2))]
                        targ2values = im2[(target2[1] - int((pixelinch * 0.75) / 2)):(target2[1] + int((pixelinch * 0.75) / 2)),
                                      (target2[0] - int((pixelinch * 0.75) / 2)):(target2[0] + int((pixelinch * 0.75) / 2))]
                        targ3values = im2[(target3[1] - int((pixelinch * 0.75) / 2)):(target3[1] + int((pixelinch * 0.75) / 2)),
                                      (target3[0] - int((pixelinch * 0.75) / 2)):(target3[0] + int((pixelinch * 0.75) / 2))]
                        targ4values = im2[(target4[1] - int((pixelinch * 0.75) / 2)):(target4[1] + int((pixelinch * 0.75) / 2)),
                                      (target4[0] - int((pixelinch * 0.75) / 2)):(target4[0] + int((pixelinch * 0.75) / 2))]

                        if (len(im2.shape) > 2) and fil in ["RE", "NIR", "Red"]:
                            t1mean = np.mean(targ1values[:,:,2])
                            t2mean = np.mean(targ2values[:,:,2])
                            t3mean = np.mean(targ3values[:,:,2])
                            t4mean = np.mean(targ4values[:,:,2])

                        elif (len(im2.shape) > 2) and fil in ["Green"]:
                            t1mean = np.mean(targ1values[:,:,1])
                            t2mean = np.mean(targ2values[:,:,1])
                            t3mean = np.mean(targ3values[:,:,1])
                            t4mean = np.mean(targ4values[:,:,1])

                        elif (len(im2.shape) > 2) and fil in ["Blue"]:
                            t1mean = np.mean(targ1values[:,:,0])
                            t2mean = np.mean(targ2values[:,:,0])
                            t3mean = np.mean(targ3values[:,:,0])
                            t4mean = np.mean(targ4values[:,:,0])

                        else:
                            t1mean = np.mean(targ1values)
                            t2mean = np.mean(targ2values)
                            t3mean = np.mean(targ3values)
                            t4mean = np.mean(targ4values)

                        y = [0.87, 0.51, 0.23, 0.0]
                        x = [t1mean, t2mean, t3mean, t4mean]
                else:
                    targ1values = im2[(target1[1] - int((pixelinch * 0.75) / 2)):(target1[1] + int((pixelinch * 0.75) / 2)),
                                  (target1[0] - int((pixelinch * 0.75) / 2)):(target1[0] + int((pixelinch * 0.75) / 2))]

                    targ2values = im2[(target2[1] - int((pixelinch * 0.75) / 2)):(target2[1] + int((pixelinch * 0.75) / 2)),
                                  (target2[0] - int((pixelinch * 0.75) / 2)):(target2[0] + int((pixelinch * 0.75) / 2))]

                    targ3values = im2[(target3[1] - int((pixelinch * 0.75) / 2)):(target3[1] + int((pixelinch * 0.75) / 2)),
                                  (target3[0] - int((pixelinch * 0.75) / 2)):(target3[0] + int((pixelinch * 0.75) / 2))]


                    if (len(im2.shape) > 2) and fil in ["RE", "NIR", "Red"]:
                        t1mean = np.mean(targ1values[:,:,2])
                        t2mean = np.mean(targ2values[:,:,2])
                        t3mean = np.mean(targ3values[:,:,2])

                    elif (len(im2.shape) > 2) and fil in ["Green"]:
                        t1mean = np.mean(targ1values[:,:,1])
                        t2mean = np.mean(targ2values[:,:,1])
                        t3mean = np.mean(targ3values[:,:,1])

                    elif (len(im2.shape) > 2) and fil in ["Blue"]:
                        t1mean = np.mean(targ1values[:,:,0])
                        t2mean = np.mean(targ2values[:,:,0])
                        t3mean = np.mean(targ3values[:,:,0])
                    else:
                        t1mean = np.mean(targ1values)
                        t2mean = np.mean(targ2values)
                        t3mean = np.mean(targ3values)
                    y = [0.87, 0.51, 0.23]
                    x = [t1mean, t2mean, t3mean]


                if (fil == "NIR" and (camera_model in ["Survey2", "Survey3"])):
                    y = self.refvalues[self.ref]["850"][0]

                elif camera_model == "Survey2" and fil == "Red":
                    y = self.refvalues[self.ref]["650"][0]

                elif camera_model == "Survey2" and fil == "Green":
                    y = self.refvalues[self.ref]["550"][1]

                elif camera_model == "Survey2" and fil == "Blue":
                    y = self.refvalues[self.ref]["450"][2]

                elif fil in ['405', '450', '490', '518', '550', '590', '615', '632', '650', '685', '725', '808', '850']:
                    mono_fil = 'Mono' + fil
                    y = self.refvalues[self.ref][mono_fil]

                elif fil == "RE":
                    y = self.refvalues[self.ref]["725"]


                if self.get_filetype(image_path) == "JPG":
                    x = [i / 255 for i in x]

                elif self.get_filetype(image_path) == "TIF":
                    x = [i / 65535 for i in x]

                if self.bad_target_photo([x]):
                    self.CalibrationLog.append("WARNING: Provided calibration target photo is not generating good calibration values. For optimal calibration, please use another calibration target photo or check that white balance and exposure settings are set to defualt values. \n")

                slope, intercept = self.get_LOBF_values(x, y)

                self.multiplication_values["mono"]["slope"] = slope
                self.multiplication_values["mono"]["intercept"] = intercept

                if version == "V2":
                    if len(self.coords) > 0:
                        self.CalibrationLog.append("Found QR Target Model 2, please proceed with calibration.")
                    else:
                        self.CalibrationLog.append("Could not find Calibration Target.")
                else:
                    self.CalibrationLog.append("Found QR Target Model 1, please proceed with calibration.")
                QtWidgets.QApplication.processEvents()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(str(e) + ' Line: ' + str(exc_tb.tb_lineno))
            self.CalibrationLog.append("Error: " + str(e))
            return
            # slope, intcpt, r_value, p_value, std_err = stats.linregress(x, y)
            # self.CalibrationLog.append("Found QR Target, please proceed with calibration.")
            #
            # return [intcpt, slope]
        # Calibration Steps: End

    def output_mono_band_validation(self):
        camera_model = self.PreProcessCameraModel.currentText()
        filt = self.PreProcessFilter.currentText()

        if not ((camera_model in ["Survey2", "Survey3"]) and (filt in ["RE", "NIR", "Red", "Blue", "Green"])):
            self.PreProcessLog.append("WARNING: Outputting mono band for filter {} is not supported for Calibration Tab \n".format(filt))

    @staticmethod
    def get_mapir_files_in_dir(dir_name):
        return glob.glob(dir_name + os.sep + "*.[mM][aA][pP][iI][rR]")

    @staticmethod
    def get_raw_files_in_dir(dir_name):
        return glob.glob(dir_name + os.sep + "*.[rR][aA][wW]")

    @staticmethod
    def get_tiff_files_in_dir(dir_name):
        file_paths = []
        file_paths.extend(glob.glob(dir_name + os.sep + "*.[tT][iI][fF]"))
        file_paths.extend(glob.glob(dir_name + os.sep + "*.[tT][iI][fF][fF]"))
        return file_paths

    @staticmethod
    def get_jpg_files_in_dir(dir_name):
        file_paths = []
        file_paths.extend(glob.glob(dir_name + os.sep + "*.[jJ][pP][gG]"))
        file_paths.extend(glob.glob(dir_name + os.sep + "*.[jJ][pP][eE][gG]"))
        return file_paths

    @staticmethod
    def get_dng_files_in_dir(dir_name):
        return glob.glob(dir_name + os.sep + "*.DNG")

    def get_rgb_clipping_channel_max_mins(self, img, counter):
        is_first_image = counter == 0

        blue = img[:, :, 0]
        green = img[:, :, 1]
        red = img[: ,: , 2]

        if is_first_image:
            self.HC_max["redmax"] = self.get_clipping_value(red)
            self.HC_max["greenmax"] = self.get_clipping_value(green)
            self.HC_max["bluemax"] = self.get_clipping_value(blue)

            print('get_rgb_clipping_channel_max_mins')
            self.min = min(red.min(), green.min(), blue.min())
            self.print_rgb_mins(blue, green, red)
            print(self.min)
        else:
            self.HC_max["redmax"] = max([self.get_clipping_value(red), self.HC_max["redmax"]])
            self.HC_max["greenmax"] = max([self.get_clipping_value(green), self.HC_max["greenmax"]])
            self.HC_max["bluemax"] = max([self.get_clipping_value(blue), self.HC_max["bluemax"]])

            self.min = min(self.min, red.min(), green.min(), blue.min())
            self.print_rgb_mins(blue, green, red)
            print(self.min)

    def delete_all_exiftool_tmp_files_in_dir(self, dir_path):
        for file_name in listdir(dir_path):
            if file_name.endswith('_exiftool_tmp'):
                os.remove(os.path.join(dir_path,file_name))


    def preProcessHelper(self, infolder, outfolder, customerdata=True):
        if self.PreProcessMonoBandBox.isChecked():
            self.output_mono_band_validation()

        self.HC_max = {"redmax": 0.0,
                       "greenmax": 0.0,
                       "bluemax": 0.0, }

        self.HC_mono_max = 0
        self.global_HC_max = 0
        self.min = 0
        self.max = 0

        if self.PreProcessCameraModel.currentText() in self.DJIS:
            os.chdir(infolder)
            infiles = []
            infiles.extend(MAPIR_ProcessingDockWidget.get_dng_files_in_dir('.'))
            infiles.sort()
            counter = 0

            for input in infiles:
                self.append_processing_image_message_to_preprocess_log(counter, infiles)
                QtWidgets.QApplication.processEvents()
                self.openDNG(infolder + input.split('.')[1] + "." + input.split('.')[2], outfolder, customerdata)

                if self.Process_Histogram_ClipBox.isChecked():
                    inphoto = infolder + input.split('.')[1] + "." + input.split('.')[2]
                    newfile = inphoto.split(".")[0] + ".tiff"
                    _, file = os.path.split(newfile)
                    full_path = os.path.join(outfolder, file)

                    img = cv2.imread(full_path, -1)
                    self.get_rgb_clipping_channel_max_mins(img, counter)
                counter += 1

            if self.Process_Histogram_ClipBox.isChecked():
                self.histogram_clip_processed_files(outfolder, infolder)


        elif self.PreProcessCameraModel.currentText() in self.KERNELS:
            os.chdir(infolder)
            infiles = []
            infiles.extend(MAPIR_ProcessingDockWidget.get_mapir_files_in_dir('.'))
            infiles.extend(MAPIR_ProcessingDockWidget.get_tiff_files_in_dir('.'))

            counter = 0
            self.csv_array = []

            # process mapirs
            for input in infiles:
                csv_name = input[3:6]

                self.append_processing_image_message_to_preprocess_log(counter, infiles)
                QtWidgets.QApplication.processEvents()

                file_path = input.split('.')
                file_name = file_path[1]
                file_ext = file_path[2]
                outputfilename = outfolder + file_name + '.tif'
                self.openMapir(infolder + file_name + "." + file_ext,  outputfilename, input, outfolder, counter)
                counter += 1

            self.reprocess_unprocessed_mapirs(outfolder, infolder)

            if self.Process_Histogram_ClipBox.isChecked():
                self.histogram_clip_processed_files(outfolder, infolder)
        else:
            # Preprocess Survey Cameras
            os.chdir(infolder)
            infiles = []
            infiles.extend(MAPIR_ProcessingDockWidget.get_raw_files_in_dir('.'))
            infiles.extend(MAPIR_ProcessingDockWidget.get_jpg_files_in_dir('.'))
            infiles.sort()

            if len(infiles) > 1:
                first_two_files_are_jpg = "JPG" in infiles[0].upper() and "JPG" in infiles[1].upper()
                first_two_files_are_raw_and_jpg = "RAW" in infiles[0].upper() and "JPG" in infiles[1].upper()

                if first_two_files_are_raw_and_jpg or first_two_files_are_jpg:
                    counter = 0

                    if first_two_files_are_raw_and_jpg:
                        files_to_process = infiles[::2]
                    else:
                        files_to_process = infiles

                    for input in files_to_process:
                        oldfirmware = False
                        if customerdata == True:
                                current_image_index = int((counter / 2) + 1) if first_two_files_are_raw_and_jpg else counter + 1
                                total_image_count = len(files_to_process)
                                log_string = "Processing Image: {} of {}  {} \n".format(str(current_image_index), str(total_image_count), input.split(os.sep)[1])
                                self.PreProcessLog.append(log_string)
                                QtWidgets.QApplication.processEvents()
                        if first_two_files_are_raw_and_jpg:
                            if self.PreProcessCameraModel.currentText() == "Survey3":
                                try:
                                    data = np.fromfile(input, dtype=np.uint8)
                                    data = np.unpackbits(data)
                                    datsize = data.shape[0]
                                    data = data.reshape((int(datsize / 4), 4))

                                    temp = copy.deepcopy(data[0::2])
                                    temp2 = copy.deepcopy(data[1::2])
                                    data[0::2] = temp2
                                    data[1::2] = temp

                                    udata = np.packbits(np.concatenate([data[0::3], np.array([0, 0, 0, 0] * 12000000, dtype=np.uint8).reshape(12000000,4),   data[2::3], data[1::3]], axis=1).reshape(192000000, 1)).tobytes()
                                    img = np.fromstring(udata, np.dtype('u2'), (4000 * 3000)).reshape((3000, 4000))

                                except Exception as e:
                                    exc_type, exc_obj, exc_tb = sys.exc_info()
                                    print(str(e) + ' Line: ' + str(exc_tb.tb_lineno))

                                    oldfirmware = True

                            elif self.PreProcessCameraModel.currentText() == "Survey2":
                                with open(input, "rb") as rawimage:
                                    jpg_file = next(x for x in os.listdir(infolder) if "JPG" in x or "jpg" in x)
                                    image_path = infolder + '/' + jpg_file
                                    height, width, _ = cv2.imread(image_path, -1).shape

                                    img = np.fromfile(rawimage, np.dtype('u2'), (width * height)).reshape((height, width))

                            if oldfirmware:
                                with open(input, "rb") as rawimage:
                                    img = np.fromfile(rawimage, np.dtype('u2'), (4000 * 3000))

                                    if img.shape[0] != (4000 * 3000):
                                        raise IndexError("Resolution of the image is {}. MCC only supports processing 12MP resolution. Please reset resolution to default settings.".format(img.shape[0]))

                                    img = img.reshape((3000, 4000))

                            try:
                                color = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2RGB).astype("float32")

                            except Exception as e:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                print(str(e) + ' Line: ' + str(exc_tb.tb_lineno))

                            if self.PreProcessColorBox.isChecked():
                                color = color / 65535.0
                                color = self.color_correction(color)
                                color = color * 65535.0

                            if self.PreProcessJPGBox.isChecked():
                                color = color / 65535.0
                                # color = (color - int(np.percentile(color, 2))) / (int(np.percentile(color, 98)) - int(np.percentile(color, 2)))
                                color = color * 255.0
                                color = color.astype("uint8")
                                filename = input.split('.')
                                outputfilename = filename[1] + '.jpg'
                                cv2.imencode(".jpg", color)

                            elif self.PreProcessDarkBox.isChecked():
                                color = color / 65535.0
                                color = color * 4095.0
                                color = color.astype("uint16")

                                filename = input.split('.')
                                outputfilename = filename[1] + '.tif'
                                cv2.imencode(".tif", color)

                            else:
                                if self.PreProcessColorBox.checkState() == self.UNCHECKED:
                                    color = color * 65535.0

                                color = color.astype("uint16")

                                if not self.PreProcessColorBox.isChecked():
                                    color = cv2.bitwise_not(color)
                                filename = input.split('.')
                                outputfilename = filename[1] + '.tif'
                                cv2.imencode(".tif", color)
                        else:
                            color = cv2.imread(input)
                            filename = input.split('.')
                            outputfilename = filename[1] + '.jpg'
                            cv2.imencode(".jpg", color)

                        if self.Process_Histogram_ClipBox.isChecked():
                            self.get_rgb_clipping_channel_max_mins(color, counter)

                        if self.PreProcessMonoBandBox.isChecked():

                            dropdown_value = self.Band_Dropdown.currentText()
                            band = dropdown_value[dropdown_value.find("(")+1:dropdown_value.find(")")]

                            if first_two_files_are_raw_and_jpg:
                                cutoff = 255.0 if self.PreProcessJPGBox.isChecked() else 65535.0
                            else:
                                cutoff = 255.0

                            if band == "Red":
                                color = color[:,:,2]
                                color[color >= cutoff] = cutoff

                            elif band == "Green":
                                color = color[:,:,1]
                                color[color >= cutoff] = cutoff

                            elif band == "Blue":
                                color = color[:,:,0]
                                color[color >= cutoff] = cutoff

                            if self.Process_Histogram_ClipBox.isChecked():
                                if counter == 0:
                                    self.HC_mono_max = self.get_clipping_value(color)
                                    self.min = color.min()
                                else:
                                    self.HC_mono_max = max([self.get_clipping_value(color), self.HC_mono_max])
                                    self.min = min(color.min(), self.min)

                        cv2.imwrite(outfolder + outputfilename, color)

                        if customerdata == True:
                            file_index = counter + 1 if first_two_files_are_raw_and_jpg else counter
                            self.copyExif(infolder + infiles[file_index], outfolder + outputfilename)
                        if first_two_files_are_jpg:
                            counter += 1
                        else:
                            counter += 2

                    self.delete_all_exiftool_tmp_files_in_dir(outfolder)

                    if self.Process_Histogram_ClipBox.isChecked():
                        files = os.listdir(outfolder)
                        for count, file in enumerate(files):
                            QtWidgets.QApplication.processEvents()
                            output_filepath = os.path.join(outfolder, file)

                            log_string = "Clipping Histogram: {} of {}  {} \n".format((count + 1), len(files), file)
                            self.PreProcessLog.append(log_string)
                            self.preprocess_clip_histogram_survey_cameras(output_filepath)

                else:
                    self.PreProcessLog.append(
                        "Incorrect file structure. Please arrange files in a RAW, JPG, RAW, JPG... format.")

    def histogram_clip_processed_files(self, outfolder, infolder):

        files = os.listdir(outfolder)
        for count, file in enumerate(files):
            QtWidgets.QApplication.processEvents()
            outputfilename = os.path.join(outfolder, file)

            log_string = "Clipping Histogram: {} of {}  {} \n".format((count + 1), len(files), file)
            self.PreProcessLog.append(log_string)
            self.clip_histogram(outputfilename, file, infolder)

    def reprocess_unprocessed_mapirs(self, outfolder, infolder):
        incomplete_files = [file for file in os.listdir(outfolder) if "_TEMP" in file]
        for count, file in enumerate(incomplete_files):
            QtWidgets.QApplication.processEvents()
            mapir_filename = file.rsplit('.', 1)[0].replace("_TEMP", "") + ".mapir"
            output_filename = file.replace("_TEMP", "")

            mapir_filepath = os.path.join(infolder, mapir_filename)
            output_filepath = os.path.join(outfolder, output_filename)

            log_string = "Reprocessing Image: {} of {} {}\n".format(count + 1, len(incomplete_files), mapir_filename)
            self.PreProcessLog.append(log_string)
            self.openMapir(mapir_filepath, output_filepath, mapir_filename, outfolder, 1)

    @staticmethod
    def get_processing_image_message(counter, infiles):
        current_file_path = infiles[counter]
        file_name_with_extension = current_file_path.split(os.sep)[-1]
        file_name = file_name_with_extension.split('.')[0]
        message = "Processing Image: {} of {}  {}\n".format(str((counter) + 1), str(len(infiles)), file_name)
        return message

    def append_processing_image_message_to_preprocess_log(self, counter, infiles):
        message = MAPIR_ProcessingDockWidget.get_processing_image_message(counter, infiles)
        self.PreProcessLog.append(message)


    def traverseHierarchy(self, tier, cont, index, image, depth):

        if tier[0][index][2] != -1:
            self.traverseHierarchy(tier, cont, tier[0][index][2], image, depth + 1)
            return
        elif depth >= 2:
            c = cont[index]
            moment = cv2.moments(c)
            if int(moment['m00']) != 0:
                x = int(moment['m10'] / moment['m00'])
                y = int(moment['m01'] / moment['m00'])
                self.coords.append([x, y])
            return

    def openDNG(self, inphoto, outfolder, customerdata=True):
        inphoto = str(inphoto)
        newfile = inphoto.split(".")[0] + ".tiff"

        if not os.path.exists(outfolder + os.sep + newfile.rsplit(os.sep, 1)[1]):
            if sys.platform == "win32":
                subprocess.call([modpath + os.sep + 'dcraw.exe', '-6', '-T', inphoto], startupinfo=si)
            else:
                subprocess.call([r'/usr/local/bin/dcraw', '-6', '-T', inphoto])
            if customerdata == True:
                self.copyExif(os.path.abspath(inphoto), newfile)

            shutil.move(newfile, outfolder)

        else:
            self.PreProcessLog.append("Attention!: " + str(newfile) + " already exists.")

    def get_dark_frame_value(self, fil_str):
        res = "3.2" if "3.2" in self.PreProcessCameraModel.currentText() else "14.4"
        with open(modpath + os.sep + r'Dark_Frame_Values.json') as json_data:
            DFVS = json.load(json_data)

            if res == "3.2":
                dark_frame_value = DFVS[res][fil_str]
            else:
                dark_frame_value = DFVS[res][self.PreProcessLens.currentText()][fil_str]

        return dark_frame_value

    def color_correction(self, color):
        roff = 0.0
        goff = 0.0
        boff = 0.0

        red_coeffs = self.COLOR_CORRECTION_VECTORS[6:9]
        green_coeffs = self.COLOR_CORRECTION_VECTORS[3:6]
        blue_coeffs = self.COLOR_CORRECTION_VECTORS[:3]

        color[:, :, 2] = (red_coeffs[0] * color[:, :, 0]) + (red_coeffs[1] * color[:, :, 1]) + (red_coeffs[2] * color[:, :, 2]) + roff
        color[:, :, 1] = (green_coeffs[0] * color[:, :, 0]) + (green_coeffs[1] * color[:, :, 1]) + (green_coeffs[2] * color[:, :, 2]) + goff
        color[:, :, 0] = (blue_coeffs[0] * color[:, :, 0]) + (blue_coeffs[1] * color[:, :, 1]) + (blue_coeffs[2] * color[:, :, 2]) + boff

        #need to rescale not clip
        color[color > 1.0] = 1.0
        color[color < 0.0] = 0.0

        return color

    def apply_vignette_dark_color(self, color, h, w):
        red = color[:, :, 2]
        green = color[:, :, 1]
        blue = color[:, :, 0]

        lens_str = self.PreProcessLens.currentText().split("m")[0]
        fil_str = self.PreProcessFilter.currentText()

        # if "/" in self.PreProcessFilter.currentText():
        #     fil_names = self.PreProcessFilter.currentText().split("/")
        #     fil_str = fil_names[0] + "-" + fil_names[1] + "-" + fil_names[2]

        dark_frame_value = self.get_dark_frame_value(fil_str)

        with open(modpath + os.sep + r"vig_" + fil_str + "_" + lens_str + "_" + "1" + r".txt", "rb") as vigfilered:
            v_array = np.ndarray((h, w), np.dtype("float32"), np.fromfile(vigfilered, np.dtype("float32")))
            red -= dark_frame_value
            red = red / v_array
            red[red > 65535.0] = 65535.0
            red[red < 0.0] = 0.0

        with open(modpath + os.sep + r"vig_" + fil_str + "_" + lens_str + "_" + "2" + r".txt", "rb") as vigfilegreen:
            v_array = np.ndarray((h, w), np.dtype("float32"),
                                 np.fromfile(vigfilegreen, np.dtype("float32")))
            green -= dark_frame_value
            green = green / v_array

            green[green > 65535.0] = 65535.0
            green[green < 0.0] = 0.0


        with open(modpath + os.sep + r"vig_" + fil_str + "_" + lens_str + "_" + "3" + r".txt", "rb") as vigfileblue:
            v_array = np.ndarray((h, w), np.dtype("float32"),
                                 np.fromfile(vigfileblue, np.dtype("float32")))
            blue -= dark_frame_value
            blue = blue / v_array

            blue[blue > 65535.0] = 65535.0
            blue[blue < 0.0] = 0.0


        red = red.astype("uint16")
        green = green.astype("uint16")
        blue = blue.astype("uint16")
        color =  cv2.merge((blue, green, red))

        return color


    def get_clipping_value(self, color):
        np.set_printoptions(threshold=np.nan, suppress=True)
        histogram_clip_percentage = float(self.Process_HC_Value.text())/ 100.0
        return int(color.max() * (1.0 - histogram_clip_percentage))
        # unique, counts = np.unique(color, return_counts=True)
        # freq_array = np.asarray((unique, counts)).T

        # total_pixels = color.size

        # num_pixels_greater_than_or_equal_to_unique_pixel_value = 0

        # for unique_pixel_value in freq_array[::-1]:
        #     value = unique_pixel_value[0]
        #     frequency_of_value = unique_pixel_value[1]

        #     num_pixels_greater_than_or_equal_to_unique_pixel_value += frequency_of_value

        #     if (num_pixels_greater_than_or_equal_to_unique_pixel_value / total_pixels) >= histogram_clip_percentage:
        #         return value

    def convert_to_bit_depth_and_merge(self, red, green, blue, filetype):
        if filetype == "TIF":
            red, green, blue, _ = self.convert_normalized_image_to_bit_depth(16, red, green, blue)
            return cv2.merge((blue, green, red))

        elif filetype == "JPG":
            red, green, blue, _ = self.convert_normalized_image_to_bit_depth(8, red, green, blue)
            return cv2.merge((blue, green, red))

    def clip_layer_max(self, layer, limit):
        layer[layer > limit] = limit
        return layer

    def clip_rgb_max(self, red, green, blue, limit):
        red = self.clip_layer_max(red, limit)
        green = self.clip_layer_max(green, limit)
        blue = self.clip_layer_max(blue, limit)
        return red, green, blue

    def clip_layer_min(self, layer, limit):
        layer[layer < limit] = limit
        return layer

    def clip_rgb_min(self, red, green, blue, limit):
        red = self.clip_layer_min(red, limit)
        green = self.clip_layer_min(green, limit)
        blue = self.clip_layer_min(blue, limit)
        return red, green, blue

    def preprocess_clip_histogram_survey_cameras(self, out_path):
        try:
            file_is_jpg = out_path.split('.')[-1].upper() in ['JPG','JPEG']
            file_is_tif = out_path.split('.')[-1].upper() in ['TIF', 'TIFF']

            if file_is_jpg:
                encoding_ext = '.jpg'
                bit_depth = 8
            elif file_is_tif:
                encoding_ext = '.tif'
                bit_depth = 16

            img = cv2.imread(out_path, -1)

            camera_model = self.PreProcessCameraModel.currentText()
            filt = self.PreProcessFilter.currentText()
            lens = self.PreProcessLens.currentText()


            if self.PreProcessMonoBandBox.isChecked():
                img = self.clip_mono_band_image(img, bit_depth)
            else:
                img, red, green, blue = self.clip_rgb_image(img)
                red, green, blue, _ = self.convert_normalized_image_to_bit_depth(bit_depth, red, green, blue)
                img = cv2.merge((blue, green, red))

            cv2.imencode(encoding_ext, img)
            self.imwrite_with_exif(img, out_path)

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(str(e) + ' Line: ' + str(exc_tb.tb_lineno))

    def imwrite_with_exif(self, img, out_path):
        exif_temp_path = out_path.split('.')[0] + r"_TEMP." + out_path.split('.')[1]

        cv2.imwrite(exif_temp_path, img)
        self.copyExif(out_path, exif_temp_path)

        cv2.imwrite(out_path, img)
        self.copy_exif_from_temp_and_delete_temp(out_path)

    def copy_exif_from_temp_mapir_and_delete_temp(self, target_path):
        temp_exif_path = target_path.split('.')[0] + r"_TEMP." + target_path.split('.')[1]
        self.copyMAPIR(temp_exif_path, target_path)
        os.unlink(temp_exif_path)

    def copy_exif_from_temp_and_delete_temp(self, target_path):
        temp_exif_path = target_path.split('.')[0] + r"_TEMP." + target_path.split('.')[1]
        self.copyExif(temp_exif_path, target_path)
        os.unlink(temp_exif_path)

    def clip_normalized_layer_min_max(self, layer):
        layer = self.clip_layer_min(layer, 0.0)
        layer = self.clip_layer_max(layer, 1.0)
        return layer

    def clip_normalized_rgb_min_max(self, red, green, blue):
        red, green, blue = self.clip_rgb_min(red, green, blue, 0.0)
        red, green, blue = self.clip_rgb_max(red, green, blue, 1.0)
        return red, green, blue

    def clip_mono_band_image(self, img, bit_depth):
        img = self.clip_layer_max(img, self.HC_mono_max)
        img = normalize(img, self.HC_mono_max, self.min)
        img = self.clip_normalized_layer_min_max(img)
        img = MAPIR_ProcessingDockWidget.convert_normalized_layer_to_bit_depth(img, bit_depth)
        return img

    def print_rgb_mins(self, blue, green, red):
        redmin = red.min()
        greenmin = green.min()
        bluemin = blue.min()

        print ('redmin: ' + str(redmin))
        print ('greenmin: ' + str(greenmin))
        print ('bluemin: ' + str(bluemin))

    def clip_rgb_image(self, img):
        # cv2.imencode('.tif', img)
        # cv2.imwrite(img, 'test.tif')
        # cv2.imshow(img)
        # self.imwrite_with_exif(img, out_path)
        blue = img[:, :, 0]
        green = img[:, :, 1]
        red = img[:, :, 2]

        self.global_HC_max = max(self.HC_max["redmax"], self.HC_max["bluemax"], self.HC_max["greenmax"])
        print('before')
        self.print_rgb_mins(blue, green, red)
        print('clip_rgb_max')
        red, green, blue = self.clip_rgb_max(red, green, blue, self.global_HC_max)

        self.print_rgb_mins(blue, green, red)
        print('normalize_rgb')
        red, green, blue = normalize_rgb(red, green, blue, self.global_HC_max, self.min)

        self.print_rgb_mins(blue, green, red)
        print('clip_normalized_rgb_min_max')
        red, green, blue = self.clip_normalized_rgb_min_max(red, green, blue)

        self.print_rgb_mins(blue, green, red)



        return img, red, green, blue

    def clip_histogram(self, outphoto, file = None, infolder = None):
        try:
            img = cv2.imread(outphoto, -1)

            camera_model = self.PreProcessCameraModel.currentText()
            filt = self.PreProcessFilter.currentText()
            lens = self.PreProcessLens.currentText()

            if camera_model == "Kernel 14.4":
                filename = file.split(".")[0]
                mapir_file = filename + ".mapir"
                mapir_file_path = os.path.join(infolder, mapir_file)

                cv2.imwrite(outphoto.split('.')[0] + r"_TEMP." + outphoto.split('.')[1], img)
                self.copySimple(outphoto, outphoto.split('.')[0] + r"_TEMP." + outphoto.split('.')[1])

                self.conv = Converter()
                darkscale_true = self.PreProcessDarkBox.isChecked()
                _, _, _, self.lensvals = self.conv.openRaw(mapir_file_path, outphoto, darkscale=darkscale_true)



            if self.PreProcessMonoBandBox.isChecked():
                bit_depth = 16
                img = self.clip_mono_band_image(img, bit_depth)

            else:
                img, red, green, blue = self.clip_rgb_image(img)

            if camera_model == "Kernel 14.4":

                if self.PreProcessJPGBox.isChecked():
                    bit_depth = 8
                    encode_ext = '.jpg'
                else:
                    bit_depth = 16
                    encode_ext = '.tif'

                red, green, blue, _ = self.convert_normalized_image_to_bit_depth(bit_depth, red, green, blue)
                img = cv2.merge((blue, green, red))
                cv2.imencode(encode_ext, img)

                cv2.imwrite(outphoto, img)
                self.copy_exif_from_temp_mapir_and_delete_temp(outphoto)

            elif camera_model == "Survey3":
                # TODO
                if self.PreProcessJPGBox.isChecked():
                    bit_depth = 8
                    encode_ext = '.jpg'
                else:
                    bit_depth = 16
                    encode_ext = '.tif'

                red, green, blue, _ = self.convert_normalized_image_to_bit_depth(bit_depth, red, green, blue)
                color = cv2.merge((blue, green, red))
                cv2.imencode(encode_ext, color)
                self.imwrite_with_exif(color, outphoto)

            elif camera_model in self.DJIS:
                bit_depth = 16

                red, green, blue, _ = self.convert_normalized_image_to_bit_depth(bit_depth, red, green, blue)
                img = cv2.merge((blue, green, red))
                self.imwrite_with_exif(color, outphoto)

            elif camera_model == "Kernel 3.2":
                cv2.imwrite(outphoto, img)
                self.copyMAPIR(outphoto, outphoto)

        except Exception as e:
            exc_type, exc_obj,exc_tb = sys.exc_info()
            print(str(e) + ' Line: ' + str(exc_tb.tb_lineno))

    def on_Process_Histogram_ClipBox_toggled(self):
        if self.Process_Histogram_ClipBox.checkState() == 2:
            self.Process_Histogram_ClipBox_Label.setEnabled(True)
            self.Process_HC_Value.setEnabled(True)

        elif self.Process_Histogram_ClipBox.checkState() == 0:
            self.Process_Histogram_ClipBox_Label.setEnabled(False)
            self.Process_HC_Value.setEnabled(False)
            self.Process_HC_Value.clear()

    def on_PreProcessColorBox_toggled(self):
        if self.PreProcessCameraModel.currentText() == "Kernel 14.4" and self.PreProcessFilter.currentText() == "644 (RGB)":
            if self.PreProcessColorBox.isChecked():
                self.PreProcessVignette.setChecked(True)

    def bad_process_hcp_value(self):
        # if "." in self.Process_HC_Value.text():
        #     return True
        if self.Process_Histogram_ClipBox.checkState() and not self.Process_HC_Value.text():
            return True
        elif (self.Process_Histogram_ClipBox.checkState() and (float(self.Process_HC_Value.text()) < 0.0 or float(self.Process_HC_Value.text()) > 100.0)):
            return True
        else:
            return False

    def unsharp_mask(self, image, kernel_size=(3, 3), sigma=1.0, amount=1.0, threshold=0):
        """Return a sharpened version of the image, using an unsharp mask."""
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)
        sharpened = float(amount + 1) * image - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 65535 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint16)
        if threshold > 0:
            low_contrast_mask = np.absolute(image - blurred) < threshold
            np.copyto(sharpened, image, where=low_contrast_mask)
        return sharpened

    def blur(self, color):
        blue = color[:, :, 0]
        green = color[:, :, 1]
        red = color[:, :, 2]

        BF = 0.2 # Blur Factor
        DF = (8 * BF) + 1
        blur_kernel = np.array([[BF,BF,BF],[BF,1,BF],[BF,BF,BF]])/ DF
        green = cv2.filter2D(green, -1, blur_kernel)
        color =  cv2.merge((blue, green, red))

        return color

    def rotate_image(self, h, w, color):
        M = cv2.getRotationMatrix2D((w/2,h/2), 180, 1)
        color = cv2.warpAffine(color, M, (w,h))
        return color

    def check_if_rotate(self, link_id, array_type):
        return (
            (array_type in [2, 6] and link_id == 0) or
            (array_type == 4 and link_id == 1) or
            (array_type in [8, 100] and link_id in [1, 3]) or
            (array_type == 10 and link_id in [0, 2]) or
            (array_type in [12, 16, 29] and link_id in [1, 3, 5]) or
            (array_type == 14 and link_id in [0, 2, 4])
        )

    def remove_lines(self, img, h, w):
        diff_perc = .50
        bad_rows = []

        for row in range(h):
            cols_start = list(range(0, 0 + (5 * 9), 5))
            cols_end = list(range(w - (5 * 9), w, 5))
            cols = cols_start + cols_end

            front = True
            count = 0

            for col in cols:
                if row == 0 or row == 1:
                    pixel_above = 0
                    pixel_below = img.item(row+2)

                elif row == (h-1) or row == (h-2):
                    pixel_above = img.item(row-2)
                    pixel_below = 0

                else:
                    pixel_below = img.item(row+2, col)
                    pixel_above = img.item(row-2, col)

                if (pixel_above / img.item(row, col)) < diff_perc and (pixel_below / img.item(row, col)) < diff_perc:
                    count += 1

                    if count == 3:
                        bad_rows.append(row)

                        if front and cols.index(col) > 2:
                            cols = list(reversed(cols))
                            front = False
                        else:
                            continue

        bad_rows = list(set(bad_rows))
        for row in bad_rows:
            for col in range(w):

                if row == 0 or row == 1:
                    f_pixel = img.item(row+2, col)
                    s_pixel = img.item(row+4, col)

                elif row == (h-1) or row == (h-2):
                    f_pixel = img.item(row-2, col)
                    s_pixel = img.item(row-4, col)

                else:
                    f_pixel = img.item(row+2, col)
                    s_pixel = img.item(row-2, col)


                img[row, col] = (f_pixel + s_pixel) / 2

        return img

    def openMapir(self, inphoto, outphoto, input, outfolder, count):
        try:
            camera_model = self.PreProcessCameraModel.currentText()
            filt = self.PreProcessFilter.currentText()
            lens = self.PreProcessLens.currentText()

            if self.Process_Histogram_ClipBox.isChecked():
                if self.bad_process_hcp_value():
                    self.PreProcessLog.append("Attention! Please enter a Histogram Clipping Percentage value from 0 to 100.")
                    self.PreProcessLog.append("For example: for 20%, please enter 20\n")

            if inphoto.endswith('.mapir'):
                self.conv = Converter()
                if self.PreProcessDarkBox.isChecked():
                    _, _, _, self.lensvals = self.conv.openRaw(inphoto, outphoto, darkscale=True)

                else:
                    _, _, _, self.lensvals = self.conv.openRaw(inphoto, outphoto, darkscale=False)

                img = cv2.imread(outphoto, cv2.IMREAD_UNCHANGED)
                ts = self.conv.META_PAYLOAD["GNSS_TIME_SECS"][1]
                ns = self.conv.META_PAYLOAD["GNSS_TIME_NSECS"][1]
                ts = ts + (ns / 1000000000)
                time = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
                self.csv_array.append([input.split("\\")[1], self.conv.META_PAYLOAD["GNSS_HEIGHT_SEA_LEVEL"][1], time])

                try:
                    if self.PreProcessCameraModel.currentText() == "Kernel 14.4":
                        h, w = img.shape[:2]

                        if self.conv.META_PAYLOAD["ARRAY_TYPE"][1] in [100, 101]:
                            img = self.remove_lines(img, h, w)

                        self.PreProcessLog.append("Debayering...")
                        QtWidgets.QApplication.processEvents()
                        cv2.imwrite(outphoto.split('.')[0] + r"_TEMP." + outphoto.split('.')[1], img)
                        self.copySimple(outphoto, outphoto.split('.')[0] + r"_TEMP." + outphoto.split('.')[1])

                        color = cv2.cvtColor(img, cv2.COLOR_BAYER_GB2RGB).astype("float32")
                        color = self.blur(color)
                        # kernel_size=(3,3)
                        # color = self.unsharp_mask(color, (3,3), 1.0, 0.5, 0.0)
                        # image, kernel_size=(3, 3), sigma=1.0, amount=1.0, threshold=0)
                        # cv2.imshow(sharp_test)

                        # cv2.imshow(color)

                        print(self.min)
                        print(self.HC_max)

                        if self.PreProcessVignette.isChecked():
                            color = self.apply_vignette_dark_color(color, h, w)
                        print(self.min)
                        color = color / 65535.0
                        if self.PreProcessColorBox.isChecked():
                            if not self.PreProcessVignette.isChecked():
                                self.PreProcessLog.append("WARNING: For better results you need to apply vignette, dark frame subtraction, and color correction together. \n")

                            color = self.color_correction(color)

                        color = (color * 65535.0).astype("uint16")
                        print(self.min)

                        if self.check_if_rotate(self.conv.STD_PAYLOAD["LINK_ID"], self.conv.META_PAYLOAD["ARRAY_TYPE"][1]):
                            color = cv2.flip(color, -1)

                        if self.Process_Histogram_ClipBox.isChecked():
                            self.get_rgb_clipping_channel_max_mins(color, count)

                        print(self.min)

                        if self.PreProcessJPGBox.isChecked():
                            color = color / 65535.0
                            color = color * 255.0
                            color = color.astype("uint8")

                            filename_arr = os.path.basename(outphoto).split('.')
                            outputfilename = filename_arr[0] + '.jpg'
                            cv2.imencode(".jpg", color)
                            path = os.path.join(os.path.dirname(outphoto), outputfilename)
                            jpg_outphoto = path

                        else:
                            cv2.imencode(".tif", color)
                            path = outphoto.split(".")[0] + "." + outphoto.split(".")[1]

                        if self.PreProcessMonoBandBox.isChecked():
                            dropdown_value = self.Band_Dropdown.currentText()
                            band = dropdown_value[dropdown_value.find("(")+1:dropdown_value.find(")")]
                            cutoff = 255.0 if self.PreProcessJPGBox.isChecked() else 65535.0

                            if band == "Red":
                                color = color[:,:,2]
                                color[color >= cutoff] = color.max()

                            elif band == "Green":
                                color = color[:,:,1]
                                color[color >= cutoff] = color.max()

                            elif band == "Blue":
                                color = color[:,:,0]
                                color[color >= cutoff] = color.max()

                        cv2.imwrite(path, color)

                        if self.PreProcessJPGBox.isChecked():
                            self.copyMAPIR(outphoto.split('.')[0] + r"_TEMP." + outphoto.split('.')[1], jpg_outphoto)
                            os.unlink(outphoto.split('.')[0] + r"_TEMP." + outphoto.split('.')[1])
                            os.unlink(outphoto)

                        else:
                            self.copyMAPIR(outphoto.split('.')[0] + r"_TEMP." + outphoto.split('.')[1], outphoto)
                            os.unlink(outphoto.split('.')[0] + r"_TEMP." + outphoto.split('.')[1])

                        self.PreProcessLog.append("Done Debayering \n")
                        QtWidgets.QApplication.processEvents()

                    else:
                        h, w = img.shape[:2]

                        try:
                            if self.Process_Histogram_ClipBox.isChecked():
                                if count == 0:
                                    self.HC_mono_max = self.get_clipping_value(img)
                                    self.min = img.min()

                                else:
                                    self.HC_mono_max = max([self.get_clipping_value(img), self.HC_mono_max])
                                    self.min = min(img.min(), self.min)


                            if self.PreProcessVignette.isChecked():
                                with open(modpath + os.sep + r'Dark_Frame_Values.json') as json_data:
                                    DFVS = json.load(json_data)
                                    dark_frame_value = DFVS["3.2"][self.PreProcessFilter.currentText()]

                                with open(modpath + os.sep + r"vig_" + str(
                                        self.PreProcessFilter.currentText()) + r".txt", "rb") as vigfile:
                                    # with open(self.VignetteFileSelect.text(), "rb") as vigfile:
                                    v_array = np.ndarray((h, w), np.dtype("float32"),
                                                         np.fromfile(vigfile, np.dtype("float32")))

                                    img = img / v_array

                                    img[img > 65535.0] = 65535.0
                                    img[img < 0.0] = 0.0

                                    img -= dark_frame_value
                                    img = img.astype("uint16")

                            if self.check_if_rotate(self.conv.STD_PAYLOAD["LINK_ID"], self.conv.META_PAYLOAD["ARRAY_TYPE"][1]):
                                img = cv2.flip(img, -1)

                            if self.PreProcessJPGBox.isChecked():
                                img = img / 65535.0
                                img = img * 255.0
                                img = img.astype("uint8")

                                filename_arr = os.path.basename(outphoto).split('.')
                                outputfilename = filename_arr[0] + '.jpg'
                                cv2.imencode(".jpg", img)
                                jpg_outphoto = os.path.join(os.path.dirname(outphoto), outputfilename)

                                cv2.imwrite(jpg_outphoto, img)
                                self.copyMAPIR(outphoto, jpg_outphoto)
                                os.unlink(outphoto)

                            else:
                                cv2.imwrite(outphoto, img)
                                self.copyMAPIR(outphoto, outphoto)

                            QtWidgets.QApplication.processEvents()

                        except Exception as e:
                            exc_type, exc_obj,exc_tb = sys.exc_info()
                            self.PreProcessLog.append("No vignette correction data found")
                            QtWidgets.QApplication.processEvents()


                except Exception as e:
                    exc_type, exc_obj,exc_tb = sys.exc_info()
                    print(str(e) + ' Line: ' + str(exc_tb.tb_lineno))
            else:
                try:

                    if self.PreProcessCameraModel.currentText() == "Kernel 14.4":
                        img = cv2.imread(inphoto, 0)
                        h, w = img.shape[:2]

                        color = cv2.cvtColor(img, cv2.COLOR_BAYER_GR2RGB)
                        # color = self.debayer(img)
                        if self.PreProcessVignette.isChecked():
                            red = color[:, :, 0]
                            green = color[:, :, 1]
                            blue = color[:, :, 2]

                            lens_str = self.PreProcessLens.currentText().split("m")[0]
                            fil_str = self.PreProcessFilter.currentText()[:3]

                            # if "/" in self.PreProcessFilter.currentText():
                            #     fil_names = self.PreProcessFilter.currentText().split("/")
                            #     fil_str = fil_names[0] + "-" + fil_names[1] + "-" + fil_names[2]

                            dark_frame_value = self.get_dark_frame_value(fil_str)

                            with open(modpath + os.sep + r"vig_" + fil_str + "_" + lens_str + "_" + "1" + r".txt", "rb") as vigfilered:
                                v_array = np.ndarray((h, w), np.dtype("float32"), np.fromfile(vigfilered, np.dtype("float32")))
                                red = red / v_array
                                red[red > 65535.0] = 65535.0
                                red[red < 0.0] = 0.0
                                red -= dark_frame_value

                            with open(modpath + os.sep + r"vig_" + fil_str + "_" + lens_str + "_" + "2" + r".txt", "rb") as vigfilegreen:
                                v_array = np.ndarray((h, w), np.dtype("float32"),
                                                     np.fromfile(vigfilegreen, np.dtype("float32")))
                                green = green / v_array
                                green[green > 65535.0] = 65535.0
                                green[green < 0.0] = 0.0

                                green -= dark_frame_value

                            with open(modpath + os.sep + r"vig_" + fil_str + "_" + lens_str + "_" + "3" + r".txt", "rb") as vigfileblue:
                                v_array = np.ndarray((h, w), np.dtype("float32"),
                                                     np.fromfile(vigfileblue, np.dtype("float32")))
                                blue = blue / v_array
                                blue[blue > 65535.0] = 65535.0
                                blue[blue < 0.0] = 0.0

                                blue -= dark_frame_value

                            red = red.astype("uint16")
                            green = green.astype("uint16")
                            blue = blue.astype("uint16")

                            color =  cv2.merge((blue, green, red))

                        self.PreProcessLog.append("Debayering...")
                        QtWidgets.QApplication.processEvents()
                        cv2.imencode(".tif", color)
                        cv2.imwrite(outphoto, color)
                        self.copyExif(inphoto, outphoto)
                        self.PreProcessLog.append("Done Debayering \n")
                        QtWidgets.QApplication.processEvents()

                    else:

                        if "mapir" not in inphoto.split('.')[1]:
                            img = cv2.imread(inphoto, -1)
                            h, w = img.shape[:2]

                            try:
                                if self.PreProcessVignette.isChecked():
                                    with open(modpath + os.sep + r'Dark_Frame_Values.json') as json_data:
                                        DFVS = json.load(json_data)
                                        dark_frame_value = DFVS["3.2"][self.PreProcessFilter.currentText()]

                                    with open(modpath + os.sep + r"vig_" + str(
                                            self.PreProcessFilter.currentText()) + r".txt", "rb") as vigfile:
                                        # with open(self.VignetteFileSelect.text(), "rb") as vigfile:
                                        v_array = np.ndarray((h, w), np.dtype("float32"),
                                                             np.fromfile(vigfile, np.dtype("float32")))
                                        img = img / v_array
                                        img[img > 65535.0] = 65535.0
                                        img[img < 0.0] = 0.0
                                        img -= dark_frame_value

                                        img = img.astype("uint16")
                                    cv2.imwrite(outphoto, img)

                                elif self.PreProcessJPGBox.isChecked():
                                    img = img / 255
                                    img = img.astype("uint8")

                                    filename = input.split('.')
                                    outputfilename = filename[1] + '.jpg'
                                    cv2.imencode(".jpg", img)
                                    cv2.imwrite(outfolder + outputfilename, img)

                                    inphoto = outfolder + outputfilename
                                    outphoto = outfolder + outputfilename

                                else:
                                    shutil.copyfile(inphoto, outphoto)

                            except Exception as e:
                                print(e)
                                self.PreProcessLog.append("No vignette correction data found")
                                QtWidgets.QApplication.processEvents()


                            self.copyExif(inphoto, outphoto)
                        else:

                            self.copyExif(outphoto, outphoto)
                        # self.PreP.shaperocessLog.append("Skipped Debayering")
                        QtWidgets.QApplication.processEvents()

                except Exception as e:
                    exc_type, exc_obj,exc_tb = sys.exc_info()
                    print(str(e) + ' Line: ' + str(exc_tb.tb_lineno))
        except Exception as e:
            print("error")
            exc_type, exc_obj,exc_tb = sys.exc_info()
            self.PreProcessLog.append("Error in function openMapir(): " + str(e) + ' Line: ' + str(exc_tb.tb_lineno))
        QtWidgets.QApplication.processEvents()

    def findCameraModel(self, resolution):
        if resolution < 10000000:
            return 'Kernel 3.2MP'
        else:
            return 'Kernel 14.4MP'

    def copyExif(self, inphoto, outphoto):
        subprocess._cleanup()
        if sys.platform == "win32":
            exiftool_exe = modpath + os.sep +r'exiftool.exe'
        else:
            exiftool_exe = r'exiftool'
        try:
            data = subprocess.run(
                args=[exiftool_exe, '-m', r'-UserComment', r'-ifd0:imagewidth', r'-ifd0:imageheight',
                      os.path.abspath(inphoto)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE, startupinfo=si).stdout.decode("utf-8")

            data = [line.strip().split(':') for line in data.split('\r\n') if line.strip()]

            # parse yaw pitch roll from metadata
            ypr = data[0][1].split()
            # ypr = [0.0] * 3

            # ypr[0] = abs(float(ypr[0]) % 360.0) #Yaw
            # ypr[1] = abs((float(ypr[1]) + 180.0) % 360.0) #Pitch
            # ypr[2] = abs((float(-ypr[2])) % 360.0) #Roll


            w = int(data[1][1])
            h = int(data[2][1])
            model = self.findCameraModel(w * h)
            centralwavelength = self.lensvals[3:6][1]
            bandname = self.lensvals[3:6][0]

            fnumber = self.lensvals[0][1]
            focallength = self.lensvals[0][0]
            lensmodel = self.lensvals[0][0] + "mm"

            # centralwavelength = inphoto.split(os.sep)[-1][1:4]
            if '' not in bandname:

                if sys.platform == "win32":
                    exiftool_exe = modpath + os.sep + r'exiftool.exe'
                else:
                    exiftool_exe = r'exiftool'

                exifout = subprocess.run(
                    [ exiftool_exe, r'-config', modpath + os.sep + r'mapir.config', '-m',
                     r'-overwrite_original', r'-tagsFromFile',
                     os.path.abspath(inphoto),
                     r'-all:all<all:all',
                     r'-ifd0:make=MAPIR',
                     r'-Model=' + model,
                     #r'-ifd0:blacklevelrepeatdim=' + str(1) + " " + str(1),
                     #r'-ifd0:blacklevel=0',
                     r'-bandname=' + str(bandname[0] + ', ' + bandname[1] + ', ' + bandname[2]),
                     # r'-bandname2=' + str( r'F' + str(self.BandNames.get(bandname, [0, 0, 0])[1])),
                     # r'-bandname3=' + str( r'F' + str(self.BandNames.get(bandname, [0, 0, 0])[2])),
                     r'-WavelengthFWHM=' + str( self.lensvals[3:6][0][2] + ', ' + self.lensvals[3:6][1][2] + ', ' + self.lensvals[3:6][2][2]) ,
                     r'-ModelType=perspective',
                     r'-Yaw=' + str(ypr[0]),
                     r'-Pitch=' + str(ypr[1]),
                     r'-Roll=' + str(ypr[2]),
                     r'-CentralWavelength=' + str(float(centralwavelength[0])) + ', ' + str(float(centralwavelength[1])) + ', ' + str(float(centralwavelength[2])),
                     r'-Lens=' + lensmodel,
                     r'-FocalLength=' + focallength,
                     r'-fnumber=' + fnumber,
                     r'-FocalPlaneXResolution=' + str(6.14),
                     r'-FocalPlaneYResolution=' + str(4.60),
                     os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                    startupinfo=si).stderr.decode("utf-8")
            else:
                if bandname[0].isdigit():
                    bandname[0] = r'F' + bandname[0]
                if bandname[1].isdigit():
                    bandname[1] = r'F' + bandname[1]
                if bandname[2].isdigit():
                    bandname[2] = r'F' + bandname[2]
                if sys.platform == "win32":
                    exiftool_exe = modpath + os.sep + r'exiftool.exe'
                else:
                    exiftool_exe = r'exiftool'
                exifout = subprocess.run(
                    [ exiftool_exe, r'-config', modpath + os.sep + r'mapir.config', '-m',
                     r'-overwrite_original', r'-tagsFromFile',
                     os.path.abspath(inphoto),
                     r'-all:all<all:all',
                     r'-ifd0:make=MAPIR',
                     r'-Model=' + model,
                     #r'-ifd0:blacklevelrepeatdim=' + str(1) + " " + str(1),
                     #r'-ifd0:blacklevel=0',
                     r'-bandname=' + str( bandname[0]),
                     r'-ModelType=perspective',
                     r'-WavelengthFWHM=' + str(self.lensvals[3:6][0][2]),
                     r'-Yaw=' + str(ypr[0]),
                     r'-Pitch=' + str(ypr[1]),
                     r'-Roll=' + str(ypr[2]),
                     r'-CentralWavelength=' + str(float(centralwavelength[0])),
                     r'-Lens=' + lensmodel,
                     r'-FocalLength=' + focallength,
                     r'-fnumber=' + fnumber,
                     r'-FocalPlaneXResolution=' + str(6.14),
                     r'-FocalPlaneYResolution=' + str(4.60),
                     os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                    startupinfo=si).stderr.decode("utf-8")
        except Exception as e:
            if sys.platform == "win32":
                exiftool_exe = modpath + os.sep + r'exiftool.exe'
            else:
                exiftool_exe = r'exiftool'
            exifout = subprocess.run(
                [ exiftool_exe, #r'-config', modpath + os.sep + r'mapir.config',
                 r'-overwrite_original_in_place', r'-tagsFromFile',
                 os.path.abspath(inphoto),
                 r'-all:all<all:all',
                 os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                startupinfo=si).stderr.decode("utf-8")
            print(exifout)

    def copySimple(self, inphoto, outphoto):
        ExifUtils.copy_simple(inphoto, outphoto, si)

    def copyMAPIR(self, inphoto, outphoto):
        if sys.platform == "win32":
            # with exiftool.ExifTool() as et:
            #     et.execute(r' -overwrite_original -tagsFromFile ' + os.path.abspath(inphoto) + ' ' + os.path.abspath(outphoto))

            try:
                # self.PreProcessLog.append(str(modpath + os.sep + r'exiftool.exe') + ' ' + inphoto + ' ' + outphoto)
                subprocess._cleanup()
                if sys.platform == "win32":
                    exiftool_exe = modpath + os.sep + r'exiftool.exe'
                else:
                    exiftool_exe = r'exiftool'

                data = subprocess.run(
                    args=[ exiftool_exe, '-m', r'-ifd0:imagewidth', r'-ifd0:imageheight', os.path.abspath(inphoto)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE, startupinfo=si).stdout.decode("utf-8")

                data = [line.strip().split(':') for line in data.split('\r\n') if line.strip()]
                #ypr = data[0][1].split()
                #
                ypr = [0.0] * 3

                ypr[0] = float(self.conv.META_PAYLOAD["ATT_Q0"][1])
                ypr[1] = float(self.conv.META_PAYLOAD["ATT_Q1"][1])
                ypr[2] = float(self.conv.META_PAYLOAD["ATT_Q2"][1])

                self.conv.META_PAYLOAD["ARRAY_ID"][1] = self.conv.STD_PAYLOAD["LINK_ID"]
                #ypr = {"yaw": 0, "pitch": 0, "roll": 0}

                if self.conv.META_PAYLOAD["ARRAY_TYPE"][1] != 0:
                    ypr = AdjustYPR(int(self.conv.META_PAYLOAD["ARRAY_TYPE"][1]), int(self.conv.META_PAYLOAD["ARRAY_ID"][1]),ypr)
                    ypr = CurveAdjustment(int(self.conv.META_PAYLOAD["ARRAY_TYPE"][1]), int(self.conv.META_PAYLOAD["ARRAY_ID"][1]),ypr)

                w = int(data[0][1])
                h = int(data[1][1])
                model = self.findCameraModel(w * h)
                centralwavelength = [self.lensvals[3:6][0][1], self.lensvals[3:6][1][1], self.lensvals[3:6][2][1]]
                bandname = [self.lensvals[3:6][0][0], self.lensvals[3:6][1][0], self.lensvals[3:6][2][0]]

                fnumber = self.lensvals[0][1]
                focallength = self.lensvals[0][0]

                lensmodel = self.lensvals[0][0] + "mm"
                pixels_per_unit = "289855/1000" if model == "Kernel 3.2MP" else "714286/1000"

                principal_point = self.PIX4D_VALUES[focallength]["PRINCIPALPOINT"]
                perspective_focal_length = self.PIX4D_VALUES[focallength]["PERSPECTIVEFOCALLENGTH"]
                perspective_distortion = self.PIX4D_VALUES[focallength]["PERSPECTIVEDISTORTION"]

            except Exception as e:
                exc_type, exc_obj,exc_tb = sys.exc_info()
                ypr = None
                print(e)
                print("Line: " + str(exc_tb.tb_lineno))
                print("Warning: No userdefined tags detected")

                # subprocess.call(
                #     [modpath + os.sep + r'exiftool.exe', '-m', r'-overwrite_original', r'-tagsFromFile',
                #      os.path.abspath(inphoto),
                #      # r'-all:all<all:all',
                #      os.path.abspath(outphoto)], startupinfo=si)
            finally:
                if ypr is not None:
                    try:
                        dto = datetime.fromtimestamp(self.conv.META_PAYLOAD["TIME_SECS"][1])
                        m, s = divmod(self.conv.META_PAYLOAD["GNSS_TIME_SECS"][1], 60)
                        h, m = divmod(m, 60)

                        # dd, h = divmod(h, 24)

                        if self.PreProcessVignette.isChecked():
                            fil_str = self.PreProcessFilter.currentText()
                            # if "/" in self.PreProcessFilter.currentText():
                            #     fil_names = self.PreProcessFilter.currentText().split("/")
                            #     fil_str = fil_names[0] + "-" + fil_names[1] + "-" + fil_names[2]
                            DFV = self.get_dark_frame_value(fil_str)
                        else:
                            DFV = None

                        altref = 0 if self.conv.META_PAYLOAD["GNSS_HEIGHT_SEA_LEVEL"][1] >= 0 else 1
                        if '' not in bandname:
                            if sys.platform == "win32":
                                exiftool_exe = modpath + os.sep +  r'exiftool.exe'
                            else:
                                exiftool_exe = r'exiftool'
                            exifout = subprocess.run(
                                [exiftool_exe,  r'-config', modpath + os.sep + r'mapir.config', '-m', r'-overwrite_original', r'-tagsFromFile',
                                 os.path.abspath(inphoto),
                                 r'-all:all<all:all',
                                 r'-ifd0:make=MAPIR',
                                 r'-Model=' + model,
                                 #r'-ifd0:blacklevelrepeatdim=' + str(1) + " " + str(1),
                                 #r'-ifd0:blacklevel=0',
                                 r'-ModelType=perspective',
                                 r'-BlackCurrent=' + str(DFV),
                                 r'-BlackCurrent=' + str(DFV),
                                 r'-BlackCurrent=' + str(DFV),
                                 r'-Yaw=' + str(ypr[0]),
                                 r'-Pitch=' + str(ypr[1]),
                                 r'-Roll=' + str(ypr[2]),
                                 r'-CentralWavelength=' + str(float(centralwavelength[0])), 
                                 r'-CentralWavelength=' + str(float(centralwavelength[1])),
                                 r'-CentralWavelength=' + str(float(centralwavelength[2])),
                                 r'-bandname=' + bandname[0],
                                 r'-bandname=' + bandname[1],
                                 r'-bandname=' + bandname[2],
                                 r'-PrincipalPoint=' + principal_point,
                                 r'-PerspectiveFocalLength=' + perspective_focal_length,
                                 r'-PerspectiveDistortion=' + perspective_distortion,
                                 r'-WavelengthFWHM=' + self.lensvals[3:6][0][2],
                                 r'-WavelengthFWHM=' + self.lensvals[3:6][1][2],
                                 r'-WavelengthFWHM=' + self.lensvals[3:6][2][2],

                                 r'-GPSLatitude="' + str(self.conv.META_PAYLOAD["GNSS_LAT_HI"][1]) + r'"',

                                 r'-GPSLongitude="' + str(self.conv.META_PAYLOAD["GNSS_LON_HI"][1]) + r'"',
                                 r'-GPSTimeStamp="{hour=' + str(h) + r',minute=' + str(m) + r',second=' + str(s) + r'}"',
                                 r'-GPSAltitude=' + str(self.conv.META_PAYLOAD["GNSS_HEIGHT_SEA_LEVEL"][1]),
                                 # r'-GPSAltitudeE=' + str(self.conv.META_PAYLOAD["GNSS_HEIGHT_ELIPSOID"][1]),
                                 r'-GPSAltitudeRef#=' + str(altref),
                                 r'-GPSTimeStampS=' + str(self.conv.META_PAYLOAD["GNSS_TIME_NSECS"][1]),
                                 r'-GPSLatitudeRef=' + self.conv.META_PAYLOAD["GNSS_VELOCITY_N"][1],
                                 r'-GPSLongitudeRef=' + self.conv.META_PAYLOAD["GNSS_VELOCITY_E"][1],
                                 r'-GPSLeapSeconds=' + str(self.conv.META_PAYLOAD["GNSS_LEAP_SECONDS"][1]),
                                 r'-GPSTimeFormat=' + str(self.conv.META_PAYLOAD["GNSS_TIME_FORMAT"][1]),
                                 r'-GPSFixStatus=' + str(self.conv.META_PAYLOAD["GNSS_FIX_STATUS"][1]),
                                 r'-DateTimeOriginal=' + dto.strftime("%Y:%m:%d %H:%M:%S"),
                                 r'-SubSecTimeOriginal=' + str(self.conv.META_PAYLOAD["TIME_NSECS"][1]),
                                 r'-ExposureTime=' + str(self.conv.META_PAYLOAD["EXP_TIME"][1]),
                                 r'-ExposureMode#=' + str(self.conv.META_PAYLOAD["EXP_MODE"][1]),
                                 r'-ISO=' + str(self.conv.META_PAYLOAD["ISO_SPEED"][1]),
                                 r'-Lens=' + lensmodel,
                                 r'-FocalLength=' + focallength,
                                 r'-fnumber=' + fnumber,
                                 r'-ArrayID=' + str(self.conv.META_PAYLOAD["ARRAY_ID"][1]),
                                 r'-ArrayType=' + str(self.conv.META_PAYLOAD["ARRAY_TYPE"][1]), #add rig name and rig index
                                 r'-FocalPlaneXResolution#=' + pixels_per_unit,
                                 r'-FocalPlaneYResolution#=' + pixels_per_unit,
                                 r'-FocalPlaneResolutionUnit#=' + '4',
                                 os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=si).stderr.decode("utf-8")
                        else:

                            bandname = [band for band in bandname if band]
                            CWL = [cwl for cwl in centralwavelength if cwl]

                            if sys.platform == "win32":
                                exiftool_exe = modpath + os.sep + r'exiftool.exe'
                            else:
                                exiftool_exe = r'exiftool'

                            exifout = subprocess.run(
                                [ exiftool_exe , r'-config', modpath + os.sep + r'mapir.config',
                                 '-m', r'-overwrite_original', r'-tagsFromFile',
                                 os.path.abspath(inphoto),
                                 r'-all:all<all:all',
                                 r'-ifd0:make=MAPIR',
                                 r'-Model=' + model,
                                 r'-ModelType=perspective',
                                 r'-BlackCurrent=' + str(DFV),
                                 r'-Yaw=' + str(ypr[0]),
                                 r'-Pitch=' + str(ypr[1]),
                                 r'-Roll=' + str(ypr[2]),
                                 r'-CentralWavelength=' + str(CWL[0] if CWL[0] == "" else float(CWL[0])),
                                 #r'-ifd0:blacklevelrepeatdim=' + str(1) + " " +  str(1),
                                 #r'-ifd0:blacklevel=0',
                                 # r'-BandName="{band1=' + str(self.BandNames[bandname][0]) + r'band2=' + str(self.BandNames[bandname][1]) + r'band3=' + str(self.BandNames[bandname][2]) + r'}"',
                                 r'-bandname=' + bandname[0],
                                 r'-PrincipalPoint=' + principal_point,
                                 r'-PerspectiveFocalLength=' + perspective_focal_length,
                                 r'-PerspectiveDistortion=' + perspective_distortion,
                                 r'-WavelengthFWHM=' + str(self.lensvals[3:6][0][2]),
                                 r'-GPSLatitude="' + str(self.conv.META_PAYLOAD["GNSS_LAT_HI"][1]) + r'"',

                                 r'-GPSLongitude="' + str(self.conv.META_PAYLOAD["GNSS_LON_HI"][1]) + r'"',
                                 r'-GPSTimeStamp="{hour=' + str(h) + r',minute=' + str(m) + r',second=' + str(
                                     s) + r'}"',
                                 r'-GPSAltitude=' + str(self.conv.META_PAYLOAD["GNSS_HEIGHT_SEA_LEVEL"][1]),
                                 # r'-GPSAltitudeE=' + str(self.conv.META_PAYLOAD["GNSS_HEIGHT_ELIPSOID"][1]),
                                 r'-GPSAltitudeRef#=' + str(altref),
                                 r'-GPSTimeStampS=' + str(self.conv.META_PAYLOAD["GNSS_TIME_NSECS"][1]),
                                 r'-GPSLatitudeRef=' + self.conv.META_PAYLOAD["GNSS_VELOCITY_N"][1],
                                 r'-GPSLongitudeRef=' + self.conv.META_PAYLOAD["GNSS_VELOCITY_E"][1],
                                 r'-GPSLeapSeconds=' + str(self.conv.META_PAYLOAD["GNSS_LEAP_SECONDS"][1]),
                                 r'-GPSTimeFormat=' + str(self.conv.META_PAYLOAD["GNSS_TIME_FORMAT"][1]),
                                 r'-GPSFixStatus=' + str(self.conv.META_PAYLOAD["GNSS_FIX_STATUS"][1]),
                                 r'-DateTimeOriginal=' + dto.strftime("%Y:%m:%d %H:%M:%S"),
                                 r'-SubSecTimeOriginal=' + str(self.conv.META_PAYLOAD["TIME_NSECS"][1]),
                                 r'-ExposureTime=' + str(self.conv.META_PAYLOAD["EXP_TIME"][1]),
                                 r'-ExposureMode#=' + str(self.conv.META_PAYLOAD["EXP_MODE"][1]),
                                 r'-ISO=' + str(self.conv.META_PAYLOAD["ISO_SPEED"][1]),
                                 r'-Lens=' + lensmodel,
                                 r'-FocalLength=' + focallength,
                                 r'-fnumber=' + fnumber,
                                 r'-ArrayID=' + str(self.conv.META_PAYLOAD["ARRAY_ID"][1]),
                                 r'-ArrayType=' + str(self.conv.META_PAYLOAD["ARRAY_TYPE"][1]),
                                 r'-FocalPlaneXResolution=' + pixels_per_unit,
                                 r'-FocalPlaneYResolution=' + pixels_per_unit,
                                 r'-FocalPlaneResolutionUnit#=' + '4',
                                 os.path.abspath(outphoto)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE, startupinfo=si).stderr.decode("utf-8")
                        print(exifout)

                    except Exception as e:
                        exc_type, exc_obj,exc_tb = sys.exc_info()
                        if self.MapirTab.currentIndex() == 0:
                            self.PreProcessLog.append("Error: " + str(e) + ' Line: ' + str(exc_tb.tb_lineno))
                        elif self.MapirTab.currentIndex() == 1:
                            self.CalibrationLog.append("Error: " + str(e))
                else:
                    if sys.platform == "win32":
                        exiftool_exe = modpath + os.sep + r'exiftool.exe'
                    else:
                        exiftool_exe = r'exiftool'
                    # self.PreProcessLog.append("No IMU data detected.")
                    subprocess.call(
                        [exiftool_exe, '-m', r'-overwrite_original', r'-tagsFromFile',
                         os.path.abspath(inphoto),
                         # r'-all:all<all:all',
                         os.path.abspath(outphoto)], startupinfo=si)
        else:
            if sys.platform == "win32":
                exiftool_exe = r'exiftool.exe'
            else:
                exiftool_exe = r'exiftool'
            subprocess.call(
                [exiftool_exe, r'-overwrite_original', r'-addTagsFromFile', os.path.abspath(inphoto),
                 # r'-all:all<all:all',
                 os.path.abspath(outphoto)])

    def on_AnalyzeInButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            folder = QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read())
            self.AnalyzeInput.setText(folder)
            self.AnalyzeOutput.setText(folder)
            try:
                folders = glob.glob(self.AnalyzeInput.text() + os.sep + r'*' + os.sep)
                filecount = len(glob.glob(folders[0] + os.sep + r'*'))
                for fold in folders:
                    if filecount == len(glob.glob(fold + os.sep + r'*')):
                        pass
                    else:
                        raise ValueError("Sub-Directories must contain the same number of files.")
            except ValueError as ve:
                print("Error: " + ve)
                return 256
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.AnalyzeInput.text())

    def on_AnalyzeOutButton_released(self):
        self.present_folder_select_dialog(self.AnalyzeOutput)

    def on_AnalyzeButton_released(self):
        self.kcr = KernelConfig.KernelConfig(self.AnalyzeInput.text())
        for file in self.kcr.getItems():
            self.analyze_bands.append(file.split(os.sep)[-2])
        self.BandOrderButton.setEnabled(True)
        self.AlignButton.setEnabled(True)

    def on_PrefixBox_toggled(self):
        if self.PrefixBox.isChecked():
            self.Prefix.setEnabled(True)
        else:
            self.Prefix.setEnabled(False)
    def on_SuffixBox_toggled(self):
        if self.SuffixBox.isChecked():
            self.Suffix.setEnabled(True)
        else:
            self.Suffix.setEnabled(False)
    def on_LightRefBox_toggled(self):
        if self.LightRefBox.isChecked():
            self.LightRef.setEnabled(True)
        else:
            self.LightRef.setEnabled(False)
    def on_AlignmentPercentageBox_toggled(self):
        if self.AlignmentPercentageBox.isChecked():
            self.AlignmentPercentage.setEnabled(True)
        else:
            self.AlignmentPercentage.setEnabled(False)
    def on_BandOrderButton_released(self):
        if self.Bandwindow == None:
            self.Bandwindow = BandOrder(self, self.kcr.getItems())
        self.Bandwindow.resize(385, 205)
        self.Bandwindow.exec_()
        self.kcr.orderRigs(order=self.rdr)
        self.kcr.createCameraRig()
    def on_AlignButton_released(self):
        with open(modpath + os.sep + "instring.txt", "r+") as instring:
            cmralign = [QtWidgets.QFileDialog.getOpenFileName(directory=instring.read())[0],]
            instring.truncate(0)
            instring.seek(0)
            instring.write(cmralign[0])
        if self.PrefixBox.isChecked():
            cmralign.append(r'-prefix')
            cmralign.append(self.Prefix.text())
        if self.SuffixBox.isChecked():
            cmralign.append(r'-suffix')
            cmralign.append(self.Suffix.text())
        if self.NoVignettingBox.isChecked():
            cmralign.append(r'-novignetting')
        if self.NoExposureBalanceBox.isChecked():
            cmralign.append(r'-noexposurebalance')
        if self.NoExposureBalanceBox.isChecked():
            cmralign.append(r'-noexposurebalance')
        if self.ForceAlignmentBox.isChecked():
            cmralign.append(r'-realign')
        if self.SeperateFilesBox.isChecked():
            cmralign.append(r'-separatefiles')
        if self.SeperateFoldersBox.isChecked():
            cmralign.append(r'-separatefolders')
        if self.SeperatePagesBox.isChecked():
            cmralign.append(r'-separatepages')
        if self.LightRefBox.isChecked():
            cmralign.append(r'-variablelightref')
            cmralign.append(self.LightRef.text())
        if self.AlignmentPercentageBox.isChecked():
            cmralign.append(r'-alignframepct')
            cmralign.append(self.AlignmentPercentage.text())
        cmralign.append(r'-i')
        cmralign.append(self.AnalyzeInput.text())
        cmralign.append(r'-o')
        cmralign.append(self.AnalyzeOutput.text())
        cmralign.append(r'-c')
        cmralign.append(self.AnalyzeInput.text() + os.sep + "mapir_kernel.camerarig")
        subprocess.call(cmralign)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
