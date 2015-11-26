#!/usr/bin/env python
from PyQt4.QtCore import QTimer

class PV(object):
    def __init__(self, pvname, value=0.0, connection_timeout=0.0, connection_callback=None):
        self._pvname = pvname
        self._value = value
        self._callback = None
        self._connection_callback = connection_callback
        QTimer.singleShot(1000, self.run_connection_callback)

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value
        self.run_callback()

    def add_callback(self, fn):
        if self._callback:
            raise Exception('Only one callback supported!')
        self._callback = fn
        return 1

    def remove_callback(self, idx):
        self._callback = None
    
    def run_callback(self, idx=1):
        if not self._callback:
            return
        self._callback(pvname=self._pvname, value=self._value)

    def run_connection_callback(self):
        if not self._connection_callback:
            return
        self._connection_callback(pvname=self._pvname, conn=True)
