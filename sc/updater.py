""" Module responsible for periodic updating """

import time
import threading
import logging
logger = logging.getLogger(__name__)

halt = False

def is_interactive():
    import __main__ as main
    #Abort updating in interactive sessions
    return not hasattr(main, '__file__')

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
    import sc.text_image
    from sc.util import filelock
    
    
    # name, function, repeat?
    functions = [
        ('sc.textdata.periodic_update', sc.textdata.periodic_update, False),
        ('sc.scimm.periodic_update', sc.scimm.periodic_update, True),
        ('sc.textdata.periodic_update', sc.textdata.periodic_update, True),
        ('sc.text_image.update_symlinks', sc.text_image.update_symlinks, True)
    ]

    time.sleep(0.5)
    i = 0
    
    times_called = {t[0]:0 for t in functions}

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
            for fn_name, fn, repeat in functions:
                if halt:
                    return
                if not repeat and i > 0:
                    continue
                if i > 0:
                    time.sleep(1)
                try:
                    fn(times_called[fn_name])
                    times_called[fn_name] += 1
                except Exception as e:
                    logger.error('An exception occured when running {}'.format(fn_name))
                    raise
        if is_interactive():
            return            
        
        if i == 0:
            # Perform special first-pass actions
            if sc.config.app['update_search']:
                import sc.search.updater
                sc.search.updater.start_non_blocking()
        
        time.sleep(sc.config.db_refresh_interval)
        i += 1
        
updater = threading.Thread(target=run_updaters, daemon=True)
updater.start()


