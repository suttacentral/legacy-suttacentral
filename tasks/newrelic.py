"""New Relic tasks."""

import sc
from sc import config

from tasks.helpers import *


@task
def update_ini(ctx):
    """Update the newrelic.ini file."""
    blurb(update_ini)
    if not config.newrelic_license_key:
        raise Exception('newrelic_license_key must be defined')
    ini_path = sc.base_dir / 'newrelic.ini'
    template_path = sc.base_dir / 'newrelic.ini-template'
    with template_path.open('r', encoding='utf-8') as input:
        with ini_path.open('w+', encoding='utf-8') as output:
            template = input.read()
            ini = template.format(base_dir=sc.base_dir,
                                  license_key=config.newrelic_license_key)
            output.write(ini)
