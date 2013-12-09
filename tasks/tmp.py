"""Temporary file tasks."""

from .helpers import *

@task
@blurb
def clean():
    """Delete Python cache and temporary files."""
    rm_rf(
        '__pycache__',
        '*/__pycache__',
        '*/*/__pycache__',
        'tmp/*'
    )
