#!/usr/bin/env python

"""Create newrelic.ini from configuration"""

import env
from sc import config

if __name__ == '__main__':

    if not config.newrelic_license_key:
        raise Exception('newrelic_license_key must be defined')

    newrelic_ini_path = config.base_dir / 'newrelic.ini'
    newrelic_ini_template_path = config.base_dir / 'newrelic.ini-template'

    with newrelic_ini_template_path.open('r', encoding='utf-8') as input:
        with newrelic_ini_path.open('w+', encoding='utf-8') as output:
            template = input.read()
            ini = template.format(base_dir=config.base_dir,
                license_key=config.newrelic_license_key)
            output.write(ini)
