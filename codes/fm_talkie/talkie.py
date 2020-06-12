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


    def __init__(self, bus, pin_ptt, freq = FREQ_DEFAULT, sql = 15, check_rssi_interval_ms = 10, *args, **kwargs):
        super().__init__(bus, freq = freq, *args, **kwargs)

        pin_ptt.irq(trigger = machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler = self.ptt_handler)

        self._pin_ptt = pin_ptt
        self.sql = sql
        self._check_rssi_interval_ms = check_rssi_interval_ms
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

        if v1 == v2 and v1 != self._state:
            self._state = v1
            self.set_state(self.state)
            print('[{} mode]'.format(self.state))


    def check_sql(self):
        if self.state == 'Receiver':
            print('[Receiver mode] sql: {} / rssi: {}'.format(self.sql, self.rssi))

            if self.rssi >= self.sql:
                self.set_volume(self._volume)
            else:
                self.write_register(0x05, self._set_element_value(0x05, 0, 4, 0))


    def run(self):
        while True:
            self.check_sql()
            time.sleep(self._check_rssi_interval_ms / 1000)
