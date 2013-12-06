"""Dictionary tasks."""

from .helpers import *

@task
def build():
    """Create/update the dictionary SQLite database."""
    run('cd src && python build_dict_db.py')

@task
def clean():
    """Delete the search SQLite databases."""
    rm_rf('db/dictionaries.sqlite')
