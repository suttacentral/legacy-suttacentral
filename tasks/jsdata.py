"""Dictionary tasks."""

from tasks.helpers import *

@task
def build(minify=False, download=False, verbose=False, quiet=False):
    """Build the JavaScript data script files used by zh2en dictionary."""
    blurb(build)
    cmd = 'python utility/dicts/build_lzh2en_data.py'
    if minify:
        cmd += ' --minify'
    if download:
        cmd += ' --download'
    if quiet:
        cmd += ' --quiet'
    if verbose:
        cmd += ' --verbose'
    run(cmd)

