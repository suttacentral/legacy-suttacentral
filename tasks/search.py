"""Search tasks."""

import textsearch

from .helpers import *

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
