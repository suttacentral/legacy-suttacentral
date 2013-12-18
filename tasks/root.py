"""Common tasks."""

import os

import config
import tasks
from .helpers import *

@task
def clean(aggressive=False):
    """Remove unnecessary files."""
    tasks.log.clean()
    tasks.tmp.clean()
    if aggressive:
        tasks.assets.clean(older=False)
        tasks.dictionary.clean()
        tasks.exports.offline.clean(older=False)
        tasks.search.clean()
    else:
        tasks.assets.clean(older=True)
        tasks.exports.offline.clean(older=True)

@task('newrelic.update_ini')
def daemonize():
    """Run the *HARDCORE* server."""
    blurb(daemonize)
    os.chdir(str(config.source_dir))
    os.environ['NEW_RELIC_CONFIG_FILE'] = str(config.base_dir / 'newrelic.ini')
    os.execlp('newrelic-admin', 'newrelic-admin', 'run-program', 'cherryd', '-i', 'server')

@task
def reset():
    """Reset the environment."""
    blurb(reset)
    clean(aggressive=True)
    update_data()
    tasks.dictionary.build()
    tasks.search.index()

@task
def update_data():
    """Update the data repository."""
    blurb(update_data)
    with local.cwd(config.data_dir):
        run('git pull')

@task
def server():
    """Run the local development server."""
    blurb(server)
    os.chdir(str(config.source_dir))
    os.execlp('python', 'python', 'server.py')
