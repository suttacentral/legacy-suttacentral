""" Module responsible for updating search """

import time
import sched
import logging
logger = logging.getLogger(__name__)

import sc

import sc.search.discourse
scheduler = sched.scheduler()

def run_discourse():
    sc.search.discourse.update()
    scheduler.enter(sc.config.discourse['sync_period'], action=run_discourse, priority=1)

def start():
    """ Start the scheduler and block """
    scheduler.enter(0, action=run_discourse, priority=1)
    scheduler.run(blocking=True)

def start_non_blocking():
    """ Start in a seperate daemon thread then return """
    import threading
    updater_thread = threading.Thread(target=start, daemon=True)
    updater_thread.start()
    return updater_thread
