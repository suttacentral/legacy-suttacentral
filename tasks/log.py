"""Logging tasks."""

from tasks.helpers import *

@task
@blurb
def clean():
    """Delete log files."""
    rm_rf('log/*.log')
