"""Database tasks."""

from invoke import Collection

from tasks.helpers import *

@task
def create():
    """Create the database."""
    run('utility/dbutil.py create-db', pty=True)

@task
def drop():
    """Drop the database."""
    run('utility/dbutil.py drop-db', pty=True)

@task
def reset():
    """Reset the database."""
    run('utility/dbutil.py reset-db', pty=True)

@task
def setup():
    """Create the database user and setup database authentication."""
    run('utility/dbutil.py create-db-user', pty=True)
    run('utility/dbutil.py setup-db-auth', pty=True)

ns = Collection(create, drop, reset, setup)

@task(name='download')
def download_dump():
    """Download the latest database dump from the production server."""
    run('utility/dbutil.py fetch-db-export', pty=True)

@task(name='import')
def import_dump():
    """Import the downloaded database dump into the database."""
    run('utility/dbutil.py load-db', pty=True)

ns.add_collection(Collection(download_dump, import_dump), 'dump')
