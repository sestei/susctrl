#!/usr/bin/env python
import sys
import argparse
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

try:
    from epics import PV
except ImportError:
    print 'Running in demo mode, this is probably not what you want!'
    from dummyepics import PV

class MainWindow(QWidget):
    def __init__(self, options, parent=None):
        super(MainWindow, self).__init__(parent)
        uic.loadUi('pycommander.ui', self)
        if options['suspension']:
            self._suspension = options['suspension']
            self.lblTheSuspension.setText(self._suspension)
        else:
            print 'Please provide a suspension name via the -s/--suspension command line parameter.'
            exit(1)
        if options['demo']:
            self._demo = True
            print 'Running in demo mode.'
        else:
            self._demo = False
        self._yaw = 0
        self._pitch = 0
        self._yawTimer = None
        self._pitchTimer = None
        self.initialise_PVs()

    @property
    def yaw(self):
        return self._yaw
    @yaw.setter
    def yaw(self, value):
        if value < -32767:
            value = -32767
        elif value > 32767:
            value = 32768
        self._yaw = value
        self._PV_yaw.value = int(self._yaw)

    @property
    def pitch(self):
        return self._pitch
    @pitch.setter
    def pitch(self, value):
        if value < -32767:
            value = -32767
        elif value > 32767:
            value = 32768
        self._pitch = value
        self._PV_pitch.value = int(self._pitch)

    def initialise_PVs(self):
        myPV = PV
        if self._demo:
            import dummyepics
            myPV = dummyepics.PV
        self._PV_yaw = myPV(
            'G2:SUS-{0}_YAW_OFFSET'.format(self._suspension),
            connection_timeout=1.0,
            connection_callback=self.on_PV_yaw_connected,
            callback=self.on_PV_yaw_changed
        )
        
        self._PV_pitch = myPV(
            'G2:SUS-{0}_PITCH_OFFSET'.format(self._suspension),
            connection_timeout=1.0,
            connection_callback=self.on_PV_pitch_connected,
            callback=self.on_PV_pitch_changed
        )
        self.lcdPitch.display('---')
        self.lcdYaw.display('---')

    def timerEvent(self, ev):
        if ev.timerId() == self._yawTimer:
            self.yaw += (self.slYaw.value()/1000.0)**3 * 2000
        elif ev.timerId() == self._pitchTimer:
            self.pitch += (self.slPitch.value()/1000.0)**3 * 2000

    def step_size(self, large=False):
        modifiers = QApplication.keyboardModifiers()
        if large or (modifiers & Qt.ShiftModifier):
            return 100
        else:
            return 1

    # ====== PV callbacks ======
    def on_PV_pitch_connected(self, conn, **kw):
        if conn == False:
            return
        self.slPitch.setEnabled(True)
        self.btnPitchInc.setEnabled(True)
        self.btnPitchDec.setEnabled(True)

    def on_PV_yaw_connected(self, conn, **kw):
        if conn == False:
            return
        self.slYaw.setEnabled(True)
        self.btnYawInc.setEnabled(True)
        self.btnYawDec.setEnabled(True)

    def on_PV_pitch_changed(self, value, **kw):
        self.lcdPitch.display(int(value))
    
    def on_PV_yaw_changed(self, value, **kw):
        self.lcdYaw.display(int(value))

    # ====== SLOTS ======
    @pyqtSlot(int)
    def on_slYaw_actionTriggered(self, action):
        if action == QSlider.SliderMove:
            return
        #elif action == QSlider.SliderSingleStepAdd:
        #    self.yaw += self.step_size()
        #elif action == QSlider.SliderSingleStepSub:
        #    self.yaw -= self.step_size()
        #elif action == QSlider.SliderPageStepAdd:
        #    self.yaw += self.step_size()
        #elif action == QSlider.SliderPageStepSub:
        #    self.yaw -= self.step_size()
        self.slYaw.setValue(0)

    @pyqtSlot(int)
    def on_slPitch_actionTriggered(self, action):
        if action == QSlider.SliderMove:
            return
        #elif action == QSlider.SliderSingleStepAdd:
        #    self.pitch += self.step_size()
        #elif action == QSlider.SliderSingleStepSub:
        #    self.pitch -= self.step_size()
        #elif action == QSlider.SliderPageStepAdd:
        #    self.pitch += self.step_size(True)
        #elif action == QSlider.SliderPageStepSub:
        #    self.pitch -= self.step_size(True)
        self.slPitch.setValue(0)

    @pyqtSlot()
    def on_slYaw_sliderPressed(self):
        if not self._yawTimer:
            self._yawTimer = self.startTimer(200)

    @pyqtSlot()
    def on_slYaw_sliderReleased(self):
        self.slYaw.setValue(0)
        self.killTimer(self._yawTimer)
        self._yawTimer = None

    @pyqtSlot()
    def on_slPitch_sliderPressed(self):
        if not self._pitchTimer:
            self._pitchTimer = self.startTimer(200)

    @pyqtSlot()
    def on_slPitch_sliderReleased(self):
        self.slPitch.setValue(0)
        self.killTimer(self._pitchTimer)
        self._pitchTimer = None

    @pyqtSlot()
    def on_btnYawInc_clicked(self):
        self.yaw += self.step_size()

    @pyqtSlot()
    def on_btnYawDec_clicked(self):
        self.yaw -= self.step_size()

    @pyqtSlot()
    def on_btnPitchInc_clicked(self):
        self.pitch += self.step_size()

    @pyqtSlot()
    def on_btnPitchDec_clicked(self):
        self.pitch -= self.step_size()


if __name__ == '__main__':
    qApp = QApplication(sys.argv)

    parser = argparse.ArgumentParser(prog='pycommander.py')
    parser.add_argument('-s', '--suspension', help='display controls for SUSPENSION')
    parser.add_argument('-d', '--demo', help='enter demo mode', action='store_true')
    args = parser.parse_args()
    window = MainWindow(vars(args))
    window.show()
    window.raise_()
    qApp.exec_()
