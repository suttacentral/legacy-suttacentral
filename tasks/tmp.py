"""Temporary file tasks."""

from .helpers import *

@task
def clean():
    """Delete temporary files."""
    rm_rf(
        '__pycache__',
        '*/__pycache__',
        '*/*/__pycache__',
        'tmp/*'
    )
