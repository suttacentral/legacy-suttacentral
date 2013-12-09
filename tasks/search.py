"""Search tasks."""

import textsearch

from .helpers import *

@task
@blurb
def clean():
    """Delete the search index SQLite databases."""
    rm_rf('db/search_*.sqlite')

@task
@blurb
def index():
    """Create the search index SQLite databases."""
    textsearch.build()
