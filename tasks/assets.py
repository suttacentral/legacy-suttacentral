"""(Compiled CSS/JS) asset tasks."""

from .helpers import *

@task
def clean(older=False):
    """Remove compiled and temporary assets."""
    if older:
        run_sc('assets.clean(older=True)')
    else:
        run_sc('assets.clean()')

@task(aliases=('build',))
def compile():
    """Compile the assets."""
    run_sc('assets.compile()')
