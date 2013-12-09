"""Dictionary tasks."""

from .helpers import *

@task
@blurb
def build():
    """Create the dictionary SQLite database."""
    run('cd src && python build_dict_db.py')

@task
@blurb
def clean():
    """Delete the dictionary SQLite databases."""
    rm_rf('db/dictionaries.sqlite')
