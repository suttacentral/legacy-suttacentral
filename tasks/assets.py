"""(Compiled CSS/JS) asset tasks."""

import assets

from .helpers import *

@task
@blurb
def clean(older=False):
    """Delete compiled (CSS/JS) assets and cache files."""
    if older:
        assets.clean(older=True)
    else:
        assets.clean

@task(aliases=('build',))
@blurb
def compile():
    """Compile the (CSS/JS) assets."""
    assets.compile()
