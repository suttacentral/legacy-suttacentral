"""Tasks to run in the Travis CI environment."""

import os
import time

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
@blurb
def prepare():
    """Prepare the travis environment."""
    with open('local.conf', 'w', encoding='utf-8') as f:
        f.write(TRAVIS_LOCAL_CONF)
    run('mysql -e "CREATE DATABASE suttacentral;"')
    tasks.db.reset()

@task
@blurb
def start_server():
    """Start a background server for the travis environment."""
    run('cd src && python server.py &', fg=True)
    # Give time to server to warm up.
    time.sleep(10)
    notice('Awoken after for 10 seconds...')

@task
@blurb
def stop_server():
    """Stop the background server for the travis environment."""
    run('pkill -f server.py')
