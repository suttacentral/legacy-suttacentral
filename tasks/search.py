"""Search tasks."""

from .helpers import *

@task
def clean():
    """Delete the search index SQLite databases."""
    rm_rf('db/search_*.sqlite')

@task
def index():
    """Create/update the search index SQLite databases."""
    run_sc('textsearch.build()')
