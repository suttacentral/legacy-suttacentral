"""Common tasks."""

import os

import tasks
from .helpers import *

@task
def clean(aggressive=False):
    """Remove unnecessary files."""
    tasks.db.dump.clean()
    tasks.log.clean()
    tasks.tmp.clean()
    if aggressive:
        tasks.assets.clean(older=False)
        tasks.db.clean()
        tasks.dictionary.clean()
        tasks.exports.db.clean(older=False)
        tasks.exports.offline.clean(older=False)
        tasks.search.clean()
    else:
        tasks.assets.clean(older=True)
        tasks.exports.db.clean(older=True)
        tasks.exports.offline.clean(older=True)

@task('newrelic.update_ini')
def daemonize():
    """Replace the current process with the server for use as a daemon."""
    os.chdir('src')
    os.environ['NEW_RELIC_CONFIG_FILE'] = '{}/newrelic.ini'.format(root_path)
    os.execlp('newrelic-admin', 'newrelic-admin', 'run-program', 'cherryd', '-i', 'server')

@task
def server():
    """Run the local development server."""
    run('cd src && python server.py')
