""" Module responsible for periodic updating """

import time
import threading
import logging
logger = logging.getLogger(__name__)

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
    functions = [
        ('sc.textdata.periodic_update', sc.textdata.periodic_update),
        ('sc.scimm.periodic_update', sc.scimm.periodic_update),
        ('sc.search.dicts.periodic_update', sc.search.dicts.periodic_update),
        ('sc.search.suttas.periodic_update', sc.search.suttas.periodic_update),
        ('sc.search.texts.periodic_update', sc.search.texts.periodic_update)
    ]
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
            for fn_name, fn in functions:
                if i > 0:
                    time.sleep(1)
                try:
                    fn(i)
                except Exception as e:
                    logger.error('An exception occured when running {}'.format(fn_name))
                    raise
        time.sleep(sc.config.db_refresh_interval)
        i += 1

updater = threading.Thread(target=run_updaters, daemon=True)
updater.start()
