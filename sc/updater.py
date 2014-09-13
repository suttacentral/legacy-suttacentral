""" Module responsible for periodic updating """

import time
import threading

import sc
import sc.scimm
import sc.search.dicts


def run_updaters():
    print('Running updaters...')    
    time.sleep(0.5)
    while True:
        sc.scimm.perioidc_update()
        sc.search.dicts.periodic_update()
        time.sleep(sc.config.db_refresh_interval)

updater = threading.Thread(target=run_updaters, daemon=True)
updater.start()
