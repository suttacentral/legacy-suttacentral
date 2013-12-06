"""Database dump tasks."""

from ..helpers import *

@task
def clean():
    """Delete the downloaded MySQL database dump."""
    rm_rf('tmp/sc-db-latest.zip')

@task(aliases=('fetch',))
def download():
    """Download the latest MySQL database dump from the production server."""
    run('utility/dbutil.py fetch-db-export')

@task(name='import')
def import_():
    """Import the downloaded MySQL database dump into the MySQL database."""
    run('utility/dbutil.py load-db')
