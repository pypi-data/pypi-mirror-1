# Please do not change this hardware control module for Quisk.
# This hardware module is for using Quisk with the LP-PAN
# and rig control either to the Elecraft K3 directly, or through
# the fldigi digimode program.   If one route becomes unavailable,
# it will try the other.
#
# To use this hardware module, specify it in quisk_conf.py.
# import quisk.quisk_hardware_lppan as quisk_hardware
# See quisk_hardware_model.py for documantation.

from quisk.quisk_hardware_model import Hardware as BaseHardware

import quisk_hardware_fldigi
import quisk_hardware_k3
import time

class Hardware(BaseHardware):
  def __init__(self, app, conf):
    BaseHardware.__init__(self, app, conf)
    self.rig = None
    self.lastRigFailure = None
    self.fldigi = quisk_hardware_fldigi.Hardware(app, conf)
    self.k3 = quisk_hardware_k3.Hardware(app, conf)

  def open(self):
    while self.rig == None:
      print "Waiting for rig control"
      if self.lastRigFailure != self.k3 and self.use_k3():
        return
      if self.lastRigFailure != self.fldigi and self.use_fldigi():
        return
      self.lastRigFailure = None
      time.sleep(1)
    
  def switchRig(self):
    self.lastRigFailure = self.rig
    self.close()
    self.open()

  def use_fldigi(self):
    try:
      self.close()
      self.fldigi.open()
      self.fldigi.GetVFO()
      self.rig = self.fldigi
      print "Using K3 through fldigi"
      return True
    except:
      return False

  def use_k3(self):
    try:
      self.close()
      self.k3.open()
      self.rig = self.k3
      print "Using K3 Directly"
      return True
    except:
      return False

  def close(self):
    if self.rig != None:
      self.rig.close()
    self.rig = None

  def ChangeFrequency(self, tune, vfo, source='', band='', event=None):
    while True:
      try:
        return self.rig.ChangeFrequency(tune, vfo, source, band, event)
      except:
        self.switchRig()

  def ReturnFrequency(self):
    while True:
      try:
        return self.rig.ReturnFrequency()
      except:
        self.switchRig()

  def GetVFO(self):
    while True:
      try:
        return self.rig.GetVFO()
      except:
        self.switchRig()

  def ChangeMode(self, mode):
    while True:
      try:
        return self.rig.ChangeMode(mode)
      except:
        self.switchRig()

  def ChangeBand(self, band):
    while True:
      try:
        return self.rig.ChangeBand(band)
      except:
        self.switchRig()

  def HeartBeat(self):
    # optimize this call out since neither the K3 nor fldigi want it.
    pass
