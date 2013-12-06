"""Common tasks."""

import os

from .helpers import *

@task
def clean():
    """Remove unnecessary files."""
    rm_rf(
        '__pycache__',
        '**/__pycache__',
        'log/*.log',
        'tmp/*'
    )

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

@task
def test(url=None, phantomjs=False):
    """Run the test suite."""
    command = "python -m unittest discover -s tests -p '*_test.py'"
    if url:
        command = "URL='{}' {}".format(url, command)
    if phantomjs:
        command = "PHANTOMJS=1 {}".format(command)
    run(command)
