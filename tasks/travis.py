"""Tasks to run in the Travis CI environment."""

import os
import time

import config
import tasks.db
from .helpers import *

TRAVIS_LOCAL_CONF = """\
[global]
    engine.autoreload.on: False
[mysql]
    user: 'travis'
    password: ''
    db: 'suttacentral'
"""

@task
def prepare():
    """Prepare the travis environment."""
    blurb(prepare)
    with open('local.conf', 'w', encoding='utf-8') as f:
        f.write(TRAVIS_LOCAL_CONF)
    # Make sure we reload config after config gets updated...
    config.reload()
    run('mysql -e "CREATE DATABASE suttacentral;"')
    tasks.db.reset()

@task
def start_server():
    """Start a background server for the travis environment."""
    blurb(start_server)
    run('cd src && python server.py &', fg=True)
    # Give time to server to warm up.
    time.sleep(10)
    notice('Awoken after for 10 seconds...')

@task
def stop_server():
    """Stop the background server for the travis environment."""
    blurb(stop_server)
    run('pkill -f server.py')
