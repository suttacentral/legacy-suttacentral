"""Database tasks."""

from ..helpers import *

from . import dump

@task
def clean():
    """Delete the main SQLite database & temporary database files."""
    rm_rf('db/sc.sqlite', 'db/*.sqlite.tmp*')

@task
def create():
    """Create the MySQL database."""
    run('utility/dbutil.py create-db', pty=True)

@task(aliases=('destroy',))
def drop():
    """Drop (destroy) the MySQL database."""
    run('utility/dbutil.py drop-db', pty=True)

@task
def reset():
    """Reset the MYSQL database."""
    run('utility/dbutil.py reset-db', pty=True)

@task
def setup():
    """Setup the MySQL database user and authentication."""
    run('utility/dbutil.py create-db-user', pty=True)
    run('utility/dbutil.py setup-db-auth', pty=True)
