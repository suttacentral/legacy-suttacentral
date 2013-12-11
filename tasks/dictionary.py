"""Dictionary tasks."""

from .helpers import *

@task
def build():
    """Create the dictionary SQLite database."""
    blurb(build)
    run('cd src && python build_dict_db.py')

@task
def clean():
    """Delete the dictionary SQLite databases."""
    blurb(clean)
    rm_rf('db/dictionaries.sqlite')
