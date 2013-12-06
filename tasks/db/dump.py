"""Database dump tasks."""

from ..helpers import *

@task
def download():
    """Download the latest MySQL database dump from the production server."""
    run('utility/dbutil.py fetch-db-export', pty=True)

@task(name='import')
def import_():
    """Import the downloaded MySQL database dump into the MySQL database."""
    run('utility/dbutil.py load-db', pty=True)
