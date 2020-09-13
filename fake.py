import logging

from random import randint
from pwnagotchi import plugins


class APFaker(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = '0.1.0'
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

    def on_loaded(self):
        logging.info("APFaker loaded")

    def on_ready(self, agent):
        for ssid in self.options['ssids']:
            try:
                agent.run(f"set wifi.ap.ssid {ssid}")
                agent.run(f"set wifi.ap.bssid {APFaker.random_mac()}")
                agent.run("wifi.ap")
            except Exception as ex:
                log.debug(ex)

