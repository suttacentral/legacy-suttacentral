"""Database tasks."""

import sys
from invoke import Collection

import config
from . import dump
from ..helpers import *

@task
def clean():
    """Delete the main SQLite database & temporary database files."""
    blurb(clean)
    rm_rf('db/sc.sqlite', 'db/*.sqlite.tmp*')

@task
def create():
    """Create the MySQL database."""
    blurb(create)
    sql = 'CREATE DATABASE {db} CHARACTER SET utf8;'.format(**config.mysql)
    mysql(sql, db=False)

@task(aliases=('destroy',))
def drop():
    """Drop the MySQL database."""
    blurb(drop)
    sql = 'DROP DATABASE IF EXISTS {db};'.format(**config.mysql)
    mysql(sql, db=False)

@task
def reset():
    """Reset the MySQL database."""
    blurb(reset)
    dump.download()
    drop()
    create()
    dump.import_()

@task
def setup():
    """Setup MySQL database authentication."""
    blurb(setup)
    notice('When prompted, enter the MySQL root password.')
    sql = """
        GRANT ALL PRIVILEGES ON {db}.* TO {user}@{host}
            IDENTIFIED BY '{password}';
        FLUSH PRIVILEGES;
    """.format(**config.mysql)
    mysql(sql, root=True, db=False)

ns = Collection.from_module(sys.modules[__name__])
ns.add_collection(dump)
