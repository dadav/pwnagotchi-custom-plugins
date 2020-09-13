import os
import logging

from random import randint, choice, shuffle
from pwnagotchi import plugins


class APFaker(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '0.2.1'
    __license__ = 'GPL3'
    __description__ = 'Creates fake aps.'

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
        if 'ssids' not in self.options or ('ssids' in self.options and self.options['ssids'] is None):
            logging.debug("APfaker: No ssids or wordlist supplied.")
            return

        if 'max' not in self.options or ('max' in self.options and self.options['max'] is None):
            self.max_ap_cnt = 10
        else:
            self.max_ap_cnt = self.options['max']

        if isinstance(self.options['ssids'], str):
            path = self.options['ssids']
            if not os.path.exists(path):
                self.ssids = [path]
            else:
                try:
                    with open(path) as wordlist:
                        self.ssids = wordlist.read().split()
                except OSError as oserr:
                    logging.error(oserr)
                    return
        elif isinstance(self.options['ssids'], list):
            self.ssids = self.options['ssids']
        else:
            logging.error("APFaker: wtf is %s", self.options['ssids'])
            return

        self.ready = True
        logging.info('APFaker loaded')

    def on_ready(self, agent):
        if not self.ready:
            return

        shuffle(self.ssids)

        for ssid in self.ssids[:self.max_ap_cnt]:
            channel = choice([1,6,11])
            mac = APFaker.random_mac()
            try:
                log.info("APFaker: creating fake ap with ssid \"%s\" (bssid: %s) on channel %d", ssid, mac, channel)
                agent.run(f"set wifi.ap.ssid {ssid}")
                agent.run(f"set wifi.ap.bssid {mac}")
                agent.run(f"set wifi.ap.channel {channel}")
                agent.run("wifi.ap")
            except Exception as ex:
                log.debug(ex)

