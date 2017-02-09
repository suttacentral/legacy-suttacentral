"""Tasks to run in the Travis CI environment."""

import os
import time

import sc
from sc import config

from tasks.helpers import *


TRAVIS_LOCAL_CONF = """\
[global]
    engine.autoreload.on: False
[app]
    compile_assets: True
"""


@task
def prepare(ctx):
    """Prepare the travis environment."""
    blurb(prepare)
    assert not sc.local_config_path.exists()
    with sc.local_config_path.open('w', encoding='utf-8') as f:
        f.write(TRAVIS_LOCAL_CONF)
    # Make sure we reload config after config gets updated...
    config.reload()


@task
def start_server(ctx):
    """Start a background server for the travis environment."""
    blurb(start_server)
    run('invoke server &', fg=True)
    # Give time to server to warm up.
    time.sleep(10)
    notice('Awoken after for 10 seconds...')


@task
def stop_server(ctx):
    """Stop the background server for the travis environment."""
    blurb(stop_server)
    run('pkill -f cherryd')
