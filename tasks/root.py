"""Common tasks."""

import os

import sc
from sc import config

import tasks
from tasks.helpers import *


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


@task
def reset():
    """Reset the environment."""
    blurb(reset)
    clean(aggressive=True)
    update_data()
    tasks.dictionary.build()
    tasks.search.index()


@task
def server():
    """Run the server."""
    blurb(server)
    if config.newrelic_license_key:
        tasks.newrelic.update_ini()
        os.environ['NEW_RELIC_ENVIRONMENT'] = config.newrelic_environment
        os.environ['NEW_RELIC_CONFIG_FILE'] = str(sc.base_dir / 'newrelic.ini')
        os.execlp('newrelic-admin', 'newrelic-admin', 'run-program', 'cherryd',
                  '-i', 'sc.server')
    else:
        os.execlp('cherryd', 'cherryd', '-i', 'sc.server')

@task
def test_server():
    """Run test server to validate code."""
    blurb(test_server)
    os.execlp('cherryd', 'cherryd', '-i', 'sc.test_server')

@task
def update_data():
    """Update the data repository."""
    blurb(update_data)
    with local.cwd(sc.data_dir):
        run('git pull')
