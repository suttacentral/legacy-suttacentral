"""Common tasks."""

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

@task
def server():
    """Run the local development server."""
    run('cd src && python server.py', pty=True)

@task
def test(url=None, phantomjs=False):
    """Run the test suite."""
    command = "python -m unittest discover -s tests -p '*_test.py'"
    if url:
        command = "URL='{}' {}".format(url, command)
    if phantomjs:
        command = "PHANTOMJS=1 {}".format(command)
    run(command, pty=True)
