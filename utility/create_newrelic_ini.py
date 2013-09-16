#!/usr/bin/env python

"""Create newrelic.ini from configuration"""

import env
import config, os.path

if __name__ == '__main__':

    if not config.newrelic_license_key:
        raise Exception('newrelic_license_key must be defined')

    newrelic_ini_path = os.path.join(config.base_dir,
        'newrelic.ini')
    newrelic_ini_template_path = os.path.join(config.base_dir,
        'newrelic.ini-template')

    template = open(newrelic_ini_template_path, 'r').read()
    ini = template.format(base_dir=config.base_dir,
        license_key=config.newrelic_license_key)
    open(newrelic_ini_path, 'w+').write(ini)
