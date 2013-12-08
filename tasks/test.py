"""Test tasks."""

from .helpers import *

def prefix(command, url=None, phantomjs=False):
    if url:
        command = 'URL="{}" {}'.format(url, command)
    if phantomjs:
        command = 'PHANTOMJS=1 {}'.format(command)
    return command

@task
def all(url=None, phantomjs=False):
    """Run all tests in the test suite."""
    run(prefix('py.test tests', url=url, phantomjs=phantomjs))

@task
def functional(url=None, phantomjs=False):
    """Run the functional test suite."""
    run(prefix('py.test tests/functional', url=url, phantomjs=phantomjs))

@task
def unit():
    """Run the unit test suite."""
    run('py.test tests/unit')
