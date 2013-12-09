"""Logging tasks."""

from tasks.helpers import *

@task
def clean():
    """Delete log files."""
    blurb(clean)
    rm_rf('log/*.log')
