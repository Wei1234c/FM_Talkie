#  for ESP32 ===========================
import machine
import peripherals
from talkie import Talkie


with_hardware_device = True

if with_hardware_device:
    _i2c = peripherals.I2C.get_uPy_i2c(id = -1, scl_pin_id = 5, sda_pin_id = 4, freq = 400000)
    pin_ptt = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
else:
    _i2c = pin_ptt = None  # using None for testing without actual hardware device.

bus = peripherals.I2C(_i2c)
#  for ESP32 ===========================

ft = Talkie(bus, pin_ptt, freq = 88.8e6, sql = 30, check_rssi_interval_ms = 10)
# ft.run()
