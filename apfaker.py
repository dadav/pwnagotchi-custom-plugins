import os
import logging

from random import randint, choice, shuffle
from pwnagotchi import plugins
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from pwnagotchi.ui import fonts


class APFaker(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '1.1.4'
    __license__ = 'GPL3'
    __description__ = 'Creates fake aps.'
    __defaults__ = {
        'enabled': False,
        'ssids': ['5G TEST CELL TOWER'],
        'max': 10,
        'repeat': True,
    }

    @staticmethod
    def random_mac():
        return "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(randint(0, 255),
                                                                  randint(0, 255),
                                                                  randint(0, 255),
                                                                  randint(0, 255),
                                                                  randint(0, 255),
                                                                  randint(0, 255))

    def __init__(self):
        self.options = dict()
        self.ready = False

    def on_loaded(self):
        if isinstance(self.options['ssids'], str):
            path = self.options['ssids']
            if not os.path.exists(path):
                self.ssids = [path]
            else:
                try:
                    with open(path) as wordlist:
                        self.ssids = wordlist.read().split()
                except OSError as oserr:
                    logging.error('[apfaker] %s', oserr)
                    return
        elif isinstance(self.options['ssids'], list):
            self.ssids = self.options['ssids']
        else:
            logging.error('[apfaker] wtf is %s', self.options['ssids'])
            return

        self.ready = True
        logging.info('[apfaker] plugin loaded')

    def on_ready(self, agent):
        if not self.ready:
            return

        shuffle(self.ssids)

        cnt = 0
        base_list = self.ssids.copy()
        while len(self.ssids) < self.options['max'] and self.options['repeat']:
            self.ssids.extend([f"{ssid}_{cnt}" for ssid in base_list])
            cnt += 1

        for idx, ssid in enumerate(self.ssids[:self.options['max']]):
            channel = choice([1, 6, 11])
            mac = APFaker.random_mac()
            try:
                logging.info('[apfaker] creating fake ap with ssid "%s" (bssid: %s) on channel %d', ssid, mac, channel)
                agent.run(f"set wifi.ap.ssid {ssid}")
                agent.run(f"set wifi.ap.bssid {mac}")
                agent.run(f"set wifi.ap.channel {channel}")
                agent.run("wifi.ap")
                agent.view().set('apfake', str(idx + 1))
            except Exception as ex:
                logging.debug('[apfaker] %s', ex)

    def on_ui_setup(self, ui):
        with ui._lock:
            ui.add_element('apfake', LabeledValue(color=BLACK, label='F', value='-', position=(ui.width() / 2 + 20, 0),
                           label_font=fonts.Bold, text_font=fonts.Medium))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('apfake')
