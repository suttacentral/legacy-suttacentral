""" Module responsible for updating search """

import time
import sched
import logging
logger = logging.getLogger(__name__)


import sc
import sc.scm
import sc.search.indexer
import sc.search.dicts
import sc.search.texts
import sc.search.suttas
import sc.search.discourse
import sc.search.autocomplete

scheduler = sched.scheduler()

localdata_functions = [
    ('sc.search.dicts.periodic_update', sc.search.dicts.periodic_update),
    ('sc.search.suttas.periodic_update', sc.search.suttas.periodic_update),
    ('sc.search.texts.periodic_update', sc.search.texts.periodic_update),
    ('sc.search.autocomplete.periodic_update', sc.search.autocomplete.periodic_update)
]

times_called = {t[0]:0 for t in localdata_functions}

last_git_commit_time = None

def run_periodic():
    global last_git_commit_time
    skip = False
    # We can bypass performing updates if we know that
    # the git repository has not changed, but we should
    # only do this if it is guaranteed that changes have
    # come through git, otherwise never skip.
    if sc.config.updated_through_git_only:
        git_commit_time = sc.scm.scm.last_commit_time
        skip = gitCommitTime == last_git_commit_time
        last_git_commit_time = git_commit_time
            
    if not skip:
        for fn_name, fn in localdata_functions:
            try:
                fn(times_called[fn_name])
                times_called[fn_name] += 1
            except Exception as e:
                logger.exception('An exception occured when running {}'.format(fn_name))
                
            time.sleep(1)
    scheduler.enter(sc.config.db_refresh_interval, action=run_periodic, priority=2)

def run_discourse():
    sc.search.discourse.update()
    scheduler.enter(sc.config.discourse['sync_period'], action=run_discourse, priority=1)

def start():
    """ Start the scheduler and block """
    scheduler.enter(0, action=run_discourse, priority=1)
    scheduler.enter(1, action=run_periodic, priority=2)
    scheduler.run(blocking=True)

def start_non_blocking():
    """ Start in a seperate daemon thread then return """
    import threading
    updater_thread = threading.Thread(target=start, daemon=True)
    updater_thread.start()
    return updater_thread
