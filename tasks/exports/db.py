"""SuttaCentral database export tasks."""

from ..helpers import *

@task
def clean(older=False):
    """Delete SuttaCentral database export files."""
    if older:
        run('find static/exports -type f -mtime +2 -name "sc-db-*" ' +
            '-exec rm {} \;')
    else:
        rm_rf('static/exports/sc-db-*')

@task
def create(force=False, quiet=False):
    """Create a SuttaCentral database export."""
    command = 'utility/export/db.py'
    if force:
        command += ' --force'
    if quiet:
        command += ' --quiet'
    run(command)

@task
def create_dev():
    """Create a SuttaCentral database export for a development environment."""
    create(force=True)

@task
def create_production():
    """Create a SuttaCentral database export for the production environment."""
    create(quiet=True)
