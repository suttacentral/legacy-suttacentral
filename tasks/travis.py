import os
import time

from .helpers import *

TRAVIS_LOCAL_CONF = """\
[mysql]
    user: 'travis'
    password: ''
    db: 'suttacentral'
"""

@task
def prepare():
    """Prepare the travis environment."""
    with open('local.conf', 'w', encoding='utf-8') as f:
        f.write(TRAVIS_LOCAL_CONF)
    run('mysql -e "CREATE DATABASE suttacentral;"')
    run('utility/dbutil.py reset-db', pty=True)

@task
def start_server():
    """Start a daemonized server for the travis environment."""
    # run() seems to have problems with background processes.
    command = 'cd src && python server.py &'
    print(command)
    os.system(command)
    # Give time to server to warm up.
    time.sleep(10)

@task
def stop_server():
    """Stop the daemonized server for the travis environment."""
    run('pkill -f server.py')
