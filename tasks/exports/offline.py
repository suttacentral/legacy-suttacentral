"""Offline SuttaCentral export tasks."""

from tasks.helpers import *


@task
def clean(older=False):
    """Delete offline SuttaCentral export files."""
    blurb(clean)
    if older:
        run('find static/exports -type f -mtime +2 -name "sc-offline-*" ' +
            '-exec rm {} \;')
    else:
        rm_rf('static/exports/sc-offline-*')


@task
def create(host='localhost:8800', basestem='sc-offline', force=False, quiet=False, wait=None, omit=None):
    """Create an offline SuttaCentral export."""
    blurb(create)
    command = 'utility/export/offline.py'
    if force:
        command += ' --force'
    if quiet:
        command += ' --quiet'
    if wait:
        command += ' --wait={}'.format(wait)
    if omit:
        command += ' --omit={}'.format(omit)
    
    command += ' {} {}'.format(host, basestem)
    run(command)


@task
def create_dev():
    """Create an offline SuttaCentral export for a development environment."""
    create(force=True)


@task
def create_production():
    """Create an offline SuttaCentral export for the production environment."""
    create(host='suttacentral.net', quiet=True, wait=0.15)
    create(host='suttacentral.net', quiet=True, wait=0.15,
        basestem='sc-offline-en', omit='de,es,fr,it,ko,ru,my,vn')
