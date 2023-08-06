# Please do not change this hardware control module for Quisk.
# This hardware module is for using the Elecraft K3 transceiver
# via the k3lib library.  See k3lib, see http://wa5znu.org.
#
# To use this hardware module, specify it in quisk_conf.py.
# import quisk.quisk_hardware_k3 as quisk_hardware
# See quisk_hardware_model.py for documentation.

import k3lib
from quisk.quisk_hardware_model import Hardware as BaseHardware

class Hardware(BaseHardware):
  def __init__(self, app, conf):
    BaseHardware.__init__(self, app, conf)
    self.VFO = 0
  def open(self):
    self.k3 = k3lib.K3()

  def close(self):
    pass

  def ChangeFrequency(self, tune, vfo, source='', band='', event=None):
    # Change and return the tuning and VFO frequency in Hertz.  The VFO frequency is the
    # frequency in the center of the display; that is, the RF frequency corresponding to an
    # audio frequency of zero Hertz.  The tuning frequency is the RF frequency indicated by
    # the tuning line on the display, and is equivalent to the transmit frequency.  The quisk
    # receive frequency is the tuning frequency plus the RIT (receive incremental tuning).
    # If your hardware will not change to the requested frequencies, return different
    # frequencies.
    # The source is a string indicating the source of the change:
    #   BtnBand       A band button
    #   BtnUpDown     The band Up/Down buttons
    #   FreqEntry     The user entered a frequency in the box
    #   MouseBtn1     Left mouse button press
    #   MouseBtn3     Right mouse button press
    #   MouseMotion   The user is dragging with the left button
    #   MouseWheel    The mouse wheel up/down
    # For "BtnBand", the string band is in the band argument.
    # For the mouse events, the Tk event is in the event argument.
    if source=="MouseBtn1" or source=="MouseMotion" or source=="MouseWheel":
      self.tune = tune
      return tune, self.GetVFO()
    elif source=="BtnBand" or source=="BtnUpDown" or source=="FreqEntry":
      self.k3.qsy(float(tune))
      self.tune = tune
      newVFO = self.GetVFO()
      return (newVFO, newVFO)
    elif source=="MouseBtn3":
      self.k3.qsy(float(tune))
      self.tune = tune
      newVFO = self.GetVFO()
      return (newVFO, newVFO)
    else:
      return (tune, self.GetVFO())

  def ReturnFrequency(self):
    # Return the current tuning and VFO frequency.  If neither have changed,
    # you can return (None, None).
    newVFO = self.GetVFO()
    if self.VFO == newVFO:
      return None, None	# frequencies have not changed
    else:
      self.VFO = newVFO
      tune = newVFO
      return tune, self.VFO

  def GetVFO(self):
    return (int(self.k3.qsyq()*1000))+self.GetIFDelta()

  def GetVFO2(self):
    return (int(self.k3.qsyq2()*1000))

  def GetIFDelta(self):
    return int(round((self.k3.fiq()-8215.0)*1000))

  def ChangeMode(self, mode):		# Change the tx/rx mode
    # mode is a string: "USB", "AM", etc.
    pass

  def ChangeBand(self, band):		# Change the band
    # band is a string: "60", "40", "WWV", etc.
    pass

  def HeartBeat(self):	# Called at about 10 Hz by the main
    pass
