"""(Compiled CSS/JS) asset tasks."""

from .helpers import *

@task
def clean(aggressive=False):
    """Remove compiled and temporary assets."""
    if aggressive:
        run_sc('assets.clean(all=True)')
    else:
        run_sc('assets.clean()')

@task(aliases=('build',))
def compile():
    """Compile the assets."""
    run_sc('assets.compile()')
