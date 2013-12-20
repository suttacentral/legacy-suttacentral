"""Dictionary tasks."""

from tasks.helpers import *


@task
def build():
    """Create the dictionary SQLite database."""
    blurb(build)
    run('python sc/build_dict_db.py')


@task
def clean():
    """Delete the dictionary SQLite databases."""
    blurb(clean)
    rm_rf('db/dictionaries.sqlite')
