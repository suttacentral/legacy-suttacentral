"""Common tasks."""

import os
import os.path

import config
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
@blurb
def daemonize():
    """Run the *HARDCORE* server."""
    os.chdir(config.source_dir)
    os.environ['NEW_RELIC_CONFIG_FILE'] = '{}/newrelic.ini'.format(config.base_dir)
    os.execlp('newrelic-admin', 'newrelic-admin', 'run-program', 'cherryd', '-i', 'server')

@task
@blurb
def server():
    """Run the local development server."""
    os.chdir(config.source_dir)
    os.execlp('python', 'python', 'server.py')
