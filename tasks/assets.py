"""(Compiled CSS/JS) asset tasks."""

import assets

from .helpers import *

@task
def clean(older=False):
    """Delete compiled (CSS/JS) assets and cache files."""
    blurb(clean)
    if older:
        assets.clean(older=True)
    else:
        assets.clean

@task(aliases=('build',))
def compile():
    """Compile the (CSS/JS) assets."""
    blurb(compile)
    assets.compile()
