""" Module responsible for periodic updating """

import time
import threading
import logging
logger = logging.getLogger(__name__)

halt = False

def run_updaters():
    """ Run update functions which apply to data such as texts

    Update functions which don't apply to data should not
    be run here

    """
    
    time.sleep(0.5)
    # Import here to delay intialization code.
    import sc
    import sc.scm
    import sc.scimm
    import sc.textdata
    import sc.search.dicts
    import sc.search.texts
    import sc.search.suttas
    import sc.search.autocomplete
    from sc.util import filelock
    # name, function, lock needed?
    functions = [
        ('sc.textdata.periodic_update', sc.textdata.periodic_update, False),
        ('sc.scimm.periodic_update', sc.scimm.periodic_update, False)
    ]
    if sc.config.app['update_search']:
        functions.extend([
            ('sc.search.dicts.periodic_update', sc.search.dicts.periodic_update, True),
            ('sc.search.suttas.periodic_update', sc.search.suttas.periodic_update, True),
            ('sc.search.texts.periodic_update', sc.search.texts.periodic_update, True),
            ('sc.search.autocomplete.periodic_update', sc.search.autocomplete.periodic_update, True)
        ])
    time.sleep(0.5)
    i = 0

    lastGitCommitTime = None
    
    skip = False
    while True:
        
        # We can bypass performing updates if we know that
        # the git repository has not changed, but we should
        # only do this if it is guaranteed that changes have
        # come through git, otherwise never skip.
        if sc.config.updated_through_git_only:
            gitCommitTime = sc.scm.scm.last_commit_time
            skip = gitCommitTime == lastGitCommitTime
            lastGitCommitTime = gitCommitTime
                
        if not skip:
            for fn_name, fn, global_lock in functions:
                if halt:
                    return
                if i > 0:
                    time.sleep(1)
                try:
                    if global_lock:
                        with filelock('/tmp/suttacentral_updater_global.lock', block=False) as acquired:
                            if acquired:
                                fn(i)
                            else:
                                logger.warn('Search index update lock not acquired.')
                                time.sleep(10)
                                continue
                    else:
                        fn(i)
                except Exception as e:
                    logger.error('An exception occured when running {}'.format(fn_name))
                    raise
        time.sleep(sc.config.db_refresh_interval)
        i += 1

updater = threading.Thread(target=run_updaters, daemon=True)
updater.start()
