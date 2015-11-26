#!/usr/bin/env python

class PV(object):
    def __init__(self, pvname, value=0.0):
        self._pvname = pvname
        self._value = value
        self._callback = None

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
