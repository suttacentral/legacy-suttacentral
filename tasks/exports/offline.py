"""Offline SuttaCentral export tasks."""

from ..helpers import *

@task
def clean(aggressive=False):
    """Delete offline SuttaCentral export files."""
    if aggressive:
        rm_rf('static/exports/sc-offline-*')
    else:
        run('find static/exports -type f -mtime +2 -name "sc-offline-*" ' +
            '-exec rm {} \;')

@task
def create(host='localhost:8800', force=False, quiet=False, wait=None):
    """Create an offline SuttaCentral export."""
    command = 'utility/export/offline.py'
    if force:
        command += ' --force'
    if quiet:
        command += ' --quiet'
    if wait:
        command += ' --wait={}'.format(wait)
    command += ' {}'.format(host)
    run(command)

@task
def create_dev():
    """Create an offline SuttaCentral export for a development environment."""
    create(force=True)

@task
def create_production():
    """Create an offline SuttaCentral export for the production environment."""
    create(host='suttacentral.net', quiet=True, wait=0.05)
