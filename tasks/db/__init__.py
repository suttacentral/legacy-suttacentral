"""Database tasks."""

import sys
from invoke import Collection

import config
from . import dump
from ..helpers import *

@task
@blurb
def clean():
    """Delete the main SQLite database & temporary database files."""
    rm_rf('db/sc.sqlite', 'db/*.sqlite.tmp*')

@task
@blurb
def create():
    """Create the MySQL database."""
    sql = 'CREATE DATABASE {db} CHARACTER SET utf8;'.format(**config.mysql)
    mysql(sql, db=False)

@task(aliases=('destroy',))
@blurb
def drop():
    """Drop the MySQL database."""
    sql = 'DROP DATABASE IF EXISTS {db};'.format(**config.mysql)
    mysql(sql, db=False)

@task
@blurb
def reset():
    """Reset the MySQL database."""
    dump.download()
    drop()
    create()
    dump.import_()

@task
@blurb
def setup():
    """Setup MySQL database authentication."""
    notice('When prompted, enter the MySQL root password.')
    sql = """
        GRANT ALL PRIVILEGES ON {db}.* TO {user}@{host}
            IDENTIFIED BY '{password}';
        FLUSH PRIVILEGES;
    """.format(**config.mysql)
    mysql(sql, root=True, db=False)

ns = Collection.from_module(sys.modules[__name__])
ns.add_collection(dump)
