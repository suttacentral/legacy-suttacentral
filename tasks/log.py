"""Logging tasks."""

from tasks.helpers import *

@task
def clean():
    """Delete log files."""
    rm_rf('log/*.log')
