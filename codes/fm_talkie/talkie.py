try:
    from fm_transceivers.rda58xx.rda5820n_proxy import RDA5820N_proxy, _value_key
except:
    from rda5820n_proxy import RDA5820N_proxy, _value_key

import machine



class Talkie(RDA5820N_proxy):
    FREQ_DEFAULT = 88.8e6
    STATES = {'Transmit': 0,  # transmit mode
              'Receive' : 1,  # receive mode, rssi above threshold.
              # 'Mute'    : 2,  # receive mode, rssi below threshold.
              }
    STATES_value_key = _value_key(STATES)
    WORK_MODES = {'Receive': 'FM_Receiver', 'Transmit': 'FM_Transmitter'}


    def __init__(self, bus, pin_ptt, freq = FREQ_DEFAULT, sql = 7, *args, **kwargs):
        super().__init__(bus, freq = freq, *args, **kwargs)

        self._pin_ptt = pin_ptt
        self._sql = sql
        self._state = None

        pin_ptt.irq(trigger = machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler = self.ptt_handler)


    @property
    def state(self):
        return self._state


    def set_state(self, state):
        self._state = state
        self.set_work_mode(self.WORK_MODES[state])


    def ptt_handler(self, event_source):
        iqr_state = machine.disable_irq()

        machine.delay(100)  # de-bounce
        new_state = self.STATES_value_key[self._pin_ptt.value()]
        if new_state != self._state:  # only if state changed.
            self.set_state(new_state)

        machine.enable_irq(iqr_state)


    def check_sql(self):
        if self._state == 'Receive':
            _ = self.mute(True) if self.rssi < self._sql else self.mute(False)
