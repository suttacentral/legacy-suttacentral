"""New Relic tasks."""

from .helpers import *

@task
@blurb
def update_ini():
    """Update the newrelic.ini file."""
    run('utility/create_newrelic_ini.py')
