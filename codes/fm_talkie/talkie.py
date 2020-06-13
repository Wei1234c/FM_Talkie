try:
    from fm_transceivers.rda58xx.rda5820n_proxy import RDA5820N_proxy, _value_key
except:
    from rda5820n_proxy import RDA5820N_proxy, _value_key

import time

import machine



class Talkie(RDA5820N_proxy):
    FREQ_DEFAULT = 88.8e6
    STATES = {'Transmitter': 0, 'Receiver': 1}
    STATES_value_key = _value_key(STATES)


    def __init__(self, bus, pin_ptt, freq = FREQ_DEFAULT, squelch = 5, check_rssi_interval_ms = 50,
                 input_level_v = 0.6, adc_gain = 7, tx_power_dBm = 3, volume = 1,
                 *args, **kwargs):

        super().__init__(bus, freq = freq,
                         input_level_v = input_level_v,
                         adc_gain = adc_gain,
                         tx_power_dBm = tx_power_dBm,
                         volume = volume,
                         *args, **kwargs)

        pin_ptt.irq(trigger = machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler = self.ptt_handler)

        self._pin_ptt = pin_ptt
        self.squelch = squelch
        self._check_rssi_interval_s = check_rssi_interval_ms / 1000
        self.set_state('Receiver')


    @property
    def state(self):
        return self.STATES_value_key[self._state]


    def set_state(self, state):
        self._state = self.STATES[state]
        self.set_work_mode(state)


    def ptt_handler(self, pin_ptt):
        v1 = pin_ptt.value()
        time.sleep(0.1)  # de-bounce
        v2 = pin_ptt.value()

        if v2 == v1 and v2 != self._state:  # only if state changed
            self._state = v2
            self.set_state(self.state)
            print('[{} mode]'.format(self.state))


    def check_sql(self):
        if self.state == 'Receiver':
            print('[Receiver mode] sql: {} / rssi: {}'.format(self.squelch, self.rssi))

            if self.rssi >= self.squelch:
                self.set_volume(self._volume)
            else:
                self.write_register(0x05, self._set_element_value(0x05, 0, 4, 0))


    def run(self):
        while True:
            self.check_sql()
            time.sleep(self._check_rssi_interval_s)
