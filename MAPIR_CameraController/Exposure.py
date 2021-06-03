import PyQt5.uic as uic
import os
from MAPIR_Enums import *
from PyQt5 import QtCore, QtGui, QtWidgets
A_EXP_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_A_Exposure.ui'))

M_EXP_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'MAPIR_Processing_dockwidget_M_Exposure.ui'))

#Class for handling Manual Exposure Settings
class M_EXP_Control(QtWidgets.QDialog, M_EXP_CLASS):
    parent = None
    _initial_ISO = None
    _initial_Shutter = None
    def __init__(self, parent=None):
        """Constructor."""
        super(M_EXP_Control, self).__init__(parent=parent)
        self.parent = parent

        self.setupUi(self)
        self.KernelShutterSpeed.blockSignals(True)
        self.KernelISO.blockSignals(True)
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_BLOCK_READ_REPORT
        buf[1] = eRegister.RG_CAMERA_SETTING.value
        buf[2] = eRegister.RG_SIZE.value

        res = self.parent.writeToKernel(buf)
        self.parent.regs = res[2:]
        self._initial_Shutter = shutter = self.parent.getRegister(eRegister.RG_SHUTTER.value)
        self.KernelShutterSpeed.setCurrentIndex(shutter - 1)
        self._initial_ISO = iso = self.parent.getRegister(eRegister.RG_ISO.value)
        self.KernelISO.setCurrentIndex(self.KernelISO.findText(str(iso) + "00"))

        self.KernelShutterSpeed.blockSignals(False)
        self.KernelISO.blockSignals(False)

    # def on_KernelShutterSpeed_currentIndexChanged(self):
    #
    #
    # def on_KernelISO_currentIndexChanged(self):

    def on_ModalSaveButton_released(self):
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_SHUTTER.value
        buf[2] = self.KernelShutterSpeed.currentIndex() + 1

        res = self.parent.writeToKernel(buf)

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_ISO.value
        buf[2] = int(int(self.KernelISO.currentText()) / 100)

        res = self.parent.writeToKernel(buf)
        self.close()
    def on_ModalCancelButton_released(self):
        # buf = [0] * 512
        # buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        # buf[1] = eRegister.RG_SHUTTER.value
        # buf[2] = self._initial_Shutter
        # res = self.parent.writeToKernel(buf)
        #
        # buf = [0] * 512
        # buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        # buf[1] = eRegister.RG_ISO.value
        # buf[2] = self._initial_ISO
        #
        # res = self.parent.writeToKernel(buf)
        self.close()
#Class for handling Auto Exposure Settings
class A_EXP_Control(QtWidgets.QDialog, A_EXP_CLASS):
    parent = None
    _initial_Algorithm = None
    _initial_MAX_Shutter = None
    _initial_MIN_Shutter = None
    _initial_MAX_ISO = None
    _initial_FSTOP = None
    _initial_GAIN = None
    _initial_SETPOINT = None
    def __init__(self, parent=None):
        """Constructor."""
        super(A_EXP_Control, self).__init__(parent=parent)
        self.parent = parent
        self.setupUi(self)
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_AE_SELECTION.value
        self._initial_Algorithm = self.parent.writeToKernel(buf)[2]
        self.AutoAlgorithm.setCurrentIndex(self._initial_Algorithm)

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_AE_MAX_SHUTTER.value

        self.AutoMaxShutter.setCurrentIndex(self.parent.writeToKernel(buf)[2])

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_AE_MIN_SHUTTER.value

        self.AutoMinShutter.setCurrentIndex(self.parent.writeToKernel(buf)[2])

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_AE_MAX_GAIN.value

        self.AutoMaxISO.setCurrentIndex(self.parent.writeToKernel(buf)[2])

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_AE_F_STOP.value

        self.AutoFStop.setCurrentIndex(self.parent.writeToKernel(buf)[2])

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_AE_GAIN.value

        self.AutoGain.setCurrentIndex(self.parent.writeToKernel(buf)[2])

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_READ_REPORT
        buf[1] = eRegister.RG_AE_SETPOINT.value

        self.AutoSetpoint.setCurrentIndex(self.parent.writeToKernel(buf)[2])


    def on_ModalSaveButton_released(self):
        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_AE_SELECTION.value
        buf[2] = self.AutoAlgorithm.currentIndex()
        res = self.parent.writeToKernel(buf)

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_AE_MAX_SHUTTER.value
        buf[2] = self.AutoMaxShutter.currentIndex()

        res = self.parent.writeToKernel(buf)

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_AE_MIN_SHUTTER.value
        buf[2] = self.AutoMinShutter.currentIndex()

        res = self.parent.writeToKernel(buf)

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_AE_MAX_GAIN.value
        buf[2] = self.AutoMaxISO.currentIndex()

        res = self.parent.writeToKernel(buf)

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_AE_F_STOP.value
        buf[2] = self.AutoFStop.currentIndex()

        res = self.parent.writeToKernel(buf)

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_AE_GAIN.value
        buf[2] = self.AutoGain.currentIndex()

        res = self.parent.writeToKernel(buf)

        buf = [0] * 512
        buf[0] = self.parent.SET_REGISTER_WRITE_REPORT
        buf[1] = eRegister.RG_AE_SETPOINT.value
        buf[2] = self.AutoSetpoint.currentIndex()

        res = self.parent.writeToKernel(buf)

        self.close()
    def on_ModalCancelButton_released(self):


        self.close()