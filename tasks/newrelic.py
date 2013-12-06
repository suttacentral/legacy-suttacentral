"""New Relic tasks."""

from .helpers import *

@task
def update_ini():
    """Create/update the newrelic.ini file."""
    run('utility/create_newrelic_ini.py')
