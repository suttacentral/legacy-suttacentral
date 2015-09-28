""" Module responsible for updating search """

import time
import threading
import logging
logger = logging.getLogger(__name__)

import sc

import sc.search.discourse

class Updater(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True, name='DiscourseUpdaterThread')
        self.started = False
    
    def run(self):
        self.started = True
        while True:
            time.sleep(sc.config.discourse['sync_period'])
            sc.search.discourse.update()

updater_thread = Updater()

def start():
    if not updater_thread.started:
        updater_thread.start()
