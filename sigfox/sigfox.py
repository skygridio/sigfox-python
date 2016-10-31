import serial
import time
import RPi.GPIO as GPIO

'''
SigFox
'''
class SigFox(object):
  # hex instructions
  READ_ID                = chr(0x39)
  CONFIGURE_ID           = chr(0x41)
  SIGFOX_MODE            = chr(0x46)
  MEMORY_CONFIGURATION   = chr(0x4D)
  QUALITY_INDICATOR      = chr(0x51)
  SIGNAL_STRENGTH        = chr(0x53)
  TEMPERATURE_MONITORING = chr(0x55)
  BATTERY_MONITORING     = chr(0x56)
  MEMORY_READ_ONE_BYTE   = chr(0x59)
  SLEEP_MODE             = chr(0x5A)
  LIST_CONFIGURATION     = chr(0x30)
  EXIT_CONFIGURATION     = chr(0xFF)

  EXIT_CONF_MODE         = chr(0x58)
  ENTER_CONF_MODE        = chr(0x00)

  # pins
  PIN_CONFIG = 18  # Avoid hw config mode, use sw (0x00)
  PIN_RESET  = 23


  def __init__(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(self.PIN_CONFIG, GPIO.OUT)
    GPIO.output(self.PIN_CONFIG, True)

    GPIO.setup(self.PIN_RESET, GPIO.OUT)
    GPIO.output(self.PIN_RESET, True)

    self._reset()

    self._connected = False


  def connect(self):
    self.ser = serial.Serial(port='/dev/ttyS0', baudrate=19200, timeout=10)
    self._connected = True


  def disconnect(self):
    self.ser.close()
    self._connected = False



  '''
  READ CONFIG PARAMS
  '''

  def print_config(self):
    self._cmd(self.LIST_CONFIGURATION, config_mode=True)


  def read_id(self):
    self._cmd(self.READ_ID, config_mode=True)


  def read_quality(self):
    self._cmd(self.QUALITY_INDICATOR, config_mode=True)


  def read_signal_strength(self):
    self._cmd(self.SIGNAL_STRENGTH, config_mode=True)


  def read_temperature(self):
    self._cmd(self.TEMPERATURE_MONITORING, config_mode=True)


  def read_memory(self, address):
    if address < 0x00 or address > 0x7F:
      raise Exception('Address out of range (0x00 - 0x7F') 

    self._cmd(self.MEMORY_READ_ONE_BYTE, config_mode=True)
    self._cmd(address)


  '''
  SET CONFIG PARAMS
  '''
  def set_sigfox_mode(self, mode):
    pass


  def set_config(self, param, value):
    pass


  def send(self, payload):
    if self._config_mode:
      self._config_mode = False

    self._reset()

    payload_length = chr(len(payload))
    self._cmd(payload_length)

    for p in payload:
      self._cmd(chr(p))


  def _reset(self):
    GPIO.output(self.PIN_RESET, False)
    time.sleep(0.1)
    GPIO.output(self.PIN_RESET, True)

    self._config_mode = True


  def _cmd(self, cmd, wait=0.5, force=False, config_mode=False):
    if not self._connected:
      self.connect()

    if config_mode and not self._config_mode:
      self._write(self.ENTER_CONF_MODE)
      self._config_mode = True

    elif not config_mode and self._config_mode:
      self._write(self.EXIT_CONF_MODE)
      self._config_mode = False

    self._write(cmd, wait, force)


  def _write(self, cmd, wait=0.5, force=False):
    self.ser.write(cmd)

    unread_bytes = 0
    result = []

    if force:
      time.sleep(wait)
      unread_bytes = self.ser.inWaiting()

    else:
      attempts = 0

      while attempts < (wait/0.1):
        time.sleep(0.1)
        unread_bytes = self.ser.inWaiting()

        if unread_bytes > 0:
          break

        attempts += 1

    while unread_bytes > 0:
      out = self.ser.read(unread_bytes)

      result.append(out)
      
      unread_bytes = self.ser.inWaiting()

    # TODO should check result for OK, etc
    return result