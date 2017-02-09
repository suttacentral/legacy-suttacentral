"""Logging tasks."""

from tasks.helpers import *


@task
def clean(ctx):
    """Delete log files."""
    blurb(clean)
    rm_rf('log/*.log')
