"""New Relic tasks."""

from tasks.helpers import *

@task
def update_ini():
    """Update the newrelic.ini file."""
    blurb(update_ini)
    run('utility/create_newrelic_ini.py')
