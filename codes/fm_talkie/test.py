try:
    from utilities.adapters import peripherals
    from .talkie import Talkie
    import fx2lp


    bus = fx2lp.I2C(as_400KHz = True)
    pin_ptt = fx2lp.GPIO().Pin(id = 1, mode = fx2lp.Pin.IN)

except:

    #  for ESP32 ===========================
    import peripherals
    from .talkie import Talkie


    with_hardware_device = True

    if with_hardware_device:
        _i2c = peripherals.I2C.get_uPy_i2c(id = -1, scl_pin_id = 5, sda_pin_id = 4, freq = 400000)
        pin_ptt = fx2lp.GPIO().Pin(id = 1, mode = fx2lp.Pin.IN)
    else:
        _i2c = pin_ptt = None  # using None for testing without actual hardware device.

    bus = peripherals.I2C(_i2c)
    #  for ESP32 ===========================

fm_talkie = Talkie(bus, pin_ptt, freq = 88.8e6, sql = 7)

while True:
    fm_talkie.check_sql()
