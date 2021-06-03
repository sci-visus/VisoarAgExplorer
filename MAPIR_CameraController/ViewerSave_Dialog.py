import os
from PyQt5 import QtCore, QtGui, QtWidgets
import PyQt5.uic as uic
import cv2
import numpy as np

from ExifUtils import *


SAVE_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_Viewer_Save.ui'))

class SaveDialog(QtWidgets.QDialog, SAVE_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(SaveDialog, self).__init__(parent=parent)
        self.parent = parent
        self.setupUi(self)

    def on_ViewerSaveFileButton_released(self):
        with open(os.path.dirname(__file__) + os.sep + "instring.txt", "r+") as instring:
            self.ViewerSaveFile.setText(
                QtWidgets.QFileDialog.getExistingDirectory(directory=instring.read())
            )
            instring.truncate(0)
            instring.seek(0)
            instring.write(self.ViewerSaveFile.text())

            self.SaveButton.setStyleSheet("QComboBox {width: 75; height: 23;}")
            self.SaveButton.setEnabled(True)

    def save_lut_or_ndvi_with_metadata(self, in_path, file_to_save, out_path):
        cv2.imwrite(out_path, file_to_save)
        ExifUtils.copy_simple(in_path, out_path)

    def on_SaveButton_released(self):
    # TODO: Save exif metadata when lut and index files are saved
        try:
            in_file_path = self.parent.KernelBrowserFile.text()
            in_filename_arr = in_file_path.split(r'/')[-1].split('.')
            in_filename_base = in_filename_arr[0]
            in_filename_ext = in_filename_arr[1]
            out_path_base = self.ViewerSaveFile.text() + os.sep + in_filename_base

            if self.SaveLutBox.isChecked() and self.parent.LUT_to_save is not None:
                lut_out_path = out_path_base + '_LUT.' + in_filename_ext
                self.save_lut_or_ndvi_with_metadata(in_file_path, self.parent.LUT_to_save, lut_out_path)


            if self.SaveIndexBox.isChecked() and self.parent.index_to_save is not None:
                self.parent.index_to_save = self.parent.index_to_save.astype("float32")
                index_out_path = out_path_base + '_NDVI.' + in_filename_ext
                self.save_lut_or_ndvi_with_metadata(in_file_path, self.parent.index_to_save, index_out_path)
        except Exception as e:
            print(e)
        self.close()

    def on_CancelButton_released(self):
        self.close()
