"""(Compiled CSS/JS) asset tasks."""

from sc import assets

from tasks.helpers import *


@task
def clean(ctx, older=False):
    """Delete compiled (CSS/JS) assets and cache files."""
    blurb(clean)
    if older:
        assets.clean(older=True)
    else:
        assets.clean


@task(aliases=('build',))
def compile(ctx, precompress=False):
    """Compile the (CSS/JS) assets."""
    blurb(compile)
    assets.compile()
    if precompress:
        assets.compress_static()
