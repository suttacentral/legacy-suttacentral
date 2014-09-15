""" Module responsible for periodic updating """

import time
import threading
import logging
logger = logging.getLogger(__name__)

def run_updaters():
    time.sleep(0.5)
    import sc
    import sc.scimm
    import sc.textdata
    import sc.search.dicts
    functions = [
        ('sc.textdata.periodic_update', sc.textdata.periodic_update),
        ('sc.scimm.periodic_update', sc.scimm.periodic_update),
        ('sc.search.dicts.periodic_update', sc.search.dicts.periodic_update)
    ]
    time.sleep(0.5)
    i = 0
    while True:
        for fn_name, fn in functions:
            if i > 0:
                time.sleep(1)
            try:
                fn(i)
            except Exception as e:
                logger.error('An exception occured when running {}'.format(fn_name))
                logger.error(e)
        time.sleep(sc.config.db_refresh_interval)
        i += 1

updater = threading.Thread(target=run_updaters, daemon=True)
updater.start()
