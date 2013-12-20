"""Search tasks."""

from sc import textsearch

from tasks.helpers import *

@task
def clean():
    """Delete the search index SQLite databases."""
    blurb(clean)
    rm_rf('db/search_*.sqlite')

@task
def index():
    """Create the search index SQLite databases."""
    blurb(index)
    textsearch.build()
